from datetime import datetime
import json
import re
import os
import scrapy
import scrapy.selector
from apotal.items import ProductItem
from apotal.product_manager import formatter


from urllib.parse import urlparse, urlunparse


class ProductSeedSpider(scrapy.Spider):
    name = "product-seed"
    allowed_domains = ["apotal.com"]
    start_urls = ["https://front.apotal.com/product/2866049042"]

    custom_settings = {
        "ITEM_PIPELINES": {
            "apotal.pipelines.SeedProductPipeline": 400,
        }
    }

    def check_url(self, url):
        parsed_url = urlparse(url)
        split_path = parsed_url.path.split("/")
        if len(split_path) > 1 and split_path[1] == "prod":
            split_path[1] = "product"
            parsed_url = parsed_url._replace(path="/".join(split_path))

        return urlunparse(parsed_url)

    def start_requests(self):
        for url in ProductSeedSpider.start_urls:
            headers = self.get_headers()
            yield self.crawl_product(self.check_url(url), headers)

    def get_product_id(self, url):
        parse_usl = urlparse(url)
        split_path = parse_usl.path.split("/")
        return split_path.pop()

    def get_sku(self, url):
        parse_usl = urlparse(url)
        split_path = parse_usl.path.split("/")
        return split_path.pop()

    def get_cookies(self):
        cookies = {
            "wmp-auk": "f5d78ebd-7593-44d7-a83e-8256-ebec6ac34a3a",
            "wmp_pcstamp": "1716575146576588384",
            "_gid": "GA1.2.136416936.1717424568",
            "rp": "http%3A%2F%2Ffront.apotal.com%2Fcategory%2Fdivision%2F2100374",
            "__utmc": "122159757",
            "__utmz": "122159757.1717448436.11.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none)",
            "__utma": "122159757.919114022.1716575151.1717507113.1717510302.13",
            "wlogFunnel": "WMP-PC-002-0-V",
            "cto_bundle": "M9jcYV9YYXc4aXJKJTJCa1V0TGNjOVdNbEYyWWNnTzVTM0plSjZxdjYxc2lRcVJDZmw5SHQ4ekRqJTJGMGI3eUpQdkRvZmowUCUyQlNHZmtGZjljOUFIbjJoSEVOdkRxa1lBaEU0V2pYR0pBcXpsWFh5ZTk2SEtmMjFzQ1oxS3hMQ3R3NXBKbU9lZjlnQmE5eTNaSDlCaGVtbzlvU00lMkZnYmo4MWUxdHMyZ1BrN0UlMkJSTFlMd0VBcE1GZzlTcW1sVlZnb0Q3azdYcXZhY0p2QmdVSmFHQVgwaklOc0c0T29EUDdJUzZOJTJGZVY0cUt4WHl6eXN3VVU1UGNzaWVUZEZoZ3BrRjEyMWdMNlBRV3Rka2dLM1hWQ3d6MVVVaXZTbExJbFhiaEpCQTdkdHlkcm43Z2R5bGFUY0lQbENhRERlJTJGNlpBY3ljc1BPejdr",
            "_ga_0CD35LTKXG": "GS1.2.1717510309.12.1.1717510407.51.0.0",
            "__utmt": "1",
            "__utmb": "122159757.8.10.1717510302",
            "_ga_C3QBWSBLPT": "GS1.1.1717510303.19.1.1717511375.55.0.0",
            "_ga": "GA1.1.1922377992.1716575151",
        }
        return cookies

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

    def get_api_url(self, url):
        parse_usl = urlparse(url)
        split_path = parse_usl.path.split("/")
        product_id = split_path.pop()
        url_type = split_path.pop()
        if url_type == "product":
            base_url = "https://front.apotal.com/api/review/{url_type}/v2.1/{product_id}/review/info.json?sortType=BEST&viewScoreType=TOTAL&page=1&ieFix="
        else:
            base_url = f"https://front.apotal.com/api/review/{url_type}/{product_id}/review/info.json?sortType=BEST&viewScoreType=TOTAL&page=1&ieFix="
        return f"{base_url}{round(datetime.now().timestamp()*100)}"

    def crawl_product(self, url, headers):
        return scrapy.Request(
            url,
            method="GET",
            headers=headers,
            cookies=self.get_cookies(),
            errback=self.errback,
            callback=self.parse_product,
        )

    def errback(self, failure):
        self.logger.error(f"{failure.request.url}: {repr(failure)}")

    def get_img_tag(self, url):
        return f"<img src='{url}'>"

    def get_category_id(self, url):
        return url.split("/").pop()

    def get_title(self, data):
        if "basic" in data:
            return data.get("basic", {}).get("prodNm")
        elif "prodMain" in data:
            return data.get("prodMain", {}).get("basic", {}).get("prodNm")

    def extract_image_url(self, url):
        parsed_url = urlparse(url)
        return parsed_url.geturl()

    def get_title_from_prod_main(self, data):
        return data.get("prodMain", {}).get("basic", {}).get("prodNm")

    def get_title_from_basic(self, data):
        return data.get("basic", {}).get("prodNm")

    def get_price(self, data):
        kr_won = data.get("sale", {}).get("salePrice") or data.get("sale", {}).get("originPrice")
        if not kr_won:
            return None

        return round(int(kr_won) * 0.00073, 2)

    def get_categories(self, data):
        if "basic" not in data:
            data = data.get("prodMain", {})
        lcate = data.get("basic", {}).get("lcateNm")
        mcate = data.get("basic", {}).get("mcateNm")
        scate = data.get("basic", {}).get("scateNm")
        return f"{lcate} > {mcate} > {scate}"

    def get_available_qty(self, data):
        return data.get("sale", {}).get("stockCount", 0)

    def get_sold_count(self, data):
        return data.get("sale", {}).get("salesCount", 0)

    def get_brand_frome_basic(self, data):
        return data.get("basic", {}).get("brandNm")

    def get_brand_frome_main(self, data):
        return data.get("prodMain", {}).get("basic", {}).get("brandNm")

    def get_brand(self, data):
        return data.get("basic", {}).get("brandNm") or data.get("prodMain", {}).get(
            "basic", {}
        ).get("brandNm")

    def get_images(self, data):
        try:
            image_list = data.get("prodMain", {}).get("mainImgList") or data.get(
                "mainImgList", [{}]
            )
            return ";".join(
                [
                    self.extract_image_url(image.get("origin", {}).get("imgUrl"))
                    for image in image_list
                ]
            )
        except Exception as e:
            breakpoint()

    def get_description(self, data):
        desc = data.get("detail", {}).get("desc")
        if desc == "null":
            image_list = data.get("detail", {}).get("imgList")
            if not image_list:
                return
            desc = (
                "<div>"
                + "".join([self.get_img_tag(image["imgUrl"]) for image in image_list])
                + "</div>"
            )
        return desc

    def get_options(self, data):
        options = data.get("option", {}).get("sel", {}).get("optTitle")
        if options:
            return [{"id": None, "name": option.strip()} for option in options]

    def get_specifications(self, data):
        notices = data.get("noticeGroupList", [])
        for notice in notices:
            notice.get("noticeNm")
            notice.get("desc")

    def get_is_deal(self, data):
        is_deal = True if "prodSimpleList" in data else False
        return is_deal

    def extract_initial_data(self, script):
        match = re.search(r"GV\.set\('initialData', JSON\.parse\('({.*?})'\)\);", script)
        if match:
            return match.group(1)

    def get_variants_form_option(self, data, options):
        option_values = data.get("option", {}).get("sel", {}).get("valueList")
        if not option_values:
            return
        standard_variants = []
        for option in option_values:
            standard_variants.extend(self.get_variants_from_option(option, options))
        return standard_variants

    def get_variants(self, data, options):
        if not options:
            return
        if len(options) == 2:
            return self.get_variants_form_option(data, options)

        option_values = data.get("option", {}).get("sel", {}).get("valueList")
        if not option_values:
            return
        standard_variants = []

        for variant in option_values:
            standard_variant = {}
            standard_variant["option_values"] = [
                {"option_name": options[0]["name"], "option_value": variant["optVal"].strip()}
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

    async def get_data(self, page):
        return await page.evaluate("""() => {
            return GV.get('initialData');
        }""")

    def parse_product(self, response):
        item = ProductItem()
        item["product_id"] = self.get_product_id(response.url)
        item["sku"] = self.get_sku(response.url)
        item["url"] = response.url
        item["date"] = datetime.now().replace(microsecond=0).isoformat()
        item["existence"] = False
        if response.status >= 400:
            yield item
            return

        script = response.xpath("//script[contains(text(), 'initialData')]/text()").extract_first()
        if not script:
            yield item
            return
        initial_data = self.extract_initial_data(script)
        if not initial_data:
            yield item
            return

        item["data"] = initial_data

        item["_id"] = item["sku"]
        if response.text.find("판매종료") > 0:
            item["existence"] = False
        else:
            item["existence"] = True

        item = formatter.to_standard(item)
        if item:
            yield item
