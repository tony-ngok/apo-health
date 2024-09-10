import unittest

from resources.filters import filters


class TestFilters(unittest.TestCase):
    def setUp(self):
        self.seeds = [
            {
                "product": {
                    "title": "LG Elastine Shampoo 4.2kg Large Capacity Commercial Home Use Fragrant Shampoo",
                },
                "result": True,
            },
            {
                "product": {
                    "title": "키즈 어린이 비타민E 루테인 꾸미 2.5g 90개입",
                },
                "result": False,
            },
        ]

    def test_filters(self):
        for seed in self.seeds:
            self.assertEqual(filters(seed["product"]), seed["result"])


if __name__ == "__main__":
    unittest.main()
