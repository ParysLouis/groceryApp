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
- **Onglet Recettes** : Créez vos recettes avec le temps, la difficulté et le nombre de personnes. Ajoutez ensuite les ingrédients et leurs quantités.
- **Onglet Liste de courses** : Sélectionnez des recettes, ajustez le nombre de personnes par recette et générez automatiquement la liste consolidée.

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

L'importateur de recettes attend un fichier JSON avec un objet racine contenant une liste `recipes`. Chaque recette nécessite `name`, `difficulty`, `time` (facultatif), `instructions` (facultatif) et une liste `ingredients` (facultative). Le champ `servings` est optionnel et représente le nombre de personnes (entier positif). Chaque entrée d'ingrédient doit référencer un nom d'ingrédient existant et inclure une `quantity` numérique. `difficulty` peut être l'une des valeurs suivantes : `facile`, `moyen`, `difficile` (les équivalents `easy`, `medium`, `hard` sont acceptés). `time` doit correspondre à l'une des valeurs disponibles dans l'application (ex. `15min`, `30`, `45`, `1h`, `1h30`).

```json
{
  "recipes": [
    {
      "name": "Salade tomate",
      "difficulty": "facile",
      "time": "15min",
      "servings": 2,
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
      "difficulty": string,                    // required: facile | moyen | difficile (easy|medium|hard accepted)
      "time": string,                          // optional: 15min | 30 | 45 | 1h | 1h30 | 2h | 2h30 | 3h | 3h30 | 4h+
      "servings": number,                      // optional: positive integer
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
1) Ask me clarifying questions if any required information is missing (recipe name, difficulty, ingredient names, quantities, or optional instructions if I want to include them).
2) Difficulty must be one of: facile, moyen, difficile (easy/medium/hard are accepted aliases).
3) If I provide a total time, use one of the allowed time labels (15min, 30, 45, 1h, 1h30, 2h, 2h30, 3h, 3h30, 4h+).
4) If I provide a number of servings, ensure it is a positive integer.
5) If I provide an ingredient list without quantities, ask for each quantity.
6) If I provide quantities but no units, do not add units (quantities are numeric only).
7) If I provide multiple recipes, output a JSON array with one object per recipe.
8) Once you have all required info, respond ONLY with the final JSON and no extra text.

Now, here is what I know so far:
<paste recipe name, optional instructions, and ingredient list here>
```

## Lancer les tests

```bash
python -m unittest discover -s tests
```
