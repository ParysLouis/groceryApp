from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from db.connection import get_connection


class IngredientImportError(ValueError):
    pass


def parse_ingredient_json(payload: str) -> list[dict[str, Any]]:
    try:
        data = json.loads(payload)
    except json.JSONDecodeError as exc:
        raise IngredientImportError("Le fichier JSON est invalide.") from exc

    if not isinstance(data, dict):
        raise IngredientImportError("Le JSON doit contenir un objet racine.")

    ingredients = data.get("ingredients")
    if not isinstance(ingredients, list):
        raise IngredientImportError(
            "Le JSON doit contenir une liste 'ingredients'."
        )

    parsed: list[dict[str, Any]] = []
    for index, ingredient in enumerate(ingredients, start=1):
        if not isinstance(ingredient, dict):
            raise IngredientImportError(
                f"L'ingrédient #{index} doit être un objet JSON."
            )

        name = _required_string(ingredient, "name", index)
        aisle = _required_string(ingredient, "aisle", index)
        unit = _required_string(ingredient, "unit", index)
        seasons = ingredient.get("seasons", [])
        if seasons is None:
            seasons = []
        if not isinstance(seasons, list):
            raise IngredientImportError(
                f"L'ingrédient #{index} doit contenir une liste 'seasons'."
            )
        parsed_seasons: list[str] = []
        for season_index, season in enumerate(seasons, start=1):
            if not isinstance(season, str) or not season.strip():
                raise IngredientImportError(
                    f"La saison #{season_index} de l'ingrédient #{index} est invalide."
                )
            parsed_seasons.append(season.strip())

        parsed.append(
            {
                "name": name,
                "aisle": aisle,
                "unit": unit,
                "seasons": parsed_seasons,
            }
        )

    return parsed


def import_ingredients_from_json(
    file_path: str | Path, db_path: str | None = None
) -> int:
    payload = Path(file_path).read_text(encoding="utf-8")
    ingredients = parse_ingredient_json(payload)

    with get_connection(db_path) as connection:
        aisle_lookup = _load_lookup(connection, "aisle")
        unit_lookup = _load_lookup(connection, "unit")
        season_lookup = _load_lookup(connection, "season")
        imported = 0

        for ingredient in ingredients:
            name = ingredient["name"]
            aisle_id = _resolve_lookup(aisle_lookup, ingredient["aisle"], "rayon")
            unit_id = _resolve_lookup(unit_lookup, ingredient["unit"], "unité")
            season_ids = [
                _resolve_lookup(season_lookup, season_name, "saison")
                for season_name in ingredient["seasons"]
            ]

            ingredient_id = _upsert_ingredient(
                connection, name, aisle_id, unit_id
            )
            _replace_seasons(connection, ingredient_id, season_ids)
            imported += 1

        connection.commit()

    return imported


def _required_string(ingredient: dict[str, Any], key: str, index: int) -> str:
    value = ingredient.get(key)
    if not isinstance(value, str) or not value.strip():
        raise IngredientImportError(
            f"L'ingrédient #{index} doit définir '{key}'."
        )
    return value.strip()


def _load_lookup(connection, table: str) -> dict[str, int]:
    rows = connection.execute(f"SELECT id, name FROM {table};").fetchall()
    return {_normalize(row["name"]): row["id"] for row in rows}


def _resolve_lookup(lookup: dict[str, int], value: str, label: str) -> int:
    key = _normalize(value)
    if key not in lookup:
        raise IngredientImportError(
            f"{label.capitalize()} inconnue: '{value}'."
        )
    return lookup[key]


def _normalize(value: str) -> str:
    return value.strip().lower()


def _upsert_ingredient(connection, name: str, aisle_id: int, unit_id: int) -> int:
    existing = connection.execute(
        "SELECT id FROM ingredient WHERE name = ?;",
        (name,),
    ).fetchone()
    if existing:
        ingredient_id = existing["id"]
        connection.execute(
            """
            UPDATE ingredient
            SET default_aisle_id = ?, unit_id = ?
            WHERE id = ?;
            """,
            (aisle_id, unit_id, ingredient_id),
        )
        return ingredient_id

    cursor = connection.execute(
        """
        INSERT INTO ingredient (name, default_aisle_id, unit_id)
        VALUES (?, ?, ?);
        """,
        (name, aisle_id, unit_id),
    )
    return cursor.lastrowid


def _replace_seasons(connection, ingredient_id: int, season_ids: list[int]) -> None:
    connection.execute(
        "DELETE FROM ingredient_season WHERE ingredient_id = ?;",
        (ingredient_id,),
    )
    connection.executemany(
        "INSERT INTO ingredient_season (ingredient_id, season_id) VALUES (?, ?);",
        [(ingredient_id, season_id) for season_id in season_ids],
    )
