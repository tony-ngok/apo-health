from datetime import datetime
import json
from multiprocessing.pool import ThreadPool
import re

from peewee import *
from playhouse.db_url import connect

from em_product.product import StandardProduct
from pymongo import MongoClient
from urllib.parse import urlparse


from google.oauth2 import service_account
from google.cloud.translate_v2 import Client


from wemakeprice.settings import MONGO_URI
from utils.site_product import fetch_source_ids


def connect_to_mongo_by_collection(db_name, collection_name):
    client = MongoClient(MONGO_URI)
    db = client[db_name]
    collection = db[collection_name]
    return collection


def get_brand(data):
    return data.get("basic", {}).get("brandNm") or data.get("prodMain", {}).get("basic", {}).get(
        "brandNm"
    )


def get_title(data):
    return data.get("basic", {}).get("prodNm") or data.get("prodMain", {}).get("basic", {}).get(
        "prodNm"
    )


def get_img_tag(url):
    return f"<img src='{url}'>"


def get_description(data):
    desc = data.get("detail", {}).get("desc")
    if desc == "null":
        image_list = data.get("detail", {}).get("imgList")
        if not image_list:
            return
        desc = "<div>" + "".join([get_img_tag(image["imgUrl"]) for image in image_list]) + "</div>"
    return desc


def invalid_specification(notice):
    invalid_values = ["상품상세설명 참조", "상품상세 설명 참고"]
    invalid_keys = [
        "상품상세설명 참조",
        "소비자상담관련 전화번호",
        "A/S 책임자와 전화번호 또는 소비자상담 관련 전화번호",
    ]
    if notice.get("desc") in invalid_values or notice.get("noticeNm") in invalid_keys:
        return True


def get_specifications(data):
    notices = data.get("noticeGroupList", [{}])[0].get("noticeList", [])
    specs = []
    for notice in notices:
        if not (
            notice.get("desc") == "상품상세 설명 참고"
            or notice.get("noticeNm") == "소비자상담관련 전화번호"
        ):
            if notice.get("noticeNm") and notice.get("desc"):
                specs.append({"name": notice.get("noticeNm"), "value": notice.get("desc")})

    return specs if specs else None


def extract_image_url(url):
    parsed_url = urlparse(url)
    return parsed_url.geturl()


def get_images(data):
    try:
        image_list = data.get("prodMain", {}).get("mainImgList") or data.get("mainImgList", [{}])
        return ";".join(
            [extract_image_url(image.get("origin", {}).get("imgUrl")) for image in image_list]
        )
    except Exception as e:
        breakpoint()


def get_price(data):
    kr_won = data.get("sale", {}).get("salePrice") or data.get("sale", {}).get("originPrice")
    if not kr_won:
        return None

    return round(int(kr_won) * 0.00073, 2)


def get_categories(data):
    if "basic" not in data:
        data = data.get("prodMain", {})
    lcate = data.get("basic", {}).get("lcateNm")
    mcate = data.get("basic", {}).get("mcateNm")
    scate = data.get("basic", {}).get("scateNm")
    return f"{lcate} > {mcate} > {scate}"


def get_available_qty(data):
    return data.get("sale", {}).get("stockCount", 0)


def get_sold_count(data):
    return data.get("sale", {}).get("salesCount", 0)


def get_variants_from_option(option, options):
    standard_variants = []

    option_value = {
        "option_id": None,
        "option_value_id": None,
        "option_name": options[0]["name"],
        "option_value": option["optVal"].strip(),
    }
    for variant in option["valueList"]:
        standard_variant = {}
        standard_variant["option_values"] = [
            option_value,
            {
                "option_id": None,
                "option_value_id": None,
                "option_name": options[1]["name"],
                "option_value": option["optVal"].strip(),
            },
        ]
        standard_variant["variant_id"] = str(variant["optNo"])
        standard_variant["sku"] = str(variant["optNo"])
        standard_variant["images"] = None
        standard_variant["barcode"] = None
        standard_variant["price"] = round(int(variant["optSalePrice"]) * 0.00073, 2)
        standard_variant["available_qty"] = min(int(variant["stockCount"]), 10)
        standard_variants.append(standard_variant)
    return standard_variants


def get_variants_form_option(data, options):
    option_values = data.get("option", {}).get("sel", {}).get("valueList")
    if not option_values:
        return
    standard_variants = []
    for option in option_values:
        standard_variants.extend(get_variants_from_option(option, options))
    return standard_variants


def get_variants_form_simple_list(data, option_title):
    variants = data.get("prodSimpleList")
    if not variants:
        return
    standard_variants = []
    for variant in variants:
        standard_variant = {}
        standard_variant["title"] = variant["prodNm"]
        standard_variant["sku"] = variant["prodNo"]
        standard_variant["images"] = extract_image_url(
            variant.get("mainImg", {}).get("largeImg", {}).get("imgUrl")
        )
        standard_variant["price"] = round(int(variant["salePrice"]) * 0.00073, 2)
        standard_variant["available_qty"] = min(int(variant["stockCount"]), 10)
        standard_variant["option_values"] = [
            {
                "option_id": None,
                "option_value_id": None,
                "option_name": option_title,
                "option_value": variant["optVal"].strip(),
            }
        ]
        standard_variants.append(standard_variant)

    return standard_variants


