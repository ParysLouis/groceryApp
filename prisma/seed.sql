INSERT OR IGNORE INTO "Aisle" (id, name, sortOrder) VALUES
  ('aisle-produce', 'Produce', 1),
  ('aisle-bakery', 'Bakery', 2),
  ('aisle-dairy', 'Dairy', 3),
  ('aisle-meat', 'Meat & Seafood', 4),
  ('aisle-pantry', 'Pantry', 5),
  ('aisle-frozen', 'Frozen', 6),
  ('aisle-beverages', 'Beverages', 7),
  ('aisle-household', 'Household', 8);

INSERT OR IGNORE INTO "Unit" (id, name, abbreviation) VALUES
  ('unit-piece', 'Piece', 'pc'),
  ('unit-gram', 'Gram', 'g'),
  ('unit-kilogram', 'Kilogram', 'kg'),
  ('unit-liter', 'Liter', 'L'),
  ('unit-milliliter', 'Milliliter', 'mL'),
  ('unit-cup', 'Cup', 'cup'),
  ('unit-tbsp', 'Tablespoon', 'tbsp'),
  ('unit-tsp', 'Teaspoon', 'tsp');

INSERT OR IGNORE INTO "Season" (id, name) VALUES
  ('season-winter', 'Winter'),
  ('season-spring', 'Spring'),
  ('season-summer', 'Summer'),
  ('season-fall', 'Fall');
