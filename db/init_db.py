from db.connection import get_connection
from db.schema import SCHEMA_SQL, DEFAULT_AISLES, DEFAULT_UNITS, DEFAULT_SEASONS


def initialize_database(db_path: str | None = None) -> None:
    with get_connection(db_path) as connection:
        connection.executescript(SCHEMA_SQL)
        ensure_recipe_columns(connection)
        seed_aisles(connection)
        seed_units(connection)
        seed_seasons(connection)
        connection.commit()


def ensure_recipe_columns(connection) -> None:
    columns = {
        row["name"]
        for row in connection.execute("PRAGMA table_info(recipe);").fetchall()
    }
    missing = {
        "time_label": "TEXT",
        "difficulty": "TEXT",
    }
    for column, definition in missing.items():
        if column not in columns:
            connection.execute(
                f"ALTER TABLE recipe ADD COLUMN {column} {definition};"
            )


def seed_aisles(connection) -> None:
    connection.executemany(
        "INSERT OR IGNORE INTO aisle (sort_order, name) VALUES (?, ?);",
        DEFAULT_AISLES,
    )


def seed_units(connection) -> None:
    connection.executemany(
        "INSERT OR IGNORE INTO unit (name, abbreviation) VALUES (?, ?);",
        DEFAULT_UNITS,
    )


def seed_seasons(connection) -> None:
    connection.executemany(
        "INSERT OR IGNORE INTO season (name) VALUES (?);",
        [(season,) for season in DEFAULT_SEASONS],
    )
