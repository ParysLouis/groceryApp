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
