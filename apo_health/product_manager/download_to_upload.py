import json
from em_product.product import StandardProduct
from utils.price_calculator import PriceCalculator
from utils.site_product import fetch_source_ids
from .formatter import to_upload
from .loader import ApoHealthElasticSearchLoder
from apo_health.settings import (
    ELASTICSEARCH_SERVERS,
    ELASTICSEARCH_USERNAME,
    ELASTICSEARCH_PASSWORD,
)
from resources.filters import product_filer, doc_filer


def main():
    product_ids = fetch_source_ids(["ApoHealth"])

    price_rules = {"roi": 0.3, "ad_cost": 5, "transfer_cost": 0}

    price_calculator = PriceCalculator(price_rules)

    filterd_settings = {
        "ELASTICSEARCH_SERVERS": ELASTICSEARCH_SERVERS,
        "ELASTICSEARCH_USERNAME": ELASTICSEARCH_USERNAME,
        "ELASTICSEARCH_PASSWORD": ELASTICSEARCH_PASSWORD,
    }

    loader = ApoHealthElasticSearchLoder(filterd_settings, "product_id")

    with open("apo_health_0903.txt", "w+") as file:
        for doc in loader.load_content(type="product", query=None):
            if doc_filer(doc):
                continue

            try:
                if doc["product_id"] in product_ids:
                    continue
                if isinstance(doc["images"], list):
                    doc["images"] = ";".join(doc["images"])
                product = doc
                product["source"] = "ApoHealth"
                keys = ["available_qty", "title_en", "options", "variants", "sold_count"]
                for key in keys:
                    if key not in product:
                        product[key] = None
                product["has_only_default_variant"] = True
                if product["existence"] is None:
                    product["existence"] = True
                product["sku"] = "X21_" + product["product_id"]

                product["price"] = product["price"] + product["shipping_fee"]

                standard_product = StandardProduct(**product)
                upload_product = to_upload(standard_product.model_dump(), price_calculator)
                if product_filer(upload_product):
                    continue
                json.dump(upload_product, file, ensure_ascii=False)
                file.write("\n")
            except Exception as e:
                breakpoint()


if __name__ == "__main__":
    main()
