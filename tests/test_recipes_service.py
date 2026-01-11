import tempfile
import unittest
from pathlib import Path

from db.connection import get_connection
from db.init_db import initialize_database
from services.ingredients import create_ingredient
from services.recipes import add_recipe_ingredient, create_recipe, list_recipes


class RecipeServiceTests(unittest.TestCase):
    def _get_ids(self, db_path: str, season_name: str):
        with get_connection(db_path) as connection:
            aisle_id = connection.execute(
                "SELECT id FROM aisle ORDER BY sort_order ASC LIMIT 1;"
            ).fetchone()["id"]
            unit_id = connection.execute(
                "SELECT id FROM unit ORDER BY name ASC LIMIT 1;"
            ).fetchone()["id"]
            season_id = connection.execute(
                "SELECT id FROM season WHERE name = ?;",
                (season_name,),
            ).fetchone()["id"]
        return aisle_id, unit_id, season_id

    def test_create_recipe_in_list(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            initialize_database(str(db_path))

            create_recipe(
                "Salade",
                "Mélanger.",
                time_label="30",
                difficulty="Easy",
                db_path=str(db_path),
            )
            recipes = list_recipes(db_path=str(db_path))

            self.assertEqual(len(recipes), 1)
            self.assertEqual(recipes[0]["name"], "Salade")
            self.assertEqual(recipes[0]["time_label"], "30")
            self.assertEqual(recipes[0]["difficulty"], "Easy")

    def test_rejects_empty_recipe_name(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            initialize_database(str(db_path))

            with self.assertRaises(ValueError):
                create_recipe(
                    "   ",
                    "Mélanger.",
                    time_label="15min",
                    difficulty="Easy",
                    db_path=str(db_path),
                )

    def test_filters_out_mixed_season_recipes(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            initialize_database(str(db_path))
            aisle_id, unit_id, summer_id = self._get_ids(str(db_path), "été")
            _, _, autumn_id = self._get_ids(str(db_path), "automne")

            summer_ingredient = create_ingredient(
                "Tomate", aisle_id, unit_id, [summer_id], db_path=str(db_path)
            )
            autumn_ingredient = create_ingredient(
                "Courge", aisle_id, unit_id, [autumn_id], db_path=str(db_path)
            )

            summer_recipe_id = create_recipe(
                "Salade d'été",
                "Mélanger.",
                db_path=str(db_path),
            )
            mixed_recipe_id = create_recipe(
                "Mélange saison",
                "Mélanger.",
                db_path=str(db_path),
            )

            add_recipe_ingredient(
                summer_recipe_id, summer_ingredient, 1, db_path=str(db_path)
            )
            add_recipe_ingredient(
                mixed_recipe_id, summer_ingredient, 1, db_path=str(db_path)
            )
            add_recipe_ingredient(
                mixed_recipe_id, autumn_ingredient, 1, db_path=str(db_path)
            )

            recipes = list_recipes(db_path=str(db_path), season_id=summer_id)

            self.assertEqual([recipe["name"] for recipe in recipes], ["Salade d'été"])

    def test_includes_recipes_with_unseasoned_ingredients(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            initialize_database(str(db_path))
            aisle_id, unit_id, summer_id = self._get_ids(str(db_path), "été")

            unseasoned_ingredient = create_ingredient(
                "Sel", aisle_id, unit_id, [], db_path=str(db_path)
            )
            recipe_id = create_recipe(
                "Assaisonnement",
                "Ajouter.",
                db_path=str(db_path),
            )
            add_recipe_ingredient(
                recipe_id, unseasoned_ingredient, 1, db_path=str(db_path)
            )

            recipes = list_recipes(db_path=str(db_path), season_id=summer_id)

            self.assertEqual([recipe["name"] for recipe in recipes], ["Assaisonnement"])


if __name__ == "__main__":
    unittest.main()
