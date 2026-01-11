from __future__ import annotations

from db.connection import get_connection


def list_recipes():
    with get_connection() as connection:
        return connection.execute(
            """
            SELECT id, name, notes
            FROM recipe
            ORDER BY name ASC;
            """
        ).fetchall()


def create_recipe(
    name: str,
    instructions: str,
    total_minutes: int = 0,
    source_url: str | None = None,
):
    notes = instructions.strip() if instructions.strip() else None
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO recipe (name, total_minutes, source_url, notes)
            VALUES (?, ?, ?, ?);
            """,
            (name.strip(), total_minutes, source_url, notes),
        )
        connection.commit()
