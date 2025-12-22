# Repository file overview

This document summarizes the purpose of each tracked file in the project so newcomers can quickly understand where logic lives.

## Root
- `README.md`: High-level project summary, tech stack, and quick-start notes.
- `package.json`: npm metadata and scripts for development, testing, Prisma, and building the Next.js app.
- `tsconfig.json`: TypeScript configuration with strict settings and path alias support for `@/*`.
- `tailwind.config.ts`: Tailwind CSS content scanning paths and theme extension hook.
- `postcss.config.js`: PostCSS pipeline configuration used by Tailwind (default Next.js setup).
- `next.config.mjs`: Next.js config enabling Partial Prerendering (`ppr`).
- `vitest.config.ts`: Vitest test runner configuration.
- `next-env.d.ts`: Generated ambient Next.js/TypeScript types (do not edit manually).
- `package-lock.json` (if present locally): Locked dependency tree produced by npm install.

## Application (`app/`)
- `app/layout.tsx`: Root layout defining HTML shell, global nav, and metadata (manifest/theme color) and mounting the service-worker registration helper.
- `app/globals.css`: Global styles and Tailwind directives, including base typography and container width.
- `app/page.tsx`: Landing page with feature highlights and links into the ingredients and recipes sections.
- `app/(site)/ingredients/page.tsx`: Server component that loads ingredients, aisles, units, and seasons from Prisma and renders the catalog plus the ingredient creation form.
- `app/(site)/ingredients/actions.ts`: Server action that validates and saves new ingredients, revalidating the ingredients route on success.
- `app/(site)/recipes/page.tsx`: Server component that lists recipes (with seasons and ingredients) and hosts the recipe creation form.
- `app/(site)/recipes/actions.ts`: Server action to validate and persist a new recipe and its ingredient rows, then revalidate the recipes page.
- `app/(site)/shopping-list/page.tsx`: Placeholder shopping-list page with guidance on preparing catalog data.

## Components (`components/`)
- `ServiceWorkerRegister.tsx`: Client component that registers `public/sw.js` when the app loads.
- `IngredientForm.tsx`: Client-side form for creating ingredients using React Hook Form, Zod validation, and the server action.
- `RecipeForm.tsx`: Client-side recipe form with dynamic ingredient rows, validation, and submit handling via server action.

## Library utilities (`lib/`)
- `prisma.ts`: Singleton Prisma client instantiation safe for dev hot-reload.
- `validation.ts`: Zod schemas for validating ingredient and recipe payloads (shared by client forms and server actions).
- `shoppingList.ts`: Helper to consolidate shopping-list lines by ingredient+note and sort by aisle.

## Database (`prisma/`)
- `schema.prisma`: Prisma data model defining aisles, units, seasons, ingredients, recipes, and their relations (SQLite datasource).
- `seed.ts`: Script that seeds default aisles, units, and seasons into the SQLite database.

## Public assets (`public/`)
- `manifest.webmanifest`: PWA manifest (name, colors, icon reference, start URL).
- `icon.svg`: App icon referenced by the manifest.
- `sw.js`: Service worker that claims clients immediately and leaves fetch handling to the network/HTTP cache.

## Scripts (`scripts/`)
- `launch-linux.sh`, `launch-mac.sh`, `launch-windows.ps1`: One-command launchers that install dependencies if missing, start the dev server, and open the browser on the appropriate platform.

## Tests (`tests/`)
- `shoppingList.test.ts`: Vitest coverage for shopping-list consolidation logic.

## Configuration helpers
- `postcss.config.js`, `vitest.config.ts`: Build/test tooling configs referenced by npm scripts.
