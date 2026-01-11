SCHEMA_SQL = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS aisle (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    sort_order INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS unit (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    abbreviation TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS season (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS ingredient (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    default_aisle_id INTEGER NOT NULL,
    unit_id INTEGER NOT NULL,
    FOREIGN KEY (default_aisle_id) REFERENCES aisle(id) ON DELETE RESTRICT,
    FOREIGN KEY (unit_id) REFERENCES unit(id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS ingredient_season (
    ingredient_id INTEGER NOT NULL,
    season_id INTEGER NOT NULL,
    PRIMARY KEY (ingredient_id, season_id),
    FOREIGN KEY (ingredient_id) REFERENCES ingredient(id) ON DELETE CASCADE,
    FOREIGN KEY (season_id) REFERENCES season(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS recipe (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    total_minutes INTEGER NOT NULL,
    source_url TEXT,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS recipe_season (
    recipe_id INTEGER NOT NULL,
    season_id INTEGER NOT NULL,
    PRIMARY KEY (recipe_id, season_id),
    FOREIGN KEY (recipe_id) REFERENCES recipe(id) ON DELETE CASCADE,
    FOREIGN KEY (season_id) REFERENCES season(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS recipe_ingredient (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    recipe_id INTEGER NOT NULL,
    ingredient_id INTEGER NOT NULL,
    quantity REAL NOT NULL,
    note TEXT,
    FOREIGN KEY (recipe_id) REFERENCES recipe(id) ON DELETE CASCADE,
    FOREIGN KEY (ingredient_id) REFERENCES ingredient(id) ON DELETE RESTRICT
);
"""

DEFAULT_AISLES = [
    (1, "Produce"),
    (2, "Meat & Seafood"),
    (3, "Dairy & Eggs"),
    (4, "Bakery"),
    (5, "Pantry"),
    (6, "Frozen"),
    (7, "Household"),
    (8, "Other")
]

DEFAULT_UNITS = [
    ("piece", "pc"),
    ("gram", "g"),
    ("kilogram", "kg"),
    ("milliliter", "ml"),
    ("liter", "l"),
    ("teaspoon", "tsp"),
    ("tablespoon", "tbsp"),
    ("cup", "cup"),
]

DEFAULT_SEASONS = [
    "winter",
    "spring",
    "summer",
    "autumn",
]
