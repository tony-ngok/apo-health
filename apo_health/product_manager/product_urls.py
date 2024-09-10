import json
from urllib.parse import urlparse


def get_product_id_from_url(url):
    parsed_url = urlparse(url)
    return parsed_url.path.split("/").pop().split(".").pop(0)


def main():
    product_urls_crawled = set()

    with open("apo_health_product_urls_090302.txt", "w+") as file_to_crawl:
        with open("/home/sky/src/data/apo_health_products_0903.txt", "r") as file:
            for line in file:
                product = json.loads(line)
                product_urls_crawled.add(get_product_id_from_url(product["url"]))

        with open("/home/sky/src/data/apo_health_product_urls_0903.txt", "r") as file:
            for line in file:
                product = json.loads(line)

                if get_product_id_from_url(product["url"]) in product_urls_crawled:
                    continue

                file_to_crawl.write(product["url"] + "\n")


if __name__ == "__main__":
    main()
