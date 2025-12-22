'use server';

import { revalidatePath } from 'next/cache';
import { prisma } from '@/lib/prisma';
import { recipeSchema } from '@/lib/validation';

export async function createRecipe(values: unknown) {
  const parsed = recipeSchema.safeParse(values);
  if (!parsed.success) {
    return { success: false, error: parsed.error.flatten().fieldErrors };
  }

  const { name, totalMinutes, sourceUrl, notes, seasonIds, ingredients } = parsed.data;

  try {
    await prisma.recipe.create({
      data: {
        name,
        totalMinutes,
        sourceUrl: sourceUrl || null,
        notes: notes || null,
        seasons: {
          create: seasonIds?.map((seasonId) => ({ seasonId }))
        },
        ingredients: {
          create: ingredients.map((ingredient) => ({
            ingredientId: ingredient.ingredientId,
            quantity: ingredient.quantity,
            note: ingredient.note || null
          }))
        }
      }
    });
  } catch (error) {
    console.error('Failed to create recipe', error);
    return { success: false, error: { name: ['Unable to save recipe'] } };
  }

  revalidatePath('/recipes');
  return { success: true };
}
