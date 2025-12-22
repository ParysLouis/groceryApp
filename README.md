# Grocery Planner (Next.js)

A local-first, installable grocery planning app built with **Next.js (App Router)**, **TypeScript**, **Prisma**, and **SQLite**. Seeded aisles, units, and seasons let you capture ingredients and recipes immediately, with shopping-list consolidation and offline export planned for the next milestone.

## Tech stack
- Next.js 14 (App Router) + React 18 + TypeScript
- Tailwind CSS for styling
- Prisma ORM with SQLite (cuid IDs)
- Zod + React Hook Form for validation
- Vitest for unit tests
- PWA manifest + service worker for installability

## Getting started
Prerequisites: Node.js 20+ and npm.

```bash
npm install
npm run dev
```
Visit http://localhost:3000. The app ships with a local SQLite database at `prisma/dev.db`. Default data includes aisles, units, and seasons.

### Database
- Schema lives in [`prisma/schema.prisma`](./prisma/schema.prisma) with SQLite datasource.
- To apply the initial migration locally: `npx prisma migrate dev --name init`.
- To regenerate the Prisma client: `npm run prisma:generate`.
- To reseed the catalog: `npm run prisma:seed` (uses `prisma/seed.ts`).

Backup the database by copying `prisma/dev.db`:

```bash
cp prisma/dev.db prisma/dev-backup-$(date +%Y%m%d%H%M).db
```

### Scripts
Cross-platform launchers that install dependencies if needed and open the browser:
- Linux: `./scripts/launch-linux.sh`
- macOS: `./scripts/launch-mac.sh`
- Windows (PowerShell): `./scripts/launch-windows.ps1`

### Testing and quality
- `npm run lint` – ESLint (Next.js config)
- `npm run typecheck` – TypeScript strict check
- `npm run test` – Vitest unit tests (shopping list consolidation)

### PWA
The manifest (`public/manifest.webmanifest`) and service worker (`public/sw.js`) make the app installable. Icons are generated locally and bundled; no CDN dependencies are required.

## Roadmap
Milestone 1 (this commit) sets up the project scaffolding, Prisma schema/migrations, seed data, PWA plumbing, and basic pages for ingredients, recipes, and the shopping list shell. Future milestones will deliver full CRUD flows, list consolidation UX, and offline HTML export.
