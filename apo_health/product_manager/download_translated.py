# from datetime import datetime
# import json
# from multiprocessing.pool import ThreadPool
# import re

# from google.oauth2 import service_account
# from google.cloud.translate_v2 import Client

# from peewee import *

# from em_product.product import StandardProduct
# from pymongo import MongoClient


# from wemakeprice.settings import MONGO_URI
# from utils.site_product import fetch_source_ids
# from utils.translate_service import get_translator

# from .formatter import to_standard


# def connect_to_mongo_by_collection(db_name, collection_name):
#     client = MongoClient(MONGO_URI)
#     db = client[db_name]
#     collection = db[collection_name]
#     return collection


# def invalid_specification(spec):
#     invalid_values = ["상품상세설명 참조", "상품상세 설명 참고", "상세설명참조", "전화"]
#     invalid_keys = [
#         "상품상세설명 참조",
#         "소비자상담관련 전화번호",
#         "A/S 책임자와 전화번호 또는 소비자상담 관련 전화번호",
#         "해당사항없음",
#     ]
#     for value in invalid_values:
#         if value in spec.get("value"):
#             return True
#     for name in invalid_keys:
#         if name in spec.get("name"):
#             return True


# def add_specs_to_description(specs, description):
#     if not specs:
#         return description

#     trs = []
#     for spec in specs:
#         tr_str = f"""<tr><th>{spec["name"]}</th><td><span>{spec["value"]}</span></td></tr>"""
#         trs.append(tr_str)

#     return f"""<tbody>{"".join(trs)}</tbody>""" + description


# def get_specifications(product):
#     if not product["specifications"]:
#         return None, None

#     new_specs = []
#     desc_specs = []
#     for spec in product["specifications"]:
#         if invalid_specification(spec):
#             continue
#         if (
#             spec.get("name").find("기한 ") > -1
#             or spec.get("name").find("사용방법") > -1
#             or spec.get("name").find("화장품법") > -1
#             or spec.get("name").find("사용할 때의 주의사항") > -1
#             or spec.get("name").find("품질보증기준") > -1
#         ):
#             desc_specs.append(spec)

#             continue
#         new_specs.append(spec)

#     if not new_specs:
#         new_specs = None

#     return new_specs, desc_specs


# def format_product(product):
#     new_specs, desc_specs = get_specifications(product)
#     product["specifications"] = new_specs
#     product["description"] = add_specs_to_description(desc_specs, product["description"])

#     return product


# def upadate_product_in_db(collection, product):
#     query = {"_id": product.pop("_id")}
#     new_value = {"$set": product}
#     collection.update_one(query, new_value, True)


# def translate_product_title(product, title_translator):
#     if product.get("title_en"):
#         return product.get("title_en")
#     return title_translator(product.get("title"))


# def update_product_translated_option(collection, product, translated_option_values):
#     if not translated_option_values:
#         return

#     translated_options = []
#     # for option_value in translated_option_values:
#     #     translated_option = {
#     #         "id": option_value.get("option_id"),
#     #         "name": option_value.get("option_name"),
#     #     }
#     #     translated_options.append(translated_option)

#     update_operations = []
#     set_opt = {}

#     for index, variant_option_values in enumerate(translated_option_values):
#         set_opt.update(
#             {
#                 f"variants.{index}.translated_option_values": variant_option_values,
#             }
#         )

#     collection.update_one({"_id": product["_id"]}, {"$set": set_opt})


# def translate_product_option(product, option_translator):
#     if not product["variants"]:
#         return
#     translated_variant_option_values = []
#     for variant in product["variants"]:
#         translated_option_values = []
#         if variant.get("translated_option_values"):
#             continue

#         for option_value in variant["option_values"]:
#             translated_op_name = option_translator(option_value["option_name"])
#             translated_op_value = option_translator(option_value["option_value"])
#             translated_option_value = {
#                 "option_id": option_value.get("option_id"),
#                 "option_value_id": option_value.get("option_value_id"),
#                 "option_name": translated_op_name,
#                 "option_value": translated_op_value,
#             }
#             translated_option_values.append(translated_option_value)
#         translated_variant_option_values.append(translated_option_values)
#     return translated_variant_option_values


# def update_product_translated_options(standard, product, option_translator):
#     translated_options = translate_product_option(product, option_translator)
#     update_product_translated_option(standard, product, translated_options)


# def main():
#     service_account_path = "./gc.json"
#     target_language = "en"
#     translation_service = Client(
#         target_language=target_language,
#         credentials=service_account.Credentials.from_service_account_file(service_account_path),
#     )
#     db_name = "wemakeprice"
#     standard = connect_to_mongo_by_collection(db_name, "standard")
#     pool = ThreadPool(10)

#     count_total = 0
#     query = {
#         "available_qty": {"$gt": 0},
#         "price": {"$gt": 0},
#         "translated_options": {"$exists": True},
#         "variants": {"$ne": None},
#     }
#     total_count = 100000

#     title_translator = get_translator(translation_service, total_count, ["ko"], "title")
#     option_translator = get_translator(translation_service, total_count, ["ko"], "option")

#     for product in standard.find(query):
#         if product["variants"] and len(product["variants"]) > 5:
#             continue

#         count_total += 1

#         try:
#             # translated_title = translate_product_title(product, title_translator)

#             # update_product_translated_options(standard, product, option_translator)
#             pool.apply_async(
#                 update_product_translated_options, args=(standard, product, option_translator)
#             )
#         except Exception as e:
#             pass

#     pool.close()
#     pool.join()

#     print(count_total)


# if __name__ == "__main__":
#     main()
