from datetime import datetime, timedelta
import json
from multiprocessing.pool import ThreadPool
import re

from google.oauth2 import service_account
from google.cloud.translate_v2 import Client


from wemakeprice.settings import MONGO_URI
from utils.site_product import fetch_source_ids
from utils.translate_service import get_translator

from .formatter import to_upload
from .loader import TranslationElasticSearchLoder
from wemakeprice.settings import (
    ELASTICSEARCH_SERVERS,
    ELASTICSEARCH_USERNAME,
    ELASTICSEARCH_PASSWORD,
)
from em_product.product import StandardProduct
from utils.price_calculator import PriceCalculator


def translate_product_title(product, title_translator):
    if product.get("title_en"):
        return product.get("title_en")
    return title_translator(product.get("title"))


def update_product_translated_title(standard, product, title_translator):
    translated_title = translate_product_title(product, title_translator)
    standard.update_one({"_id": product["_id"]}, {"$set": {"title_en": translated_title}})


def translate_products(products, loader, translate_file, title_translator):
    translation = loader.search_content(list(products.keys()), "translation")
    if translation:
        for key in translation:
            products.pop(key)

    if products:
        for id, product in products.items():
            try:
                translation = {
                    "id": str(id),
                    "title": product["title"],
                    "title_en": title_translator(product["title"]),
                }
                translate_file.write(json.dumps(translation) + "\n")
                loader.save_item(translation)
            except Exception as e:
                pass


def is_valid(product) -> bool:
    if "date" not in product:
        return False

    date_obj = datetime.strptime(product["date"], "%Y-%m-%dT%H:%M:%S")
    return datetime.now() - date_obj < timedelta(weeks=1)


def main():
    service_account_path = "./gc.json"
    target_language = "en"
    translation_service = Client(
        target_language=target_language,
        credentials=service_account.Credentials.from_service_account_file(service_account_path),
    )

    pool = ThreadPool(10)

    count_total = 0
    query = {
        "available_qty": {"$gt": 0},
        "price": {"$gt": 0},
        "$or": [{"title_en": {"$exists": False}}, {"title_en": ""}, {"title_en": None}],
    }

    title_translator = get_translator(translation_service, 10000, ["ko"], "title")

    product_ids = fetch_source_ids(["WEMAKEPRICE"])

    count_total = 0

    price_rules = {"roi": 0.3, "ad_cost": 5, "transfer_cost": 15}

    price_calculator = PriceCalculator(price_rules)

    filterd_settings = {
        "ELASTICSEARCH_SERVERS": ELASTICSEARCH_SERVERS,
        "ELASTICSEARCH_USERNAME": ELASTICSEARCH_USERNAME,
        "ELASTICSEARCH_PASSWORD": ELASTICSEARCH_PASSWORD,
    }

    translation_loader = TranslationElasticSearchLoder(filterd_settings, "id")

    batch_size = 1000

    products = {}
    with open("wemakeprice_to_translate_0809.txt", "a+") as translate_file:
        with open("wemakeprice_0809.txt", "r") as file:
            for line in file:
                product = json.loads(line)
                if not is_valid(product):
                    continue

                if len(products) < batch_size:
                    products[product["_id"]] = product
                    continue
                translate_products(products, translation_loader, translate_file, title_translator)
                products = {}

            if products:
                translate_products(products, translation_loader, translate_file, title_translator)
                products = {}

        # try:
        #     pool.apply_async(
        #         update_product_translated_title, args=(standard, product, title_translator)
        #     )
        # except Exception as e:
        #     pass

    pool.close()
    pool.join()

    print(count_total)


if __name__ == "__main__":
    main()
