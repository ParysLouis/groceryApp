# Recettes & Liste de courses

Une application de bureau pour gérer les ingrédients, les recettes et les listes de courses avec Python 3, SQLite et CustomTkinter.

## Installation

1. Assurez-vous que Python 3 est installé.
2. Depuis la racine du dépôt, exécutez :
```bash
python -m pip install customtkinter
```

3. Depuis la racine du dépôt, exécutez :

```bash
python -m app
```

Le premier lancement initialise une base SQLite locale dans `data/recipes.db` avec les rayons, unités et saisons par défaut.

## Structure du projet

```
app/        # Interface CustomTkinter
services/   # Logique métier (consolidation, export)
db/         # Schéma de base de données + initialisation
tests/      # Tests unitaires
```

## Utilisation

- **Onglet Ingrédients** : Ajouter, modifier ou supprimer des ingrédients. Chaque ingrédient comprend un rayon par défaut, une unité et des saisons optionnelles.
- **Import JSON** : Utilisez le bouton « Importer » dans l'onglet Ingrédients pour importer un fichier JSON d'ingrédients.
- **Onglet Recettes** : Espace réservé pour le CRUD des recettes à venir.
- **Onglet Liste de courses** : Espace réservé pour le générateur de liste et l'export à venir.

### Format d'import JSON

L'importateur attend un fichier JSON avec un objet racine contenant une liste `ingredients`. Chaque ingrédient exige `name`, `aisle` et `unit`. `seasons` est optionnel et doit être une liste de chaînes correspondant aux saisons existantes dans la base de données.

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

L'importateur de recettes attend un fichier JSON avec un objet racine contenant une liste `recipes`. Chaque recette nécessite `name`, `difficulty`, `time_minutes`, `instructions` (facultatif) et une liste `ingredients` (facultative). Chaque entrée d'ingrédient doit référencer un nom d'ingrédient existant et inclure une `quantity` numérique. `difficulty` doit être l'une des valeurs suivantes : `facile`, `moyen`, `difficile` (ne pas utiliser `easy`, `medium`, `hard`). `time_minutes` doit être un entier positif représentant la durée totale en minutes.

```json
{
  "recipes": [
    {
      "name": "Salade tomate",
      "difficulty": "facile",
      "time_minutes": 10,
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

### Prompt pour chatbot afin de créer un JSON de recette

Utilisez le prompt suivant avec un chatbot pour générer le JSON de recette. Fournissez votre liste d'ingrédients et toutes les informations connues ; le chatbot doit poser des questions de suivi pour les éléments manquants, puis renvoyer uniquement le JSON final au format attendu.

```
You are helping me create a JSON payload for a recipe importer. The JSON must follow this schema:

{
  "recipes": [
    {
      "name": string,                          // required
      "difficulty": string,                    // required: facile | moyen | difficile
      "time_minutes": number,                  // required: positive integer (minutes)
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
1) Ask me clarifying questions if any required information is missing (recipe name, difficulty, total time in minutes, ingredient names, quantities, or optional instructions if I want to include them).
2) Difficulty must be one of: facile, moyen, difficile (do not use easy, medium, hard).
3) time_minutes must be a positive integer representing the total time in minutes (for example 10, 45, 120).
4) If I provide an ingredient list without quantities, ask for each quantity.
5) If I provide quantities but no units, do not add units (quantities are numeric only).
6) If I provide multiple recipes, output a JSON array with one object per recipe.
7) Once you have all required info, respond ONLY with the final JSON and no extra text.

Now, here is what I know so far:
<paste recipe name, optional instructions, and ingredient list here>
```

## Lancer les tests

```bash
python -m unittest discover -s tests
```
