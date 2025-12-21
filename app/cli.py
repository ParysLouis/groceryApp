"""Command-line utility for managing grocery items without the API server.

This module offers a small CLI so users can add, list, update, toggle, and
remove grocery items directly against the SQLite database. It shares the same
models and database configuration as the API, ensuring data stays in sync.
"""

from __future__ import annotations

import argparse
from typing import Iterable

from .database import get_session
from .models import GroceryItem


def format_item(item: GroceryItem) -> str:
    status = "✓" if item.purchased else " "
    category = item.category or "Uncategorized"
    return f"[{status}] #{item.id} {item.name} (qty: {item.quantity}, category: {category})"


def list_items(include_purchased: bool) -> None:
    with get_session() as session:
        query = session.query(GroceryItem)
        if not include_purchased:
            query = query.filter(GroceryItem.purchased.is_(False))
        items = query.order_by(GroceryItem.created_at.desc()).all()

    if not items:
        print("No grocery items found.")
        return

    print("Grocery items:")
    for item in items:
        print(f"  • {format_item(item)}")


def add_item(name: str, quantity: str, category: str | None, purchased: bool) -> None:
    with get_session() as session:
        item = GroceryItem(
            name=name,
            quantity=quantity,
            category=category,
            purchased=purchased,
        )
        session.add(item)
        session.flush()
        print(f"Added {format_item(item)}")


def update_item(
    item_id: int,
    name: str | None,
    quantity: str | None,
    category: str | None,
    purchased: bool | None,
) -> None:
    with get_session() as session:
        item = session.get(GroceryItem, item_id)
        if not item:
            raise SystemExit(f"Item with id {item_id} not found.")

        if name is not None:
            item.name = name
        if quantity is not None:
            item.quantity = quantity
        if category is not None:
            item.category = category
        if purchased is not None:
            item.purchased = purchased

        session.add(item)
        print(f"Updated {format_item(item)}")


def toggle_item(item_id: int) -> None:
    with get_session() as session:
        item = session.get(GroceryItem, item_id)
        if not item:
            raise SystemExit(f"Item with id {item_id} not found.")

        item.purchased = not item.purchased
        session.add(item)
        print(f"Toggled {format_item(item)}")


def delete_item(item_id: int) -> None:
    with get_session() as session:
        item = session.get(GroceryItem, item_id)
        if not item:
            raise SystemExit(f"Item with id {item_id} not found.")

        session.delete(item)
        print(f"Deleted item #{item_id} ({item.name}).")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Manage grocery items without needing the HTTP API server.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list", help="List grocery items")
    list_parser.add_argument(
        "--all",
        action="store_true",
        help="Include items that have already been purchased.",
    )

    add_parser = subparsers.add_parser("add", help="Add a new grocery item")
    add_parser.add_argument("name", help="Name of the grocery item")
    add_parser.add_argument(
        "-q",
        "--quantity",
        default="1",
        help="Quantity to buy (default: 1)",
    )
    add_parser.add_argument(
        "-c",
        "--category",
        default=None,
        help="Optional category for grouping items",
    )
    add_parser.add_argument(
        "--purchased",
        action="store_true",
        help="Mark the new item as already purchased",
    )

    update_parser = subparsers.add_parser("update", help="Update an existing item")
    update_parser.add_argument("item_id", type=int, help="ID of the item to update")
    update_parser.add_argument("--name", help="New name for the item")
    update_parser.add_argument("--quantity", help="New quantity to buy")
    update_parser.add_argument("--category", help="New category")
    update_parser.add_argument(
        "--purchased",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="Mark the item as purchased or not",
    )

    toggle_parser = subparsers.add_parser(
        "toggle", help="Toggle the purchased status of an item"
    )
    toggle_parser.add_argument("item_id", type=int, help="ID of the item to toggle")

    delete_parser = subparsers.add_parser("delete", help="Remove an item")
    delete_parser.add_argument("item_id", type=int, help="ID of the item to remove")

    return parser


def main(argv: Iterable[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)

    if args.command == "list":
        list_items(include_purchased=args.all)
    elif args.command == "add":
        add_item(args.name, args.quantity, args.category, args.purchased)
    elif args.command == "update":
        if (
            args.name is None
            and args.quantity is None
            and args.category is None
            and args.purchased is None
        ):
            raise SystemExit("No updates specified. Provide at least one field to change.")
        update_item(
            args.item_id,
            name=args.name,
            quantity=args.quantity,
            category=args.category,
            purchased=args.purchased,
        )
    elif args.command == "toggle":
        toggle_item(args.item_id)
    elif args.command == "delete":
        delete_item(args.item_id)
    else:
        parser.error(f"Unknown command: {args.command}")


if __name__ == "__main__":
    main()
