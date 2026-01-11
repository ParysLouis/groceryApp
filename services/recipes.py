from __future__ import annotations

from db.connection import get_connection


def create_recipe(name: str, instructions: str | None) -> int:
    cleaned_name = name.strip()
    if not cleaned_name:
        raise ValueError("Recipe name cannot be empty.")

    cleaned_instructions = instructions.strip() if instructions else None

    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO recipe (name, total_minutes, notes)
            VALUES (?, ?, ?);
            """,
            (cleaned_name, 0, cleaned_instructions),
        )
        connection.commit()
        return cursor.lastrowid


def list_recipes() -> list[dict]:
    with get_connection() as connection:
        recipes = connection.execute(
            """
            SELECT id,
                   name,
                   notes AS instructions
            FROM recipe
            ORDER BY name ASC;
            """
        ).fetchall()
    return [dict(recipe) for recipe in recipes]


def get_recipe(recipe_id: int) -> dict | None:
    with get_connection() as connection:
        recipe = connection.execute(
            """
            SELECT id,
                   name,
                   notes AS instructions
            FROM recipe
            WHERE id = ?;
            """,
            (recipe_id,),
        ).fetchone()
    return dict(recipe) if recipe else None


def update_recipe(recipe_id: int, name: str, instructions: str | None) -> None:
    cleaned_name = name.strip()
    if not cleaned_name:
        raise ValueError("Recipe name cannot be empty.")

    cleaned_instructions = instructions.strip() if instructions else None

    with get_connection() as connection:
        connection.execute(
            """
            UPDATE recipe
            SET name = ?, notes = ?
            WHERE id = ?;
            """,
            (cleaned_name, cleaned_instructions, recipe_id),
        )
        connection.commit()


def delete_recipe(recipe_id: int) -> None:
    with get_connection() as connection:
        connection.execute("DELETE FROM recipe WHERE id = ?;", (recipe_id,))
        connection.commit()


def list_recipe_ingredients(recipe_id: int) -> list[dict]:
    with get_connection() as connection:
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


def get_recipe_ingredient(recipe_ingredient_id: int) -> dict | None:
    with get_connection() as connection:
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
    recipe_id: int, ingredient_id: int, quantity: float
) -> int:
    with get_connection() as connection:
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


def update_recipe_ingredient(recipe_ingredient_id: int, quantity: float) -> None:
    with get_connection() as connection:
        connection.execute(
            """
            UPDATE recipe_ingredient
            SET quantity = ?
            WHERE id = ?;
            """,
            (quantity, recipe_ingredient_id),
        )
        connection.commit()


def delete_recipe_ingredient(recipe_ingredient_id: int) -> None:
    with get_connection() as connection:
        connection.execute(
            "DELETE FROM recipe_ingredient WHERE id = ?;",
            (recipe_ingredient_id,),
        )
        connection.commit()
