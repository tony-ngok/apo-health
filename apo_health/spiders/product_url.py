from datetime import datetime
import scrapy
from apo_health.items import ProductUrlItem
import xml.etree.ElementTree as ET

from urllib.parse import urlparse, urlunparse
from resources.base_spider import BaseSpider


class ProductUrlSpider(BaseSpider):
    name = "product-url"
    allowed_domains = ["apo-health.com"]
    start_urls = []

    custom_settings = {
        "ITEM_PIPELINES": {
            "apo_health.pipelines.ProductUrlPipeline": 400,
        }
    }

    def __init__(self, *args, **kwargs):
        super(ProductUrlSpider, self).__init__(*args, **kwargs)

        self.cookies = {
            "secure_customer_sig": "",
            "localization": "US",
            "_shopify_y": "cc8af215-40b7-499b-a917-66938a581b24",
            "_orig_referrer": "https%3A%2F%2Fwww.google.com%2F",
            "_landing_page": "%2Fcollections%2Fabnehmen%2Fproducts%2Falmased-vitalkost-pulver-500-g-pulver",
            "_gcl_au": "1.1.884320508.1724344627",
            "cart": "Z2NwLWV1cm9wZS13ZXN0NDowMUo1WEY1V1ZTVjlRVkZWS0UyMFlQUDJYVg%3Fkey%3D7ab7da1917fbcf1d3533405c5e898370",
            "cart_ts": "1724344628",
            "cart_sig": "31f2f403515f4e6a75da06c8d541930a",
            "ly-lang-selected": "en",
            "_tracking_consent": "%7B%22con%22%3A%7B%22CMP%22%3A%7B%22a%22%3A%221%22%2C%22m%22%3A%221%22%2C%22p%22%3A%221%22%2C%22s%22%3A%22%22%7D%7D%2C%22v%22%3A%222.1%22%2C%22region%22%3A%22USMO%22%2C%22reg%22%3A%22%22%7D",
            "_cmp_a": "%7B%22purposes%22%3A%7B%22a%22%3Atrue%2C%22p%22%3Atrue%2C%22m%22%3Atrue%2C%22t%22%3Atrue%7D%2C%22display_banner%22%3Afalse%2C%22sale_of_data_region%22%3Afalse%7D",
            "_gid": "GA1.2.1553015619.1724506327",
            "_clck": "1jwtj0x%7C2%7Cfol%7C0%7C1695",
            "et_oip": "no",
            "receive-cookie-deprecation": "1",
            "_shopify_s": "d13bb88b-b4e3-4261-baef-14477a43d620",
            "_shopify_sa_t": "2024-08-24T19%3A26%3A14.512Z",
            "_shopify_sa_p": "",
            "_gat": "1",
            "_ga_V5G1FF7JMC": "GS1.1.1724527574.6.0.1724527574.60.0.0",
            "_uetsid": "41785160621d11ef85c0afeecfc579e7",
            "_uetvid": "c59533d060a411ef9123cdbb47128eb9",
            "_ga": "GA1.2.1476992882.1724344628",
            "_gat_gtag_UA_185803994_1": "1",
            "_clsk": "964chl%7C1724527575273%7C1%7C1%7Cl.clarity.ms%2Fcollect",
            "_pandectes_gdpr": "eyJjb3VudHJ5Ijp7ImNvZGUiOiJVUyIsInN0YXRlIjoiTU8iLCJkZXRlY3RlZCI6MTcyNDUyNzU3NX0sInN0YXR1cyI6ImFsbG93IiwidGltZXN0YW1wIjoxNzI0MzQ1MDEzLCJwcmVmZXJlbmNlcyI6MCwiaWQiOiI2NmM3NmFiNTkyNjZjMjc3YmY1MDExM2YifQ==",
            "keep_alive": "6ceee487-31f4-476e-9315-3d47df8e511f",
        }

    def start_requests(self):
        for i in range(1956):
            url = f"https://www.apo-health.com/collections/all?page={i+1}&grid_list=grid-view"
            yield scrapy.Request(
                url,
                headers=self.get_headers(),
                cookies=self.cookies,
                errback=self.errback,
            )

    def get_headers(self):
        return {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
            "cache-control": "no-cache",
            "pragma": "no-cache",
            "priority": "u=0, i",
            "referer": "http://35.192.187.156/",
            "sec-ch-ua": '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Linux"',
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "cross-site",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
        }

    def get_product_id(self, url):
        parse_usl = urlparse(url)
        return parse_usl.path.split("/").pop()

    def errback(self, failure):
        self.logger.error(repr(failure))

    def get_cat_id(self, url):
        parsed_url = urlparse(url)
        return parsed_url.path

    def parse(self, response):
        pathes = response.xpath(
            "//div[@class='productitem']//div[@class='productitem__image-container']//a/@href"
        ).getall()
        for path in pathes:
            url = response.urljoin(path)
            yield {
                "url": url,
                "id": self.get_product_id(url),
                "date": datetime.now().replace(microsecond=0).isoformat(),
            }
