import { z } from 'zod';

export const ingredientSchema = z.object({
  name: z.string().min(2, 'Name is required'),
  defaultAisleId: z.string().min(1, 'Aisle is required'),
  unitId: z.string().min(1, 'Unit is required'),
  seasonIds: z.array(z.string()).optional().default([])
});

export const recipeIngredientSchema = z.object({
  ingredientId: z.string().min(1, 'Ingredient is required'),
  quantity: z.coerce.number().positive('Quantity must be greater than zero'),
  note: z.string().optional()
});

export const recipeSchema = z.object({
  name: z.string().min(2, 'Recipe name is required'),
  totalMinutes: z.coerce.number().positive('Total minutes required'),
  sourceUrl: z.string().url().optional().or(z.literal('')),
  notes: z.string().optional(),
  seasonIds: z.array(z.string()).optional().default([]),
  ingredients: z.array(recipeIngredientSchema).default([])
});
