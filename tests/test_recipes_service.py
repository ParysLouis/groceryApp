import tempfile
import unittest
from pathlib import Path

from db.init_db import initialize_database
from services.recipes import create_recipe, list_recipes


class RecipeServiceTests(unittest.TestCase):
    def test_create_recipe_in_list(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            initialize_database(str(db_path))

            create_recipe("Salade", 10, db_path=str(db_path))
            recipes = list_recipes(db_path=str(db_path))

            self.assertEqual(len(recipes), 1)
            self.assertEqual(recipes[0]["name"], "Salade")

    def test_rejects_empty_recipe_name(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            initialize_database(str(db_path))

            with self.assertRaises(ValueError):
                create_recipe("   ", 5, db_path=str(db_path))


if __name__ == "__main__":
    unittest.main()
