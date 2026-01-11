from __future__ import annotations

from db.connection import get_connection

TIME_OPTIONS = [
    "15min",
    "30",
    "45",
    "1h",
    "1h30",
    "2h",
    "2h30",
    "3h",
    "3h30",
    "4h+",
]

DIFFICULTY_OPTIONS = ["Easy", "Medium", "Hard"]

_TIME_TO_MINUTES = {
    "15min": 15,
    "30": 30,
    "45": 45,
    "1h": 60,
    "1h30": 90,
    "2h": 120,
    "2h30": 150,
    "3h": 180,
    "3h30": 210,
    "4h+": 240,
}

_DIFFICULTY_LOOKUP = {option.lower(): option for option in DIFFICULTY_OPTIONS}


def normalize_time_label(time_label: str | None) -> tuple[str | None, int]:
    if not time_label:
        return None, 0
    cleaned = time_label.strip()
    if cleaned not in _TIME_TO_MINUTES:
        raise ValueError("Invalid recipe time selection.")
    return cleaned, _TIME_TO_MINUTES[cleaned]


def normalize_difficulty(difficulty: str | None) -> str | None:
    if not difficulty:
        return None
    cleaned = difficulty.strip().lower()
    if cleaned not in _DIFFICULTY_LOOKUP:
        raise ValueError("Invalid recipe difficulty selection.")
    return _DIFFICULTY_LOOKUP[cleaned]


def create_recipe(
    name: str,
    instructions: str | None,
    time_label: str | None = None,
    difficulty: str | None = None,
    db_path: str | None = None,
) -> int:
    cleaned_name = name.strip()
    if not cleaned_name:
        raise ValueError("Recipe name cannot be empty.")

    cleaned_instructions = instructions.strip() if instructions else None
    normalized_time_label, total_minutes = normalize_time_label(time_label)
    normalized_difficulty = normalize_difficulty(difficulty)

    with get_connection(db_path) as connection:
        cursor = connection.execute(
            """
            INSERT INTO recipe (name, total_minutes, time_label, difficulty, notes)
            VALUES (?, ?, ?, ?, ?);
            """,
            (
                cleaned_name,
                total_minutes,
                normalized_time_label,
                normalized_difficulty,
                cleaned_instructions,
            ),
        )
        connection.commit()
        return cursor.lastrowid


def list_recipes(
    db_path: str | None = None, season_id: int | None = None
) -> list[dict]:
    with get_connection(db_path) as connection:
        if season_id is None:
            recipes = connection.execute(
                """
                SELECT id,
                       name,
                       time_label,
                       difficulty,
                       notes AS instructions
                FROM recipe
                ORDER BY name ASC;
                """
            ).fetchall()
        else:
            recipes = connection.execute(
                """
                SELECT recipe.id,
                       recipe.name,
                       recipe.time_label,
                       recipe.difficulty,
                       recipe.notes AS instructions
                FROM recipe
                WHERE NOT EXISTS (
                    SELECT 1
                    FROM recipe_ingredient
                    JOIN ingredient ON ingredient.id = recipe_ingredient.ingredient_id
                    WHERE recipe_ingredient.recipe_id = recipe.id
                      AND EXISTS (
                          SELECT 1
                          FROM ingredient_season
                          WHERE ingredient_season.ingredient_id = ingredient.id
                      )
                      AND NOT EXISTS (
                          SELECT 1
                          FROM ingredient_season
                          WHERE ingredient_season.ingredient_id = ingredient.id
                            AND ingredient_season.season_id = ?
                      )
                )
                ORDER BY recipe.name ASC;
                """,
                (season_id,),
            ).fetchall()
    return [dict(recipe) for recipe in recipes]


def get_recipe(recipe_id: int, db_path: str | None = None) -> dict | None:
    with get_connection(db_path) as connection:
        recipe = connection.execute(
            """
            SELECT id,
                   name,
                   time_label,
                   difficulty,
                   notes AS instructions
            FROM recipe
            WHERE id = ?;
            """,
            (recipe_id,),
        ).fetchone()
    return dict(recipe) if recipe else None


