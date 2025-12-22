import { prisma } from '@/lib/prisma';
import { IngredientForm } from '@/components/IngredientForm';

async function getIngredientData() {
  const [ingredients, aisles, units, seasons] = await Promise.all([
    prisma.ingredient.findMany({ include: { defaultAisle: true, unit: true, seasons: { include: { season: true } } } }),
    prisma.aisle.findMany({ orderBy: { sortOrder: 'asc' } }),
    prisma.unit.findMany({ orderBy: { name: 'asc' } }),
    prisma.season.findMany({ orderBy: { name: 'asc' } })
  ]);

  return { ingredients, aisles, units, seasons };
}

export default async function IngredientsPage() {
  const { ingredients, aisles, units, seasons } = await getIngredientData();

  return (
    <div className="space-y-6">
      <div className="flex items-baseline justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-emerald-700">Ingredients</h1>
          <p className="text-sm text-slate-700">Seeded aisles, units, and seasons are ready to use.</p>
        </div>
        <p className="text-sm text-slate-600">{ingredients.length} ingredients</p>
      </div>

      <IngredientForm aisles={aisles} units={units} seasons={seasons} />

      <section className="rounded-lg border border-slate-200 bg-white shadow-sm">
        <div className="border-b border-slate-200 px-6 py-3 text-sm font-semibold text-slate-700">Catalog</div>
        <ul className="divide-y divide-slate-100">
          {ingredients.map((ingredient) => (
            <li key={ingredient.id} className="px-6 py-3 text-sm text-slate-800">
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium">{ingredient.name}</p>
                  <p className="text-xs text-slate-600">
                    {ingredient.defaultAisle.name} · {ingredient.unit.name}
                  </p>
                </div>
                {ingredient.seasons.length > 0 && (
                  <div className="flex flex-wrap gap-2 text-xs text-emerald-700">
                    {ingredient.seasons.map((s) => (
                      <span key={s.seasonId} className="rounded-full bg-emerald-50 px-3 py-1">
                        {s.season.name}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            </li>
          ))}
          {ingredients.length === 0 && (
            <li className="px-6 py-6 text-sm text-slate-600">Add your first ingredient to get started.</li>
          )}
        </ul>
      </section>
    </div>
  );
}
