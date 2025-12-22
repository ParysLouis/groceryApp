export type ShoppingListLine = {
  ingredientId: string;
  ingredientName: string;
  aisleName: string;
  quantity: number;
  note?: string | null;
};

export function consolidateShoppingList(lines: ShoppingListLine[]) {
  const keyFor = (line: ShoppingListLine) => `${line.ingredientId}::${line.note ?? ''}`;

  const grouped = new Map<string, ShoppingListLine>();

  for (const line of lines) {
    const key = keyFor(line);
    const existing = grouped.get(key);
    if (existing) {
      existing.quantity += line.quantity;
    } else {
      grouped.set(key, { ...line });
    }
  }

  return Array.from(grouped.values()).sort((a, b) => a.aisleName.localeCompare(b.aisleName));
}
