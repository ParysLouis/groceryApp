# Recipes & Grocery List

A desktop app for managing ingredients, recipes, and shopping lists using Python 3, SQLite, and Tkinter.

## Setup

1. Ensure Python 3 is installed.
2. From the repository root, run:

```bash
python -m app
```

The first launch initializes a local SQLite database in `data/recipes.db` with default aisles, units, and seasons.

## Project Structure

```
app/        # Tkinter UI
services/   # Business logic (consolidation, export)
db/         # Database schema + initialization
tests/      # Unit tests
```

## Usage

- **Ingredients tab**: Add, edit, or delete ingredients. Each ingredient includes a default aisle, unit, and optional seasons.
- **Recipes tab**: Placeholder for upcoming recipe CRUD.
- **Shopping List tab**: Placeholder for upcoming list builder and export.

## Running Tests

```bash
python -m unittest discover -s tests
```
