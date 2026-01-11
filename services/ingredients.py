from __future__ import annotations

from typing import Iterable

from db.connection import get_connection


def list_aisles():
    with get_connection() as connection:
        return connection.execute(
            "SELECT id, name, sort_order FROM aisle ORDER BY sort_order ASC;"
        ).fetchall()


def list_units():
    with get_connection() as connection:
        return connection.execute("SELECT id, name FROM unit ORDER BY name ASC;").fetchall()


def list_seasons():
    with get_connection() as connection:
        return connection.execute("SELECT id, name FROM season ORDER BY name ASC;").fetchall()


def list_ingredients():
    with get_connection() as connection:
        return connection.execute(
            """
            SELECT ingredient.id,
                   ingredient.name,
                   aisle.name AS aisle_name,
                   unit.name AS unit_name,
                   GROUP_CONCAT(season.name, ', ') AS seasons
            FROM ingredient
            JOIN aisle ON aisle.id = ingredient.default_aisle_id
            JOIN unit ON unit.id = ingredient.unit_id
            LEFT JOIN ingredient_season ON ingredient_season.ingredient_id = ingredient.id
            LEFT JOIN season ON season.id = ingredient_season.season_id
            GROUP BY ingredient.id
            ORDER BY ingredient.name ASC;
            """
        ).fetchall()


def get_ingredient(ingredient_id: int):
    with get_connection() as connection:
        ingredient = connection.execute(
            """
            SELECT id, name, default_aisle_id, unit_id
            FROM ingredient
            WHERE id = ?;
            """,
            (ingredient_id,),
        ).fetchone()
        seasons = connection.execute(
            "SELECT season_id FROM ingredient_season WHERE ingredient_id = ?;",
            (ingredient_id,),
        ).fetchall()
    season_ids = {row["season_id"] for row in seasons}
    return ingredient, season_ids


def create_ingredient(name: str, aisle_id: int, unit_id: int, season_ids: Iterable[int]):
    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO ingredient (name, default_aisle_id, unit_id)
            VALUES (?, ?, ?);
            """,
            (name.strip(), aisle_id, unit_id),
        )
        ingredient_id = cursor.lastrowid
        _replace_seasons(connection, ingredient_id, season_ids)
        connection.commit()


def update_ingredient(
    ingredient_id: int,
    name: str,
    aisle_id: int,
    unit_id: int,
    season_ids: Iterable[int],
):
    with get_connection() as connection:
        connection.execute(
            """
            UPDATE ingredient
            SET name = ?, default_aisle_id = ?, unit_id = ?
            WHERE id = ?;
            """,
            (name.strip(), aisle_id, unit_id, ingredient_id),
        )
        _replace_seasons(connection, ingredient_id, season_ids)
        connection.commit()


def delete_ingredient(ingredient_id: int):
    with get_connection() as connection:
        connection.execute("DELETE FROM ingredient WHERE id = ?;", (ingredient_id,))
        connection.commit()


def _replace_seasons(connection, ingredient_id: int, season_ids: Iterable[int]):
    connection.execute(
        "DELETE FROM ingredient_season WHERE ingredient_id = ?;", (ingredient_id,)
    )
    connection.executemany(
        "INSERT INTO ingredient_season (ingredient_id, season_id) VALUES (?, ?);",
        [(ingredient_id, season_id) for season_id in season_ids],
    )
