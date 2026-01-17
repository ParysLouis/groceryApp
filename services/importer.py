from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from db.connection import get_connection
from services.recipes import (
    TIME_OPTIONS,
    normalize_difficulty,
    normalize_time_label,
    normalize_servings,
)


class IngredientImportError(ValueError):
    pass


class RecipeImportError(ValueError):
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


def parse_recipe_json(payload: str) -> list[dict[str, Any]]:
    try:
        data = json.loads(payload)
    except json.JSONDecodeError as exc:
        raise RecipeImportError("Le fichier JSON est invalide.") from exc

    if not isinstance(data, dict):
        raise RecipeImportError("Le JSON doit contenir un objet racine.")

    recipes = data.get("recipes")
    if not isinstance(recipes, list):
        raise RecipeImportError("Le JSON doit contenir une liste 'recipes'.")

    parsed: list[dict[str, Any]] = []
    for index, recipe in enumerate(recipes, start=1):
        if not isinstance(recipe, dict):
            raise RecipeImportError(
                f"La recette #{index} doit être un objet JSON."
            )
        name = _required_string(recipe, "name", index)
        instructions = recipe.get("instructions", "")
        if instructions is None:
            instructions = ""
        if not isinstance(instructions, str):
            raise RecipeImportError(
                f"La recette #{index} doit contenir un texte 'instructions'."
            )

        time_label = recipe.get("time")
        if time_label is None:
            time_label = ""
        if not isinstance(time_label, str):
            raise RecipeImportError(
                f"La recette #{index} doit contenir un texte 'time'."
            )
        cleaned_time_label = time_label.strip()
        if cleaned_time_label and cleaned_time_label not in TIME_OPTIONS:
            raise RecipeImportError(
                f"La recette #{index} contient un temps invalide."
            )

        difficulty = recipe.get("difficulty")
        if difficulty is None:
            difficulty = ""
        if not isinstance(difficulty, str):
            raise RecipeImportError(
                f"La recette #{index} doit contenir un texte 'difficulty'."
            )
        cleaned_difficulty = difficulty.strip()
        normalized_difficulty: str | None = None
        if cleaned_difficulty:
            try:
                normalized_difficulty = normalize_difficulty(cleaned_difficulty)
            except ValueError as exc:
                raise RecipeImportError(
                    f"La recette #{index} contient une difficulté invalide."
                ) from exc

        servings = recipe.get("servings", 1)
        if servings is None:
            servings = 1
        try:
            normalized_servings = normalize_servings(servings)
        except ValueError as exc:
            raise RecipeImportError(
                f"La recette #{index} contient un nombre de personnes invalide."
            ) from exc

        ingredients = recipe.get("ingredients", [])
        if ingredients is None:
            ingredients = []
        if not isinstance(ingredients, list):
            raise RecipeImportError(
                f"La recette #{index} doit contenir une liste 'ingredients'."
            )
        parsed_ingredients: list[dict[str, Any]] = []
        for ingredient_index, ingredient in enumerate(ingredients, start=1):
            if not isinstance(ingredient, dict):
                raise RecipeImportError(
                    f"L'ingrédient #{ingredient_index} de la recette #{index} est invalide."
                )
            ingredient_name = _required_string(
                ingredient, "name", ingredient_index
            )
            quantity = ingredient.get("quantity")
            if not isinstance(quantity, (int, float)):
                raise RecipeImportError(
                    f"La quantité de l'ingrédient #{ingredient_index} de la recette #{index} est invalide."
                )
            if quantity <= 0:
                raise RecipeImportError(
                    f"La quantité de l'ingrédient #{ingredient_index} de la recette #{index} doit être positive."
                )
            parsed_ingredients.append(
                {"name": ingredient_name, "quantity": float(quantity)}
            )

        parsed.append(
            {
                "name": name,
                "instructions": instructions.strip(),
                "time_label": cleaned_time_label or None,
                "difficulty": normalized_difficulty,
                "servings": normalized_servings,
                "ingredients": parsed_ingredients,
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


def import_recipes_from_json(
    file_path: str | Path, db_path: str | None = None
) -> int:
    payload = Path(file_path).read_text(encoding="utf-8")
    recipes = parse_recipe_json(payload)

    with get_connection(db_path) as connection:
        ingredient_lookup = _load_lookup(connection, "ingredient")
        imported = 0

        for recipe in recipes:
            normalized_time_label, total_minutes = normalize_time_label(
                recipe.get("time_label")
            )
            normalized_difficulty = normalize_difficulty(
                recipe.get("difficulty")
            )
            cursor = connection.execute(
                """
                INSERT INTO recipe (
                    name,
                    total_minutes,
                    time_label,
                    difficulty,
                    servings,
                    notes
                )
                VALUES (?, ?, ?, ?, ?, ?);
                """,
                (
                    recipe["name"],
                    total_minutes,
                    normalized_time_label,
                    normalized_difficulty,
                    recipe.get("servings", 1),
                    recipe["instructions"] or None,
                ),
            )
            recipe_id = cursor.lastrowid
            ingredients_to_insert = []
            for ingredient in recipe["ingredients"]:
                ingredient_id = _resolve_lookup(
                    ingredient_lookup, ingredient["name"], "ingrédient"
                )
                ingredients_to_insert.append(
                    (recipe_id, ingredient_id, ingredient["quantity"])
                )
            if ingredients_to_insert:
                connection.executemany(
                    """
                    INSERT INTO recipe_ingredient (recipe_id, ingredient_id, quantity)
                    VALUES (?, ?, ?);
                    """,
                    ingredients_to_insert,
                )
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
