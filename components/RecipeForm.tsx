'use client';

import { zodResolver } from '@hookform/resolvers/zod';
import { Ingredient, Season } from '@prisma/client';
import { useFieldArray, useForm } from 'react-hook-form';
import { z } from 'zod';
import { recipeSchema } from '@/lib/validation';
import { createRecipe } from '@/app/(site)/recipes/actions';

export type RecipeFormData = z.infer<typeof recipeSchema>;

interface RecipeFormProps {
  ingredients: Ingredient[];
  seasons: Season[];
}

export function RecipeForm({ ingredients, seasons }: RecipeFormProps) {
  const {
    register,
    control,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting }
  } = useForm<RecipeFormData>({
    resolver: zodResolver(recipeSchema),
    defaultValues: {
      name: '',
      totalMinutes: 30,
      notes: '',
      sourceUrl: '',
      seasonIds: [],
      ingredients: [{ ingredientId: ingredients[0]?.id ?? '', quantity: 1, note: '' }]
    }
  });

  const { fields, append, remove } = useFieldArray({ control, name: 'ingredients' });

  const onSubmit = handleSubmit(async (values) => {
    const result = await createRecipe(values);
    if (result?.success) {
      reset();
    } else {
      console.warn(result?.error);
    }
  });

  return (
    <form onSubmit={onSubmit} className="space-y-6 rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
      <div className="grid gap-4 md:grid-cols-2">
        <div>
          <label className="block text-sm font-medium text-slate-700">Recipe name</label>
          <input
            className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-emerald-600 focus:outline-none"
            placeholder="Weeknight chili"
            {...register('name')}
          />
          {errors.name && <p className="mt-1 text-xs text-red-600">{errors.name.message}</p>}
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700">Total minutes</label>
          <input
            type="number"
            min={1}
            className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-emerald-600 focus:outline-none"
            {...register('totalMinutes')}
          />
          {errors.totalMinutes && (
            <p className="mt-1 text-xs text-red-600">{errors.totalMinutes.message}</p>
          )}
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <div>
          <label className="block text-sm font-medium text-slate-700">Source URL (optional)</label>
          <input
            className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-emerald-600 focus:outline-none"
            placeholder="https://example.com"
            {...register('sourceUrl')}
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700">Seasons</label>
          <div className="mt-2 flex flex-wrap gap-3">
            {seasons.map((season) => (
              <label key={season.id} className="flex items-center gap-2 text-sm text-slate-700">
                <input type="checkbox" value={season.id} {...register('seasonIds')} />
                {season.name}
              </label>
            ))}
          </div>
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-slate-700">Notes</label>
        <textarea
          rows={3}
          className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-emerald-600 focus:outline-none"
          placeholder="Add prep notes or timing guidance"
          {...register('notes')}
        />
      </div>

      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-semibold text-slate-800">Ingredients</h3>
          <button
            type="button"
            className="text-sm font-medium text-emerald-700"
            onClick={() => append({ ingredientId: ingredients[0]?.id ?? '', quantity: 1, note: '' })}
          >
            Add row
          </button>
        </div>
        {fields.map((field, index) => (
          <div key={field.id} className="grid gap-3 rounded-md border border-slate-200 p-3 md:grid-cols-[2fr_1fr_80px]">
            <div>
              <select
                className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-emerald-600 focus:outline-none"
                {...register(`ingredients.${index}.ingredientId` as const)}
              >
                {ingredients.map((ingredient) => (
                  <option key={ingredient.id} value={ingredient.id}>
                    {ingredient.name}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <input
                type="number"
                min={0}
                step="0.25"
                className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-emerald-600 focus:outline-none"
                {...register(`ingredients.${index}.quantity` as const)}
              />
            </div>
            <div className="flex items-center gap-2">
              <input
                className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-emerald-600 focus:outline-none"
                placeholder="Note"
                {...register(`ingredients.${index}.note` as const)}
              />
              <button
                type="button"
                className="text-xs font-semibold text-red-600"
                onClick={() => remove(index)}
              >
                Remove
              </button>
            </div>
          </div>
        ))}
      </div>

      <button
        type="submit"
        className="inline-flex items-center rounded-md bg-emerald-600 px-4 py-2 text-sm font-semibold text-white disabled:opacity-50"
        disabled={isSubmitting}
      >
        {isSubmitting ? 'Saving...' : 'Add recipe'}
      </button>
    </form>
  );
}
