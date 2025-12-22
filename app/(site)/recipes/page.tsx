import { prisma } from '@/lib/prisma';
import { RecipeForm } from '@/components/RecipeForm';

async function getRecipeData() {
  const [recipes, ingredients, seasons] = await Promise.all([
    prisma.recipe.findMany({
      include: {
        seasons: { include: { season: true } },
        ingredients: { include: { ingredient: true } }
      },
      orderBy: { name: 'asc' }
    }),
    prisma.ingredient.findMany({ orderBy: { name: 'asc' } }),
    prisma.season.findMany({ orderBy: { name: 'asc' } })
  ]);
  return { recipes, ingredients, seasons };
}

export default async function RecipesPage() {
  const { recipes, ingredients, seasons } = await getRecipeData();

  return (
    <div className="space-y-6">
      <div className="flex items-baseline justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-emerald-700">Recipes</h1>
          <p className="text-sm text-slate-700">Capture timing, sources, and ingredients to build lists later.</p>
        </div>
        <p className="text-sm text-slate-600">{recipes.length} recipes</p>
      </div>

      <RecipeForm ingredients={ingredients} seasons={seasons} />

      <section className="rounded-lg border border-slate-200 bg-white shadow-sm">
        <div className="border-b border-slate-200 px-6 py-3 text-sm font-semibold text-slate-700">Saved recipes</div>
        <ul className="divide-y divide-slate-100">
          {recipes.map((recipe) => (
            <li key={recipe.id} className="px-6 py-4 text-sm text-slate-800">
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium">{recipe.name}</p>
                  <p className="text-xs text-slate-600">{recipe.totalMinutes} minutes</p>
                  {recipe.sourceUrl && (
                    <a
                      href={recipe.sourceUrl}
                      target="_blank"
                      rel="noreferrer"
                      className="text-xs text-emerald-700"
                    >
                      Source
                    </a>
                  )}
                </div>
                {recipe.seasons.length > 0 && (
                  <div className="flex flex-wrap gap-2 text-xs text-emerald-700">
                    {recipe.seasons.map((s) => (
                      <span key={s.seasonId} className="rounded-full bg-emerald-50 px-3 py-1">
                        {s.season.name}
                      </span>
                    ))}
                  </div>
                )}
              </div>
              {recipe.ingredients.length > 0 && (
                <ul className="mt-3 grid gap-1 text-xs text-slate-700 md:grid-cols-2">
                  {recipe.ingredients.map((item) => (
                    <li key={item.id}>
                      {item.quantity} × {item.ingredient.name}
                      {item.note ? ` (${item.note})` : ''}
                    </li>
                  ))}
                </ul>
              )}
            </li>
          ))}
          {recipes.length === 0 && (
            <li className="px-6 py-6 text-sm text-slate-600">Add a recipe to build your shopping list.</li>
          )}
        </ul>
      </section>
    </div>
  );
}