def get_variants(data, options):
    if not options:
        return
    if len(options) == 2:
        return get_variants_form_option(data, options)

    option_values = data.get("option", {}).get("sel", {}).get("valueList")
    if not option_values:
        return
    standard_variants = []

    for variant in option_values:
        standard_variant = {}
        standard_variant["option_values"] = [
            {
                "option_id": None,
                "option_value_id": None,
                "option_name": options[0]["name"],
                "option_value": variant["optVal"].strip(),
            }
        ]
        standard_variant["variant_id"] = str(variant["optNo"])
        standard_variant["sku"] = str(variant["optNo"])
        standard_variant["barcode"] = None
        standard_variant["images"] = None
        standard_variant["price"] = round(
            int(variant["optAddPrice"] + variant["optSalePrice"]) * 0.00073, 2
        )
        standard_variant["available_qty"] = min(int(variant.get("stockCount", 0)), 10)
        standard_variants.append(standard_variant)
    return standard_variants


def translate_title(translation_service, title):
    try:
        to_translate = [title]
        result = None

        try:
            result = translation_service.translate(to_translate)
        except ValueError:
            pass
        except Exception as e:
            pass

        if result is None:
            return

        title_translation = result[0]
        title_en = title_translation["translatedText"]

        return title_en
    except Exception as e:
        pass


def add_title_en(collection, doc, translation_service, title):
    title_en = translate_title(translation_service, title)
    query = {"_id": doc["_id"]}
    collection.update_one(query, {"$set": {"title_en": title_en}}, True)
    return title_en


def format_product(collection, doc, translation_service):
    data = None
    product_data = None
    if "data" in doc:
        data = doc["data"]
        if isinstance(data, str):
            sanitized = data.replace("\\\\", "\\")
            try:
                data = json.loads(sanitized)
            except json.decoder.JSONDecodeError as e:
                return
    else:
        return

    if data is None:
        return

    if "prodMain" in data:
        product_data = data["prodMain"]
    else:
        product_data = data

    options = get_options(product_data)

    is_deal = True if "prodSimpleList" in doc["data"] else False
    multi_variants = True if options else False
    variants = get_variants(product_data, options)
    title = get_title(data)
    title_en = doc.get("title_en")

    if is_deal or multi_variants or not title:
        return

    if not title_en:
        title_en = add_title_en(collection, doc, translation_service, title)

    item = {
        "_id": doc["_id"],
        "product_id": doc["_id"],
        "url": doc.get("url") or f"https://front.wemakeprice.com/product/{doc['_id']}",
        "source": doc.get("source") or "wemakeprice",
        "sku": str(doc["_id"]),
        "existence": doc.get("existence", True),
        "title_en": title_en,
        "title": title,
        "description": get_description(data),
        "description_en": None,
        "summary": None,
        "upc": None,
        "brand": get_brand(data),
        "specifications": get_specifications(data),
        "categories": get_categories(data),
        "images": get_images(data),
        "price": get_price(data),
        "available_qty": min(get_available_qty(data), 10),
        "videos": None,
        "sold_count": get_sold_count(data),
        "shipping_fee": 0,
        "options": options,
        "variants": variants,
        "has_only_default_variant": True if variants is None else False,
        "date": datetime.now().replace(microsecond=0).isoformat(),
        "height": None,
        "width": None,
        "length": None,
        "shipping_days_min": None,
        "shipping_days_max": None,
        "returnable": None,
        "reviews": None,
        "rating": None,
        "weight": None,
    }

    return item


def get_options(data):
    options = data.get("option", {}).get("sel", {}).get("optTitle")
    if options:
        return [{"id": None, "name": option.strip()} for option in options]


def upadate_product_in_db(collection, product):
    query = {"_id": product.pop("_id")}
    new_value = {"$set": product}
    collection.update_one(query, new_value, True)


def main():
    service_account_path = "./gc.json"
    target_language = "en"
    translation_service = Client(
        target_language=target_language,
        credentials=service_account.Credentials.from_service_account_file(service_account_path),
    )

    db_name = "wemakeprice"
    collection_name = "products"
    collection = connect_to_mongo_by_collection(db_name, collection_name)
    product_ids = fetch_source_ids(["WEMAKEPRICE"])

    count_total = 0
    count_exists = 0
    with open("wemakeprice_0628_5.txt", "w+") as file:
        for doc in collection.find(
            {
                # "title_en": {"$exists": False},
                # "available_qty": {"$exists": True, "$gt": 0},
                # "price": {"$exists": True, "$ne": None},
            }
        ):
            if not isinstance(doc["_id"], int) and not doc["_id"].isdigit():
                continue

            count_total += 1

            if str(doc["_id"]) in product_ids or doc.get("options") or doc.get("variants"):
                count_exists += 1
                continue

            try:
                formated_product = format_product(collection, doc, translation_service)
                if not formated_product or not formated_product["price"]:
                    continue

                standard_product = StandardProduct(**formated_product)
                json.dump(standard_product.model_dump(), file, ensure_ascii=False)
                file.write("\n")
            except Exception as e:
                breakpoint()
                pass


if __name__ == "__main__":
    main()
