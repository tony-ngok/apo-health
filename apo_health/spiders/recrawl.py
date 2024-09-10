import scrapy
import scrapy.selector

from apo_health.product_manager.formatter import ProductParser
from resources.base_spider import BaseSpider


class RecrawlSpider(BaseSpider):
    name = "recrawl"
    # allowed_domains = ["apo_health.com"]
    start_urls = []

    custom_settings = {
        "ITEM_PIPELINES": {
            "apo_health.pipelines.RecrawlProductPipeline": 400,
        }
    }

    def __init__(self, *args, **kwargs):
        super(RecrawlSpider, self).__init__(*args, **kwargs)
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
            "_shopify_sa_p": "",
            "_pandectes_gdpr": "eyJjb3VudHJ5Ijp7ImNvZGUiOiJVUyIsInN0YXRlIjoiTU8iLCJkZXRlY3RlZCI6MTcyNDUyNzU3NX0sInN0YXR1cyI6ImFsbG93IiwidGltZXN0YW1wIjoxNzI0MzQ1MDEzLCJwcmVmZXJlbmNlcyI6MCwiaWQiOiI2NmM3NmFiNTkyNjZjMjc3YmY1MDExM2YifQ==",
            "_shopify_s": "d13bb88b-b4e3-4261-baef-14477a43d620",
            "_shopify_sa_t": "2024-08-24T19%3A51%3A58.427Z",
            "_gat": "1",
            "_ga_V5G1FF7JMC": "GS1.1.1724527574.6.1.1724529119.59.0.0",
            "_uetsid": "41785160621d11ef85c0afeecfc579e7",
            "_uetvid": "c59533d060a411ef9123cdbb47128eb9",
            "keep_alive": "57184b5e-2b03-4179-9e7a-5d47ae3484db",
            "_ga": "GA1.2.1476992882.1724344628",
            "_gat_gtag_UA_185803994_1": "1",
            "_clsk": "964chl%7C1724529119830%7C13%7C1%7Cl.clarity.ms%2Fcollect",
        }

    def start_requests(self):
        for url in RecrawlSpider.start_urls:
            if not url.endswith("html"):
                url = url.strip() + ".html"
            yield scrapy.Request(
                url,
                headers=self.get_headers(),
                cookies=self.cookies,
            )

    def get_headers(self):
        headers = {
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Pragma": "no-cache",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "X-Requested-With": "XMLHttpRequest",
            "sec-ch-ua": '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Linux"',
        }

        return headers

    def errback(self, failure):
        self.logger.error(f"{failure.request.url}: {repr(failure)}")

    def parse(self, response):
        self.logger.info(f"{response.url}: {response.status}")
        if response.status >= 300:
            return None

        parser = ProductParser()
        yield parser.parse(response)
