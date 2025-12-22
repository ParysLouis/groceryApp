import { consolidateShoppingList, ShoppingListLine } from '@/lib/shoppingList';

describe('consolidateShoppingList', () => {
  it('groups by ingredient and note', () => {
    const lines: ShoppingListLine[] = [
      { ingredientId: 'a', ingredientName: 'Apples', aisleName: 'Produce', quantity: 1 },
      { ingredientId: 'a', ingredientName: 'Apples', aisleName: 'Produce', quantity: 2 },
      { ingredientId: 'b', ingredientName: 'Beans', aisleName: 'Pantry', quantity: 3, note: 'canned' },
      { ingredientId: 'b', ingredientName: 'Beans', aisleName: 'Pantry', quantity: 1, note: 'fresh' }
    ];

    const consolidated = consolidateShoppingList(lines);

    expect(consolidated).toHaveLength(3);
    expect(consolidated.find((l) => l.ingredientId === 'a')?.quantity).toBe(3);
    const canned = consolidated.find((l) => l.note === 'canned');
    const fresh = consolidated.find((l) => l.note === 'fresh');
    expect(canned?.quantity).toBe(3);
    expect(fresh?.quantity).toBe(1);
  });
});
