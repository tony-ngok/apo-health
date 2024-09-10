import json
from .loader import ApoHealthElasticSearchLoder, ApoHealthProductUrlElasticSearchLoder
from apo_health.settings import (
    ELASTICSEARCH_SERVERS,
    ELASTICSEARCH_USERNAME,
    ELASTICSEARCH_PASSWORD,
)


def main():
    filterd_settings = {
        "ELASTICSEARCH_SERVERS": ELASTICSEARCH_SERVERS,
        "ELASTICSEARCH_USERNAME": ELASTICSEARCH_USERNAME,
        "ELASTICSEARCH_PASSWORD": ELASTICSEARCH_PASSWORD,
    }

    loader = ApoHealthElasticSearchLoder(filterd_settings, "product_id")
    url_loader = ApoHealthProductUrlElasticSearchLoder(filterd_settings, "id")

    with open("apo_health_products_0903.txt", "w+") as file:
        for doc in loader.load_content(type="product", query=None):
            new_doc = {}
            new_doc["url"] = doc["url"]
            new_doc["id"] = doc["product_id"]
            json.dump(new_doc, file, ensure_ascii=False)
            file.write("\n")

    with open("apo_health_product_urls_0903.txt", "w+") as file:
        for doc in url_loader.load_content(type="product_url", query=None):
            json.dump(doc, file, ensure_ascii=False)
            file.write("\n")


if __name__ == "__main__":
    main()
