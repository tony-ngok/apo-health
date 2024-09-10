# https://docs.python.org/zh-cn/3/library/unittest.html

import unittest

from utils.price_calculator import PriceCalculator


class TestPriceCalculator(unittest.TestCase):
    def setUp(self) -> None:
        self.price_calc1 = PriceCalculator(min_profit_amount=15, default_qty=20)
        self.price_calc2 = PriceCalculator(
            price_rules={"roi": 0.7, "ad_cost": 2, "transfer_cost": 0.5, "tax_rate": 0.15}
        )

        self.src_offer1 = {"currency": "EUR", "price": 29.99}

        self.src_offer2 = {"currency": "JPY", "price": 630}

    def test_calc_cost_v1(self):
        cost1 = self.price_calc1.calc_cost(self.src_offer1)
        self.assertEqual(cost1, 35.64)

    def test_calc_cost_v2(self):
        cost2 = self.price_calc2.calc_cost(self.src_offer2)
        self.assertEqual(cost2, 5.60)

    def test_calc_offer_v1(self):
        offer1 = self.price_calc1.calc_offer(self.src_offer1)
        self.assertEqual(offer1["price"], 75.50)

    def test_calc_offer_v2(self):
        offer2 = self.price_calc2.calc_offer(self.src_offer2)
        self.assertEqual(offer2["price"], 16.10)

    def test_calc_profit_v1(self):
        profit1 = self.price_calc1.calc_profit(self.src_offer1)
        self.assertEqual(profit1, 33.25)

    def test_calc_profit_v2(self):
        profit2 = self.price_calc2.calc_profit(self.src_offer2)
        self.assertEqual(profit2, 9.09)

    def test_calc_profit_rate_v1(self):
        profit_rate1 = self.price_calc1.calc_profit_rate(self.src_offer1)
        self.assertAlmostEqual(profit_rate1, 44.04, places=1)

    def test_calc_profit_rate_v2(self):
        profit_rate2 = self.price_calc2.calc_profit_rate(self.src_offer2)
        self.assertAlmostEqual(profit_rate2, 56.46, places=1)


if __name__ == "__main__":
    unittest.main()