def update_recipe(
    recipe_id: int,
    name: str,
    instructions: str | None,
    time_label: str | None = None,
    difficulty: str | None = None,
    db_path: str | None = None,
) -> None:
    cleaned_name = name.strip()
    if not cleaned_name:
        raise ValueError("Recipe name cannot be empty.")

    cleaned_instructions = instructions.strip() if instructions else None
    normalized_time_label, total_minutes = normalize_time_label(time_label)
    normalized_difficulty = normalize_difficulty(difficulty)

    with get_connection(db_path) as connection:
        connection.execute(
            """
            UPDATE recipe
            SET name = ?,
                total_minutes = ?,
                time_label = ?,
                difficulty = ?,
                notes = ?
            WHERE id = ?;
            """,
            (
                cleaned_name,
                total_minutes,
                normalized_time_label,
                normalized_difficulty,
                cleaned_instructions,
                recipe_id,
            ),
        )
        connection.commit()


def delete_recipe(recipe_id: int, db_path: str | None = None) -> None:
    with get_connection(db_path) as connection:
        connection.execute("DELETE FROM recipe WHERE id = ?;", (recipe_id,))
        connection.commit()


def list_recipe_ingredients(
    recipe_id: int, db_path: str | None = None
) -> list[dict]:
    with get_connection(db_path) as connection:
        items = connection.execute(
            """
            SELECT recipe_ingredient.id,
                   recipe_ingredient.quantity,
                   ingredient.name AS ingredient_name,
                   unit.name AS unit_name
            FROM recipe_ingredient
            JOIN ingredient ON ingredient.id = recipe_ingredient.ingredient_id
            JOIN unit ON unit.id = ingredient.unit_id
            WHERE recipe_ingredient.recipe_id = ?
            ORDER BY ingredient.name ASC;
            """,
            (recipe_id,),
        ).fetchall()
    return [dict(item) for item in items]


def get_recipe_ingredient(
    recipe_ingredient_id: int, db_path: str | None = None
) -> dict | None:
    with get_connection(db_path) as connection:
        item = connection.execute(
            """
            SELECT recipe_ingredient.id,
                   recipe_ingredient.quantity,
                   ingredient.name AS ingredient_name
            FROM recipe_ingredient
            JOIN ingredient ON ingredient.id = recipe_ingredient.ingredient_id
            WHERE recipe_ingredient.id = ?;
            """,
            (recipe_ingredient_id,),
        ).fetchone()
    return dict(item) if item else None


def add_recipe_ingredient(
    recipe_id: int, ingredient_id: int, quantity: float, db_path: str | None = None
) -> int:
    with get_connection(db_path) as connection:
        existing = connection.execute(
            """
            SELECT id FROM recipe_ingredient
            WHERE recipe_id = ? AND ingredient_id = ?;
            """,
            (recipe_id, ingredient_id),
        ).fetchone()
        if existing:
            connection.execute(
                """
                UPDATE recipe_ingredient
                SET quantity = ?
                WHERE id = ?;
                """,
                (quantity, existing["id"]),
            )
            connection.commit()
            return existing["id"]

        cursor = connection.execute(
            """
            INSERT INTO recipe_ingredient (recipe_id, ingredient_id, quantity)
            VALUES (?, ?, ?);
            """,
            (recipe_id, ingredient_id, quantity),
        )
        connection.commit()
        return cursor.lastrowid


def update_recipe_ingredient(
    recipe_ingredient_id: int, quantity: float, db_path: str | None = None
) -> None:
    with get_connection(db_path) as connection:
        connection.execute(
            """
            UPDATE recipe_ingredient
            SET quantity = ?
            WHERE id = ?;
            """,
            (quantity, recipe_ingredient_id),
        )
        connection.commit()


def delete_recipe_ingredient(
    recipe_ingredient_id: int, db_path: str | None = None
) -> None:
    with get_connection(db_path) as connection:
        connection.execute(
            "DELETE FROM recipe_ingredient WHERE id = ?;",
            (recipe_ingredient_id,),
        )
        connection.commit()
