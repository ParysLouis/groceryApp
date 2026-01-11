from __future__ import annotations

from db.connection import get_connection


def list_recipes(db_path: str | None = None):
    with get_connection(db_path) as connection:
        return connection.execute(
            """
            SELECT id, name, total_minutes, source_url, notes
            FROM recipe
            ORDER BY name ASC;
            """
        ).fetchall()


def create_recipe(
    name: str,
    total_minutes: int,
    source_url: str | None = None,
    notes: str | None = None,
    db_path: str | None = None,
) -> None:
    cleaned_name = name.strip()
    if not cleaned_name:
        raise ValueError("Recipe name cannot be empty.")
    with get_connection(db_path) as connection:
        connection.execute(
            """
            INSERT INTO recipe (name, total_minutes, source_url, notes)
            VALUES (?, ?, ?, ?);
            """,
            (cleaned_name, total_minutes, source_url, notes),
        )
        connection.commit()
