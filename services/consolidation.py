from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Iterable, Sequence


@dataclass(frozen=True)
class ShoppingItem:
    ingredient_name: str
    aisle_name: str
    aisle_order: int
    unit: str
    quantity: float
    note: str | None = None


@dataclass(frozen=True)
class ConsolidatedItem:
    ingredient_name: str
    aisle_name: str
    aisle_order: int
    unit: str
    quantity: float
    note: str | None = None


def consolidate_items(items: Iterable[ShoppingItem]) -> list[ConsolidatedItem]:
    grouped: dict[tuple[str, str | None, str], ConsolidatedItem] = {}
    for item in items:
        key = (item.ingredient_name, item.note, item.unit)
        if key in grouped:
            existing = grouped[key]
            grouped[key] = ConsolidatedItem(
                ingredient_name=existing.ingredient_name,
                aisle_name=existing.aisle_name,
                aisle_order=existing.aisle_order,
                unit=existing.unit,
                quantity=existing.quantity + item.quantity,
                note=existing.note,
            )
        else:
            grouped[key] = ConsolidatedItem(
                ingredient_name=item.ingredient_name,
                aisle_name=item.aisle_name,
                aisle_order=item.aisle_order,
                unit=item.unit,
                quantity=item.quantity,
                note=item.note,
            )
    return sorted(
        grouped.values(),
        key=lambda item: (item.aisle_order, item.ingredient_name.lower()),
    )


def group_by_aisle(items: Sequence[ConsolidatedItem]) -> list[tuple[str, list[ConsolidatedItem]]]:
    grouped: dict[tuple[int, str], list[ConsolidatedItem]] = defaultdict(list)
    for item in items:
        grouped[(item.aisle_order, item.aisle_name)].append(item)
    return [
        (aisle_name, grouped[(order, aisle_name)])
        for order, aisle_name in sorted(grouped.keys())
    ]
