import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

const aisles = [
  'Produce',
  'Bakery',
  'Dairy',
  'Meat & Seafood',
  'Pantry',
  'Frozen',
  'Beverages',
  'Household'
].map((name, index) => ({ name, sortOrder: index + 1 }));

const units = [
  { name: 'Piece', abbreviation: 'pc' },
  { name: 'Gram', abbreviation: 'g' },
  { name: 'Kilogram', abbreviation: 'kg' },
  { name: 'Liter', abbreviation: 'L' },
  { name: 'Milliliter', abbreviation: 'mL' },
  { name: 'Cup', abbreviation: 'cup' },
  { name: 'Tablespoon', abbreviation: 'tbsp' },
  { name: 'Teaspoon', abbreviation: 'tsp' }
];

const seasons = ['Winter', 'Spring', 'Summer', 'Fall'];

async function main() {
  await prisma.aisle.createMany({ data: aisles, skipDuplicates: true });
  await prisma.unit.createMany({ data: units, skipDuplicates: true });
  await prisma.season.createMany({ data: seasons.map((name) => ({ name })), skipDuplicates: true });
}

main()
  .catch((error) => {
    console.error('Seed failed', error);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
