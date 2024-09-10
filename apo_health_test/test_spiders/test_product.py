import json
import unittest
from scrapy.utils.test import get_crawler
from scrapy.http import Request, Response, HtmlResponse
from apo_health.spiders.product import ProductSpider


class TestProduct(unittest.TestCase):
    def setUp(self):
        self.crawler = get_crawler(ProductSpider)
        self.spider = self.crawler._create_spider()

    # check unavailable product
    def test_unavailable_product(self):
        url = "https://www.apo-health.com/products/ketoconazol-klinge-20-mgg-shampoo-60-ml-sha"
        body = None
        with open(
            "apo_health_test/pages/ketoconazol-klinge-20-mgg-shampoo-60-ml-sha.html", "rb"
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
            "existence": False,
            "date": "2024-08-24T15:09:53",
            "url": "https://www.apo-health.com/products/ketoconazol-klinge-20-mgg-shampoo-60-ml-sha",
            "source": "www_apo-health_com",
            "product_id": "4150173900860",
            "sku": "J-17390086",
            "upc": None,
            "available_qty": None,
            "returnable": False,
            "title": "Ketoconazol Klinge 20 mg/g Shampoo, 60 ml SHA",
            "images": "https://www.apo-health.com/cdn/shop/files/Bild_folgt_apohealth_Gesundheit_aus_der_Apotheke_0f0eb96c-a780-4831-b025-2ced5656decf.jpg?v=1724496800",
        }

        keys = ["existence", "product_id", "sku", "url", "images", "available_qty"]
        for key in keys:
            self.assertEqual(product[key], target_product[key])

    # check available product
    def test_available_product_v1(self):
        url = "https://www.apo-health.com/collections/all/products/hydrocortison-ratiopharm-05-creme-15-g-creme"
        body = None
        with open(
            "apo_health_test/pages/hydrocortison-ratiopharm-05-creme-15-g-creme.html",
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
            "source": "apo_health",
            "existence": True,
            "date": "2024-08-24T15:01:32",
            "url": "https://www.apo-health.com/collections/all/products/hydrocortison-ratiopharm-05-creme-15-g-creme",
            "product_id": "4150097032982",
            "sku": "J-09703298",
            "upc": None,
            "returnable": False,
            "weight": None,
            "width": None,
            "height": None,
            "length": None,
            "title": "Hydrocortison-ratiopharm 0,5 % Creme, 15 g Creme",
            "title_en": None,
            "brand": "ratiopharm",
            "available_qty": None,
            "price": 8.23,
            "price_compare": 8.94,
            "images": "https://www.apo-health.com/cdn/shop/files/09703298_01_ba537b32-6be5-46cc-9549-aa58355bf3a7.jpg?v=1724473352;https://www.apo-health.com/cdn/shop/files/40736c4e3065fb5022b8d3e8508f8507_e3845ebf-2a30-4411-ab52-33d15e885a75.jpg?v=1724473352;https://www.apo-health.com/cdn/shop/files/09703298_03_e7bc5aba-304b-4e4b-bdf7-ca0544ea9644.jpg?v=1724473352;https://www.apo-health.com/cdn/shop/files/09703298_04_6ff660c4-59e7-421c-b4a0-644d23a1e030.jpg?v=1724473352;https://www.apo-health.com/cdn/shop/files/09703298_05_ae7f04c5-03c2-4407-9ee8-b8a399ee05be.jpg?v=1724473352;https://www.apo-health.com/cdn/shop/files/09703298_08_d2c7e54c-477b-49e7-b525-b88e1eda3bac.jpg?v=1724473352",
            "summary": None,
            "description_en": None,
            "shipping_days_min": 6,
            "shipping_days_max": 9,
            "shipping_fee": 6.14,
            "videos": None,
            "categories": "Alle Artikel",
            "specifications": [
                {"name": "Packungsgröße", "value": "15 g"},
                {"name": "Darreichungsform", "value": "Creme"},
                {"name": "Inhaltsstoffe", "value": "Hydrocortison"},
            ],
            "reviews": None,
            "rating": None,
            "options": None,
            "variants": None,
            "has_only_default_variant": True,
            "sold_count": None,
        }

        keys = [
            "existence",
            "product_id",
            "sku",
            "url",
            "existence",
            "brand",
            "product_id",
            "title",
            "shipping_fee",
            "specifications",
            "images",
            "price",
            "categories",
            "options",
            "has_only_default_variant",
            "available_qty",
        ]
        for key in keys:
            self.assertEqual(product[key], target_product[key])

    # check available product
    def test_available_product_v2(self):
        url = "https://www.apo-health.com/collections/all/products/plantur-39-coffein-shampoo-color-250-ml-sha"
        body = None
        with open(
            "apo_health_test/pages/plantur-39-coffein-shampoo-color-250-ml-sha.html",
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
            "existence": False,
            "date": "2024-08-24T15:33:55",
            "url": "https://www.apo-health.com/collections/all/products/plantur-39-coffein-shampoo-color-250-ml-sha",
            "source": "apo_health",
            "product_id": "04008666700902",
            "sku": "J-05567533",
            "upc": None,
            "returnable": False,
            "weight": None,
            "width": None,
            "height": None,
            "length": None,
            "title": "Plantur 39 Coffein-Shampoo Color, 250 ml SHA",
            "title_en": None,
            "brand": "Nicht vorhanden",
            "available_qty": 0,
            "price": 19.16,
            "price_compare": None,
            "images": "https://www.apo-health.com/cdn/shop/files/05567533_01.jpg?v=1724459641;https://www.apo-health.com/cdn/shop/files/05567533_02.jpg?v=1724459641;https://www.apo-health.com/cdn/shop/files/05567533_03.jpg?v=1724459641;https://www.apo-health.com/cdn/shop/files/05567533_04.jpg?v=1724459641;https://www.apo-health.com/cdn/shop/files/05567533_05.jpg?v=1724459641;https://www.apo-health.com/cdn/shop/files/05567533_08.jpg?v=1724459641",
            "summary": '<li class="active"> <p></p> <ul>\n<li>Hersteller: Dr. Kurt Wolff GmbH &amp; Co. KG (Originalprodukt aus Deutschland)</li> <li>PZN: 05567533</li> </ul>\n<br>  <br> <br> </li>',
            "description": '<ul class="tabs"> <li class="active">Übersicht</li> <li>Details</li> <li>Inhalt</li> </ul> <ul class="tabs-content"> <li class="active"> <p></p> <ul>\n<li>Hersteller: Dr. Kurt Wolff GmbH &amp; Co. KG (Originalprodukt aus Deutschland)</li> <li>PZN: 05567533</li> </ul>\n<br>  <br> <br> </li> <li> <p>PZN: 5567533 <br><br>Produkteigenschaften:<br><br>- Das Phyto-Coffein-Shampoo für coloriertes und strapaziertes Haar repariert und schützt die beanspruchte Haarstruktur<br>- Die Struktur wird geglättet und das Haar erhält einen intensiven Glanz<br><br>Die Haarwurzel der Frau ist bis zur Menopause (Wechseljahre) durch einen hohen Anteil weiblicher Hormone (Östrogen) geschützt. Danach sinkt dieser Anteil und der Einfluss der männlichen Hormone nimmt zu. Die Folge: Das Haar wird dünner, fällt vorzeitig aus, die Kopfhaut wird sichtbar. Das Coffein, in den Plantur 39 Phyto-Coffein-Shampoos beugt der hormon\xadbedingten Erschöpfung der Haarproduktion vor. Der Wirkstoff dringt schon bei der Haarwäsche bis in den Haarfollikel vor (nach 120 Sek. Einwirkzeit nachweisbar).<br><br>Inhaltsstoffe:<br>- Der Phyto-Coffein-Complex aktiviert die Haarwurzel, verlängert die Wachstumsphase und verbessert das Haarwachstum<br>- Der weiße Tee-Extrakt verbessert die Widerstandskraft<br>- Milde Aminosäure-Tenside schonen Kopfhaut und Haarwurzeln<br>- Das Weizenprotein gibt trockenem porösem Haar wieder Festigkeit<br>- Provitamin B5 macht das Haar voller und geschmeidiger<br><br>Aqua, Sodium Laureth Sulfate, Cocamidopropyl Betaine, Sodium Chloride, Glycerin, Propylene Glycol, Panthenol, Caffeine, Glyceryl Oleate, Coco-Glucoside, Parfum, Polyquaternium-7, Sodium Citrate, Citric Acid, Potassium Sorbate, Polyquaternium-10, Hydrolyzed Wheat Protein, Camellia Sinensis Extract, Hexyl Cinnamal, Sodium Benzoate, Zinc PCA, Niacinamide, Limonene, Linalool, Phenoxyethanol, Methylparaben, Propylparaben, CI 47005, CI 42090<br><br>Quelle: www.dr-wolff-shop.de<br>Stand: 08/2015</p> </li> <li>\n<p></p>\n<ul>\n<li>Packungsgröße: 250 ml</li>\n<li>Darreichungsform: SHA</li>\n<li>Inhaltsstoffe: </li>\n</ul>\n</li> </ul>',
            "description_en": None,
            "shipping_days_min": 6,
            "shipping_days_max": 9,
            "shipping_fee": 6.14,
            "videos": None,
            "categories": "Alle Artikel",
            "specifications": [
                {"name": "Packungsgröße", "value": "250 ml"},
                {"name": "Darreichungsform", "value": "SHA"},
                {"name": "Inhaltsstoffe", "value": ""},
            ],
            "reviews": None,
            "rating": None,
            "options": None,
            "variants": None,
            "has_only_default_variant": True,
            "sold_count": None,
        }

        keys = [
            "existence",
            "product_id",
            "sku",
            "url",
            "existence",
            "brand",
            "product_id",
            "title",
            "shipping_fee",
            "specifications",
            "images",
            "price",
            "categories",
            "options",
            "has_only_default_variant",
            "available_qty",
        ]
        for key in keys:
            self.assertEqual(product[key], target_product[key])

    def test_available_product_v3(self):
        url = "https://www.apo-health.com/collections/all/products/vitamin-b-complete-hevert-all-in-one-60-st-kapseln-hevert-testen-apoteams.html"
        body = None
        with open(
            "apo_health_test/pages/vitamin-b-complete-hevert-all-in-one-60-st-kapseln-hevert-testen-apoteams.html",
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
            "existence": True,
            "date": "2024-09-03T15:11:00",
            "url": "https://www.apo-health.com/collections/all/products/vitamin-b-complete-hevert-all-in-one-60-st-kapseln-hevert-testen-apoteams.html",
            "source": "www_apo-health_com",
            "product_id": "8715891310859",
            "sku": "J-19214749",
            "upc": None,
            "returnable": False,
            "weight": None,
            "width": None,
            "height": None,
            "length": None,
            "title": "Vitamin B Complete Hevert All-in-One, 60 St. Kapseln",
            "title_en": None,
            "brand": "Hevert Apoteam",
            "available_qty": None,
            "price": 16.3,
            "price_compare": None,
            "images": "https://www.apo-health.com/cdn/shop/files/19214749.png?v=1720447384",
            "summary": "Vitamin B Complete Hevert All-in-One, 60 St. Kapseln, Hevert Apoteam",
            "description_en": None,
            "shipping_days_min": 6,
            "shipping_days_max": 9,
            "shipping_fee": 6.14,
            "videos": None,
            "categories": "",
            "specifications": None,
            "reviews": None,
            "rating": None,
            "options": None,
            "variants": None,
            "has_only_default_variant": True,
            "sold_count": None,
        }

        keys = [
            "existence",
            "product_id",
            "sku",
            "url",
            "existence",
            "brand",
            "product_id",
            "title",
            "shipping_fee",
            "specifications",
            "images",
            "price",
            "categories",
            "options",
            "has_only_default_variant",
            "available_qty",
        ]
        for key in keys:
            self.assertEqual(product[key], target_product[key])


if __name__ == "__main__":
    unittest.main()
