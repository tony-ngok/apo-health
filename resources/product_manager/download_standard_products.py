from datetime import datetime
import json
from multiprocessing.pool import ThreadPool
import re

from peewee import *
from playhouse.db_url import connect

from em_product.product import StandardProduct


from utils.site_product import fetch_source_ids


def upadate_product_in_db(collection, product):
    query = {"_id": product.pop("_id")}
    new_value = {"$set": product}
    collection.update_one(query, new_value, True)


def main():
    product_ids = fetch_source_ids(["WEMAKEPRICE", "Rakuten", "Ebay_US", "Coupang", "cosme",
        "nandansons", "jasminetrading", "faire", "Fragrancex", "11ST", "Dangdang"
        "OLIVEYOUNG"])

    count_total = 0
    count_exists = 0
    with open("wemakeprice_0628_6.txt", "w+") as file:
        for doc in collection.find(
            {
                "title_en": {"$exists": True},
                "price": {"$exists": True, "$ne": None},
            }
        ):
            count_total += 1

            if str(doc["_id"]) in product_ids or doc.get("options") or doc.get("variants"):
                count_exists += 1
                continue

            try:
                formated_product = format_product(doc)
                if not formated_product or not formated_product["price"]:
                    continue

                standard_product = StandardProduct(**formated_product)
                json.dump(standard_product.model_dump(), file, ensure_ascii=False)
                file.write("\n")
            except Exception as e:
                breakpoint()
                pass

    print(count_total)


if __name__ == "__main__":
    main()
