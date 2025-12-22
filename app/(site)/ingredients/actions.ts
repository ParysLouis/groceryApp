'use server';

import { revalidatePath } from 'next/cache';
import { prisma } from '@/lib/prisma';
import { ingredientSchema } from '@/lib/validation';

export async function createIngredient(values: unknown) {
  const parsed = ingredientSchema.safeParse(values);
  if (!parsed.success) {
    return { success: false, error: parsed.error.flatten().fieldErrors };
  }

  const { name, defaultAisleId, unitId, seasonIds } = parsed.data;

  try {
    await prisma.ingredient.create({
      data: {
        name,
        defaultAisleId,
        unitId,
        seasons: {
          create: seasonIds?.map((seasonId) => ({ seasonId }))
        }
      }
    });
  } catch (error) {
    console.error('Failed to create ingredient', error);
    return { success: false, error: { name: ['Name must be unique'] } };
  }

  revalidatePath('/ingredients');
  return { success: true };
}
