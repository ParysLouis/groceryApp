import unittest

from services.consolidation import ShoppingItem, consolidate_items, group_by_aisle


class ConsolidationTests(unittest.TestCase):
    def test_consolidates_matching_items(self):
        items = [
            ShoppingItem(
                ingredient_name="Tomato",
                aisle_name="Produce",
                aisle_order=1,
                unit="pc",
                quantity=2,
                note=None,
            ),
            ShoppingItem(
                ingredient_name="Tomato",
                aisle_name="Produce",
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
                ingredient_name="Onion",
                aisle_name="Produce",
                aisle_order=1,
                unit="pc",
                quantity=1,
                note="chopped",
            ),
            ShoppingItem(
                ingredient_name="Onion",
                aisle_name="Produce",
                aisle_order=1,
                unit="pc",
                quantity=1,
                note="sliced",
            ),
        ]
        consolidated = consolidate_items(items)
        self.assertEqual(len(consolidated), 2)

    def test_groups_by_aisle(self):
        items = [
            ShoppingItem(
                ingredient_name="Milk",
                aisle_name="Dairy",
                aisle_order=2,
                unit="l",
                quantity=1,
            ),
            ShoppingItem(
                ingredient_name="Bread",
                aisle_name="Bakery",
                aisle_order=1,
                unit="pc",
                quantity=1,
            ),
        ]
        consolidated = consolidate_items(items)
        grouped = group_by_aisle(consolidated)
        self.assertEqual(grouped[0][0], "Bakery")
        self.assertEqual(grouped[1][0], "Dairy")


if __name__ == "__main__":
    unittest.main()
