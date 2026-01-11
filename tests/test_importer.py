import json
import tempfile
import unittest
from pathlib import Path

from db.init_db import initialize_database
from db.connection import get_connection
from services.importer import (
    IngredientImportError,
    import_ingredients_from_json,
    parse_ingredient_json,
)


class ImporterTests(unittest.TestCase):
    def test_parse_ingredient_json_valid(self):
        payload = json.dumps(
            {
                "ingredients": [
                    {
                        "name": "Tomate",
                        "aisle": "Fruits et légumes",
                        "unit": "pièce",
                        "seasons": ["été", "printemps"],
                    }
                ]
            }
        )
        parsed = parse_ingredient_json(payload)
        self.assertEqual(len(parsed), 1)
        self.assertEqual(parsed[0]["name"], "Tomate")
        self.assertEqual(parsed[0]["seasons"], ["été", "printemps"])

    def test_parse_ingredient_json_requires_fields(self):
        payload = json.dumps({"ingredients": [{"name": "Lait"}]})
        with self.assertRaises(IngredientImportError):
            parse_ingredient_json(payload)

    def test_import_ingredients_from_json_inserts_rows(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            initialize_database(str(db_path))
            json_path = Path(tmpdir) / "ingredients.json"
            json_path.write_text(
                json.dumps(
                    {
                        "ingredients": [
                            {
                                "name": "Courgette",
                                "aisle": "Fruits et légumes",
                                "unit": "pièce",
                                "seasons": ["été"],
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )

            imported = import_ingredients_from_json(json_path, str(db_path))
            self.assertEqual(imported, 1)

            with get_connection(str(db_path)) as connection:
                ingredient = connection.execute(
                    "SELECT id, name FROM ingredient WHERE name = ?;",
                    ("Courgette",),
                ).fetchone()
                self.assertIsNotNone(ingredient)
                seasons = connection.execute(
                    """
                    SELECT season.name
                    FROM ingredient_season
                    JOIN season ON season.id = ingredient_season.season_id
                    WHERE ingredient_season.ingredient_id = ?;
                    """,
                    (ingredient["id"],),
                ).fetchall()

            self.assertEqual([row["name"] for row in seasons], ["été"])


if __name__ == "__main__":
    unittest.main()
