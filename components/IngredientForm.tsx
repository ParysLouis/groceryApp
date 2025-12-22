'use client';

import { zodResolver } from '@hookform/resolvers/zod';
import { Aisle, Season, Unit } from '@prisma/client';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { ingredientSchema } from '@/lib/validation';
import { createIngredient } from '@/app/(site)/ingredients/actions';

export type IngredientFormData = z.infer<typeof ingredientSchema>;

interface IngredientFormProps {
  aisles: Aisle[];
  units: Unit[];
  seasons: Season[];
}

export function IngredientForm({ aisles, units, seasons }: IngredientFormProps) {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    reset
  } = useForm<IngredientFormData>({
    resolver: zodResolver(ingredientSchema),
    defaultValues: {
      name: '',
      defaultAisleId: aisles[0]?.id ?? '',
      unitId: units[0]?.id ?? '',
      seasonIds: []
    }
  });

  const onSubmit = handleSubmit(async (values) => {
    const result = await createIngredient(values);
    if (result?.success) {
      reset();
    } else if (result?.error) {
      console.warn(result.error);
    }
  });

  return (
    <form onSubmit={onSubmit} className="space-y-4 rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
      <div>
        <label className="block text-sm font-medium text-slate-700">Name</label>
        <input
          className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-emerald-600 focus:outline-none"
          placeholder="e.g. Roma tomato"
          {...register('name')}
        />
        {errors.name && <p className="mt-1 text-xs text-red-600">{errors.name.message}</p>}
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <div>
          <label className="block text-sm font-medium text-slate-700">Default aisle</label>
          <select
            className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-emerald-600 focus:outline-none"
            {...register('defaultAisleId')}
          >
            {aisles.map((aisle) => (
              <option key={aisle.id} value={aisle.id}>
                {aisle.name}
              </option>
            ))}
          </select>
          {errors.defaultAisleId && (
            <p className="mt-1 text-xs text-red-600">{errors.defaultAisleId.message}</p>
          )}
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700">Unit</label>
          <select
            className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-emerald-600 focus:outline-none"
            {...register('unitId')}
          >
            {units.map((unit) => (
              <option key={unit.id} value={unit.id}>
                {unit.name} ({unit.abbreviation})
              </option>
            ))}
          </select>
          {errors.unitId && <p className="mt-1 text-xs text-red-600">{errors.unitId.message}</p>}
        </div>
      </div>

      <div>
        <span className="block text-sm font-medium text-slate-700">Seasons</span>
        <div className="mt-2 flex flex-wrap gap-3">
          {seasons.map((season) => (
            <label key={season.id} className="flex items-center gap-2 text-sm text-slate-700">
              <input type="checkbox" value={season.id} {...register('seasonIds')} />
              {season.name}
            </label>
          ))}
        </div>
      </div>

      <button
        type="submit"
        className="inline-flex items-center rounded-md bg-emerald-600 px-4 py-2 text-sm font-semibold text-white disabled:opacity-50"
        disabled={isSubmitting}
      >
        {isSubmitting ? 'Saving...' : 'Add ingredient'}
      </button>
    </form>
  );
}
