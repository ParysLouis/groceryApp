from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class ExportItem:
    label: str
    quantity: float
    unit: str
    note: str | None = None


@dataclass(frozen=True)
class ExportSection:
    aisle_name: str
    items: list[ExportItem]


def generate_export_html(list_id: str, sections: Iterable[ExportSection]) -> str:
    section_html = []
    for section in sections:
        items_html = "".join(
            _item_row(list_id, index, item)
            for index, item in enumerate(section.items)
        )
        section_html.append(
            f"<section class=\"aisle\"><h2>{section.aisle_name}</h2>"
            f"<ul>{items_html}</ul></section>"
        )

    sections_html = "".join(section_html)
    return f"""
<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>Shopping List</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 16px; background: #fafafa; }}
    h1 {{ font-size: 1.5rem; margin-bottom: 0.5rem; }}
    h2 {{ font-size: 1.1rem; margin-top: 1rem; }}
    ul {{ list-style: none; padding-left: 0; }}
    li {{ display: flex; align-items: center; gap: 0.6rem; padding: 0.4rem 0; }}
    .note {{ color: #666; font-size: 0.9rem; }}
    .aisle {{ background: #fff; padding: 0.8rem; margin-bottom: 0.8rem; border-radius: 8px; box-shadow: 0 1px 2px rgba(0,0,0,0.05); }}
  </style>
</head>
<body>
  <h1>Shopping List</h1>
  {sections_html}
  <script>
    const listId = "{list_id}";
    function storageKey(index) {{
      return `shopping-list-${listId}-${index}`;
    }}
    document.querySelectorAll("input[type=checkbox]").forEach((checkbox) => {{
      const key = storageKey(checkbox.dataset.index);
      checkbox.checked = localStorage.getItem(key) === "true";
      checkbox.addEventListener("change", () => {{
        localStorage.setItem(key, checkbox.checked ? "true" : "false");
      }});
    }});
  </script>
</body>
</html>
""".strip()


def _item_row(list_id: str, index: int, item: ExportItem) -> str:
    note_html = f" <span class=\"note\">({item.note})</span>" if item.note else ""
    label = f"{item.label} - {item.quantity:g} {item.unit}{note_html}"
    return (
        f"<li><input type=\"checkbox\" data-index=\"{index}\" />"
        f"<span>{label}</span></li>"
    )


def export_shopping_list(
    sections: Iterable[ExportSection],
    output_dir: str | Path,
    list_date: date | None = None,
) -> Path:
    list_date = list_date or date.today()
    list_id = list_date.isoformat()
    html = generate_export_html(list_id, sections)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    file_path = output_dir / f"shopping-list-{list_date.isoformat()}.html"
    file_path.write_text(html, encoding="utf-8")
    return file_path
