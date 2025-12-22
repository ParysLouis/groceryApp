import Link from 'next/link';

export default function ShoppingListPage() {
  return (
    <div className="space-y-6">
      <header className="space-y-2">
        <h1 className="text-2xl font-semibold text-emerald-700">Shopping list builder</h1>
        <p className="text-sm text-slate-700">
          Milestone 1 sets up the groundwork. Upcoming milestones will add recipe filters, list editing, and
          offline export to HTML.
        </p>
      </header>

      <div className="rounded-lg border border-dashed border-emerald-300 bg-white/60 p-6 text-sm text-slate-700">
        <p>
          Use the <Link href="/recipes" className="text-emerald-700 underline">Recipes</Link> and{' '}
          <Link href="/ingredients" className="text-emerald-700 underline">Ingredients</Link> sections to seed
          your catalog. The shopping list builder will use those entries to consolidate items by aisle.
        </p>
      </div>
    </div>
  );
}
