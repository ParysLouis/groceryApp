import unittest

from services.consolidation import ShoppingItem, consolidate_items, group_by_aisle


class ConsolidationTests(unittest.TestCase):
    def test_consolidates_matching_items(self):
        items = [
            ShoppingItem(
                ingredient_name="Tomate",
                aisle_name="Fruits et légumes",
                aisle_order=1,
                unit="pc",
                quantity=2,
                note=None,
            ),
            ShoppingItem(
                ingredient_name="Tomate",
                aisle_name="Fruits et légumes",
                aisle_order=1,
                unit="pc",
                quantity=3,
                note=None,
            ),
        ]
        consolidated = consolidate_items(items)
        self.assertEqual(len(consolidated), 1)
        self.assertEqual(consolidated[0].quantity, 5)

    def test_splits_by_note(self):
        items = [
            ShoppingItem(
                ingredient_name="Oignon",
                aisle_name="Fruits et légumes",
                aisle_order=1,
                unit="pc",
                quantity=1,
                note="haché",
            ),
            ShoppingItem(
                ingredient_name="Oignon",
                aisle_name="Fruits et légumes",
                aisle_order=1,
                unit="pc",
                quantity=1,
                note="émincé",
            ),
        ]
        consolidated = consolidate_items(items)
        self.assertEqual(len(consolidated), 2)

    def test_groups_by_aisle(self):
        items = [
            ShoppingItem(
                ingredient_name="Lait",
                aisle_name="Produits laitiers et œufs",
                aisle_order=2,
                unit="l",
                quantity=1,
            ),
            ShoppingItem(
                ingredient_name="Pain",
                aisle_name="Boulangerie",
                aisle_order=1,
                unit="pc",
                quantity=1,
            ),
        ]
        consolidated = consolidate_items(items)
        grouped = group_by_aisle(consolidated)
        self.assertEqual(grouped[0][0], "Boulangerie")
        self.assertEqual(grouped[1][0], "Produits laitiers et œufs")


if __name__ == "__main__":
    unittest.main()
