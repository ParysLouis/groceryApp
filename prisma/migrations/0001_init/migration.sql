-- Create tables
CREATE TABLE IF NOT EXISTS "Aisle" (
  "id" TEXT PRIMARY KEY NOT NULL,
  "name" TEXT NOT NULL UNIQUE,
  "sortOrder" INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS "Unit" (
  "id" TEXT PRIMARY KEY NOT NULL,
  "name" TEXT NOT NULL UNIQUE,
  "abbreviation" TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS "Season" (
  "id" TEXT PRIMARY KEY NOT NULL,
  "name" TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS "Ingredient" (
  "id" TEXT PRIMARY KEY NOT NULL,
  "name" TEXT NOT NULL UNIQUE,
  "defaultAisleId" TEXT NOT NULL,
  "unitId" TEXT NOT NULL,
  CONSTRAINT "Ingredient_defaultAisleId_fkey" FOREIGN KEY ("defaultAisleId") REFERENCES "Aisle"("id") ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT "Ingredient_unitId_fkey" FOREIGN KEY ("unitId") REFERENCES "Unit"("id") ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS "IngredientSeason" (
  "ingredientId" TEXT NOT NULL,
  "seasonId" TEXT NOT NULL,
  CONSTRAINT "IngredientSeason_pkey" PRIMARY KEY ("ingredientId", "seasonId"),
  CONSTRAINT "IngredientSeason_ingredientId_fkey" FOREIGN KEY ("ingredientId") REFERENCES "Ingredient"("id") ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT "IngredientSeason_seasonId_fkey" FOREIGN KEY ("seasonId") REFERENCES "Season"("id") ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS "Recipe" (
  "id" TEXT PRIMARY KEY NOT NULL,
  "name" TEXT NOT NULL,
  "totalMinutes" INTEGER NOT NULL,
  "sourceUrl" TEXT,
  "notes" TEXT
);

CREATE TABLE IF NOT EXISTS "RecipeSeason" (
  "recipeId" TEXT NOT NULL,
  "seasonId" TEXT NOT NULL,
  CONSTRAINT "RecipeSeason_pkey" PRIMARY KEY ("recipeId", "seasonId"),
  CONSTRAINT "RecipeSeason_recipeId_fkey" FOREIGN KEY ("recipeId") REFERENCES "Recipe"("id") ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT "RecipeSeason_seasonId_fkey" FOREIGN KEY ("seasonId") REFERENCES "Season"("id") ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS "RecipeIngredient" (
  "id" TEXT PRIMARY KEY NOT NULL,
  "recipeId" TEXT NOT NULL,
  "ingredientId" TEXT NOT NULL,
  "quantity" REAL NOT NULL,
  "note" TEXT,
  CONSTRAINT "RecipeIngredient_recipeId_fkey" FOREIGN KEY ("recipeId") REFERENCES "Recipe"("id") ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT "RecipeIngredient_ingredientId_fkey" FOREIGN KEY ("ingredientId") REFERENCES "Ingredient"("id") ON DELETE RESTRICT ON UPDATE CASCADE
);

-- Indexes for ordering
CREATE INDEX IF NOT EXISTS "Aisle_sortOrder_idx" ON "Aisle"("sortOrder");
