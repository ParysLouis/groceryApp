import unittest
from datetime import date
from pathlib import Path

from services.export import ExportItem, ExportSection, export_shopping_list, generate_export_html


class ExportTests(unittest.TestCase):
    def test_generate_html_includes_list_id(self):
        sections = [
            ExportSection(
                aisle_name="Fruits et légumes",
                items=[ExportItem(label="Tomate", quantity=2, unit="pc")],
            )
        ]
        html = generate_export_html("2024-01-01", sections)
        self.assertIn("liste-de-courses-2024-01-01", html)
        self.assertIn("Tomate", html)

    def test_export_writes_file(self):
        sections = [
            ExportSection(
                aisle_name="Fruits et légumes",
                items=[ExportItem(label="Tomate", quantity=2, unit="pc")],
            )
        ]
        output_dir = Path("data/test_exports")
        file_path = export_shopping_list(sections, output_dir, list_date=date(2024, 1, 2))
        self.assertTrue(file_path.exists())
        content = file_path.read_text(encoding="utf-8")
        self.assertIn("liste-de-courses-2024-01-02", content)
        file_path.unlink()
        output_dir.rmdir()


if __name__ == "__main__":
    unittest.main()
