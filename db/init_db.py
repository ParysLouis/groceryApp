from db.connection import get_connection
from db.schema import SCHEMA_SQL, DEFAULT_AISLES, DEFAULT_UNITS, DEFAULT_SEASONS


def initialize_database(db_path: str | None = None) -> None:
    with get_connection(db_path) as connection:
        connection.executescript(SCHEMA_SQL)
        ensure_recipe_columns(connection)
        seed_aisles(connection)
        seed_units(connection)
        seed_seasons(connection)
        normalize_seasons(connection)
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


def normalize_seasons(connection) -> None:
    seasons = connection.execute("SELECT id, name FROM season;").fetchall()
    name_to_id = {row["name"].strip().lower(): row["id"] for row in seasons}
    translations = {
        "winter": "hiver",
        "spring": "printemps",
        "summer": "été",
        "autumn": "automne",
        "fall": "automne",
    }
    for english_name, french_name in translations.items():
        english_id = name_to_id.get(english_name)
        if not english_id:
            continue
        french_key = french_name.lower()
        french_id = name_to_id.get(french_key)
        if french_id and french_id != english_id:
            connection.execute(
                "UPDATE ingredient_season SET season_id = ? WHERE season_id = ?;",
                (french_id, english_id),
            )
            connection.execute(
                "UPDATE recipe_season SET season_id = ? WHERE season_id = ?;",
                (french_id, english_id),
            )
            connection.execute("DELETE FROM season WHERE id = ?;", (english_id,))
        elif not french_id:
            connection.execute(
                "UPDATE season SET name = ? WHERE id = ?;",
                (french_name, english_id),
            )
            name_to_id[french_key] = english_id
