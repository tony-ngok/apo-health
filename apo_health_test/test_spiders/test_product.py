import unittest
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from scrapy.http import HtmlResponse
from scrapy.utils.test import get_crawler
from apo_health.spiders.product import ProductSpider


class TestProduct(unittest.TestCase):
    def setUp(self):
        self.crawler = get_crawler(ProductSpider)
        self.spider = self.crawler._create_spider()

    # check available product
    def test_available_product(self):
        url = "https://www.apo-health.com/collections/schmerzmittel-zur-anwendung-auf-der-haut/products/voltaren-schmerzgel-100-g-gel"
        body = None
        with open(
            "apo_health_test/pages/voltaren-schmerzgel-100-g-gel.html",
            "rb",
        ) as file:
            body = file.read()
        response = HtmlResponse(
            url=url,
            body=body,
        )
        result = list(self.spider.parse(response))
        self.assertEqual(len(result), 1)
        product = result[0]
        target_product = {
            "url": "https://www.apo-health.com/collections/schmerzmittel-zur-anwendung-auf-der-haut/products/voltaren-schmerzgel-100-g-gel",
            "product_id": "4797994500159",
            "existence": True,
            "title": "Voltaren Schmerzgel, 100 g Gel",
            "sku": "J-12732027",
            "upc": "4150127320270",
            "brand": "Voltaren",
            "categories": "Schmerzmittel zur Anwendung auf der Haut",
            "images": "https://www.apo-health.com/cdn/shop/files/12732027_01_e63710fa-85a3-4437-9a15-4cb2930bf8d6.jpg;https://www.apo-health.com/cdn/shop/files/12732027_02_07a42423-574d-4496-8e35-27c1cd191e66.jpg;https://www.apo-health.com/cdn/shop/files/12732027_03_68dc0c09-c8c2-4547-8bbf-b22a16d26847.jpg;https://www.apo-health.com/cdn/shop/files/12732027_04_610a20d7-8df1-4cbf-badf-85428911fbee.jpg;https://www.apo-health.com/cdn/shop/files/12732027_05_c6824723-133b-44fb-b6e1-3e62975a4968.jpg;https://www.apo-health.com/cdn/shop/files/12732027_08_6fcfbc59-7f32-47e0-b9d4-dd2c817a86c6.jpg",
            "price": 15.97,
            "available_qty": None,
            "weight": 0.32
        }

        for key in target_product:
            self.assertEqual(product[key], target_product[key])

    # check unavailable product
    def test_unavailable_product(self):
        url = "https://www.apo-health.com/collections/mittel-gegen-schmerzen/products/diclac-dolo-25-mg-20-st-tabletten"
        body = None
        with open(
            "apo_health_test/pages/diclac-dolo-25-mg-20-st-tabletten.html", "rb"
        ) as file:
            body = file.read()

        response = HtmlResponse(
            url=url,
            body=body,
        )
        result = list(self.spider.parse(response))
        self.assertEqual(len(result), 1)
        product = result[0]
        target_product = {
            "url": "https://www.apo-health.com/collections/mittel-gegen-schmerzen/products/diclac-dolo-25-mg-20-st-tabletten",
            "product_id": "4702435704895",
            "existence": False,
            "title": "Diclac Dolo 25 mg, 20 St. Tabletten",
            "sku": "J-01235521",
            "upc": "4150012355219",
            "brand": "HEXAL",
            "categories": "Mittel gegen Schmerzen",
            "images": "https://www.apo-health.com/cdn/shop/files/ae40996922314460ef100d9f4552fd23.jpg;https://www.apo-health.com/cdn/shop/files/b26b8753b934b0f6188e09323b12c4dd.jpg;https://www.apo-health.com/cdn/shop/files/d9a0f5ec0848e6ce89b44d6f2ca171b8.jpg",
            "price": 12.16,
            "available_qty": 0,
            "weight": 0.04
        }

        for key in target_product:
            self.assertEqual(product[key], target_product[key])


if __name__ == "__main__":
    unittest.main()
