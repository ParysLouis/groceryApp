import './globals.css';
import type { Metadata } from 'next';
import Link from 'next/link';
import { ReactNode } from 'react';
import { ServiceWorkerRegister } from '@/components/ServiceWorkerRegister';

export const metadata: Metadata = {
  title: 'Grocery Planner',
  description: 'Local-first grocery planner with recipes and shopping lists',
  manifest: '/manifest.webmanifest',
  themeColor: '#16a34a'
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body className="bg-slate-50 text-slate-900">
        <ServiceWorkerRegister />
        <header className="border-b border-slate-200 bg-white">
          <div className="container mx-auto flex items-center justify-between px-6 py-4">
            <Link href="/" className="text-xl font-semibold text-emerald-700">
              Grocery Planner
            </Link>
            <nav className="flex gap-4 text-sm font-medium">
              <Link href="/ingredients" className="hover:text-emerald-700">
                Ingredients
              </Link>
              <Link href="/recipes" className="hover:text-emerald-700">
                Recipes
              </Link>
              <Link href="/shopping-list" className="hover:text-emerald-700">
                Shopping List
              </Link>
            </nav>
          </div>
        </header>
        <main className="container mx-auto px-6 py-8">{children}</main>
      </body>
    </html>
  );
}
