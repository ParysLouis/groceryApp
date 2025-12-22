import Link from 'next/link';

const features = [
  {
    title: 'Ingredients catalog',
    body: 'Seeded aisles, units, and seasons keep your pantry organized from the start.'
  },
  {
    title: 'Recipes',
    body: 'Capture prep time, sources, and ingredient details with form-first flows.'
  },
  {
    title: 'Shopping list',
    body: 'Filter recipes by season or cook time and generate a consolidated list grouped by aisle.'
  },
  {
    title: 'PWA ready',
    body: 'Install locally and work offline with service worker caching and manifest metadata.'
  }
];

export default function HomePage() {
  return (
    <div className="space-y-8">
      <section className="rounded-xl bg-white p-8 shadow-sm">
        <h1 className="text-3xl font-semibold text-emerald-700">Local-first grocery planner</h1>
        <p className="mt-4 max-w-3xl text-lg text-slate-700">
          This app helps you manage seasonal recipes and build smart shopping lists grouped by aisle.
          Start with the seeded catalog and customize aisles, units, and seasons to fit your store.
        </p>
        <div className="mt-6 flex flex-wrap gap-4">
          <Link className="rounded-full bg-emerald-600 px-6 py-3 text-sm font-medium text-white" href="/ingredients">
            Go to ingredients
          </Link>
          <Link className="rounded-full border border-emerald-200 px-6 py-3 text-sm font-medium text-emerald-700" href="/recipes">
            Go to recipes
          </Link>
        </div>
      </section>

      <section className="grid gap-4 md:grid-cols-2">
        {features.map((feature) => (
          <div key={feature.title} className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
            <h2 className="text-lg font-semibold text-emerald-700">{feature.title}</h2>
            <p className="mt-2 text-sm text-slate-700">{feature.body}</p>
          </div>
        ))}
      </section>
    </div>
  );
}
