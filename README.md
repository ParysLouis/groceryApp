# Recipes & Grocery List

A desktop app for managing ingredients, recipes, and shopping lists using Python 3, SQLite, and CustomTkinter.

## Setup

1. Ensure Python 3 is installed.
2. From the repository root, run:
```bash
python -m pip install customtkinter
```

3. From the repository root, run:

```bash
python -m app
```

The first launch initializes a local SQLite database in `data/recipes.db` with default aisles, units, and seasons.

## Project Structure

```
app/        # CustomTkinter UI
services/   # Business logic (consolidation, export)
db/         # Database schema + initialization
tests/      # Unit tests
```

## Usage

- **Ingredients tab**: Add, edit, or delete ingredients. Each ingredient includes a default aisle, unit, and optional seasons.
- **Import JSON**: Use the "Importer" button in the Ingredients tab to import a JSON file with ingredients.
- **Recipes tab**: Placeholder for upcoming recipe CRUD.
- **Shopping List tab**: Placeholder for upcoming list builder and export.

### JSON import format

The importer expects a JSON file with a top-level object containing an `ingredients` list. Each ingredient requires `name`, `aisle`, and `unit`. `seasons` is optional and must be a list of strings matching existing seasons in the database.

```json
{
  "ingredients": [
    {
      "name": "Tomate",
      "aisle": "Fruits et légumes",
      "unit": "pièce",
      "seasons": ["été", "printemps"]
    }
  ]
}
```

The recipe importer expects a JSON file with a top-level object containing a `recipes` list. Each recipe requires `name`, optional `instructions`, and an optional `ingredients` list. Each ingredient entry must reference an existing ingredient name and include a numeric `quantity`.

```json
{
  "recipes": [
    {
      "name": "Salade tomate",
      "instructions": "Couper les tomates et assaisonner.",
      "ingredients": [
        {
          "name": "Tomate",
          "quantity": 2
        }
      ]
    }
  ]
}
```

### Chatbot prompt for creating a recipe JSON

Use the following prompt with a chatbot to generate the recipe JSON. Provide your ingredient list and any known details; the chatbot should ask follow-up questions for anything missing, then return only the final JSON in the expected format.

```
You are helping me create a JSON payload for a recipe importer. The JSON must follow this schema:

{
  "recipes": [
    {
      "name": string,                          // required
      "instructions": string (optional),
      "ingredients": [
        {
          "name": string,                      // must match an existing ingredient name
          "quantity": number                   // numeric quantity only
        }
      ]
    }
  ]
}

Rules:
1) Ask me clarifying questions if any required information is missing (recipe name, ingredient names, quantities, or optional instructions if I want to include them).
2) If I provide an ingredient list without quantities, ask for each quantity.
3) If I provide quantities but no units, do not add units (quantities are numeric only).
4) If I provide multiple recipes, output a JSON array with one object per recipe.
5) Once you have all required info, respond ONLY with the final JSON and no extra text.

Now, here is what I know so far:
<paste recipe name, optional instructions, and ingredient list here>
```

## Running Tests

```bash
python -m unittest discover -s tests
```
