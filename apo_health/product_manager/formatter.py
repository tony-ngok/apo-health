from datetime import datetime
import json
from urllib.parse import urlparse
from scrapy.selector import Selector
from bs4 import BeautifulSoup
from apo_health.util import Util


class ProductParser:
    EURO_to_US_DOLLAR_EXCHANGE_RATE = 1.12

    def get_product_id(self, url):
        parse_usl = urlparse(url)
        split_path = parse_usl.path.split("/")
        return split_path.pop()

    def remove_td_a_p_tag_replace_content(self, text):
        will_remove_tags = ["td", "a", "p"]
        soup = BeautifulSoup(text, "html.parser")
        for tag in will_remove_tags:
            for match in soup.findAll(tag):
                match.replaceWithChildren()
        return soup

    def is_listing_ended(self, response):
        listing_ended = False
        return listing_ended

    def get_title(self, data):
        return data.get("name")

    def get_brand(self, data):
        brand = None
        if "brand" in data.keys():
            brand = data["brand"]["name"]
        return brand

    def get_upc(self, data):
        upc = None

        if "variants" in data.keys():
            if len(data["variants"]) > 0:
                if "barcode" in data["variants"][0].keys():
                    upc = data["variants"][0]["barcode"]
        return upc

    def get_sku(self, data):
        sku = None

        if data:
            sku = data["sku"]

        return sku

    def get_price(self, data):
        f_price_us_dollar = None

        if data:
            if "offers" in data:
                if "price" in data["offers"] and "priceCurrency" in data["offers"]:
                    if data["offers"]["priceCurrency"] == "EUR":
                        f_price_us_dollar = float(
                            int(
                                (data["offers"]["price"] * self.EURO_to_US_DOLLAR_EXCHANGE_RATE)
                                * 100
                            )
                            / 100.0
                        )

        return f_price_us_dollar

    def get_price_compare(self, selector):
        f_price_compare_us_dollar = None

        text = selector.xpath(
            "//div[@class='price__compare-at visible']//span[@class='money']/text()"
        ).get()
        if text is not None:
            if "€" in text:
                eur_dollar = Util.extract_float_from_str(text)
                f_price_compare_us_dollar = float(
                    int((eur_dollar * self.EURO_to_US_DOLLAR_EXCHANGE_RATE) * 100) / 100.0
                )

        return f_price_compare_us_dollar

    def get_stock_quantity(self, data, url):
        i_stock_quantity = None

        if "offers" in data.keys():
            if "availability" in data["offers"].keys():
                if "OutOfStock" in data["offers"]["availability"]:
                    i_stock_quantity = 0
                elif "InStock" in data["offers"]["availability"]:
                    i_stock_quantity = None
                else:
                    raise Exception("unexpected available information")

        return i_stock_quantity

    def get_images(self, selector):
        return selector.xpath("//div[@data-pf-type='MediaItem']/img/@src").getall()

    def get_product_images(self, selector):
        imges_str = None

        images_conv_list = []
        script_text = selector.xpath("//script[@data-section-type='static-product']/text()").get()

        images_list = []
        if script_text:
            data = json.loads(script_text)
            if data is not None:
                if "product" in data:
                    if "images" in data["product"]:
                        images_list = data["product"]["images"]
        else:
            images_list = self.get_images(selector)

        # print("images_list :", images_list)

        for img in images_list:
            if "https" not in img:
                images_conv_list.append(f"https:{img}")

        if images_conv_list is not None and len(images_conv_list) > 0:
            imges_str = ";".join(images_conv_list)

        return imges_str

    def get_videos(self, response):
        return None

    def get_description_from_response(self, selector):
        return selector.xpath("//div[@data-pf-type='ProductDescription']").get()

    def get_description(self, selector):
        desc = None

        script_text = selector.xpath("//script[@data-section-type='static-product']/text()").get()
        if script_text:
            data = json.loads(script_text)
            if data is not None:
                if "product" in data:
                    if "images" in data["product"]:
                        desc = data["product"]["description"]
        else:
            return self.get_description_from_response(selector)

        return desc

    def get_summary(self, selector):
        summary = None

        summary = selector.xpath("//ul[@class='tabs-content']/li[@class='active']").get()

        return summary

    def get_categories(self, selector):
        str_cate = None

        text_list = selector.xpath("//nav[@class='breadcrumbs-container']/a/text()").getall()

        final_categories_list = []
        for text in text_list:
            if text.lower() != "home":
                final_categories_list.append(text)

        str_cate = ";".join(final_categories_list)

        return str_cate

    def get_specifications(self, selector, url):
        spec = None

        li_text_list = selector.xpath(
            "//div[contains(@class, 'product-description')]/ul[@class='tabs-content']/li"
        ).getall()

        if len(li_text_list) == 3:
            spec = []
            li_tag = li_text_list[2]

            spec_list = Selector(text=li_tag).xpath("//ul/li/text()").getall()

            for a_spec in spec_list:
                splitted = a_spec.split(":")

                if len(splitted) == 2:
                    spec.append({"name": splitted[0].strip(), "value": splitted[1].strip()})
                elif len(splitted) > 2:
                    list_value = []
                    for i in range(1, len(splitted)):
                        list_value.append(splitted[i].strip())

                    spec.append({"name": splitted[0].strip(), "value": ",".join(list_value)})
        else:
            self.file_write_exception_log(url, "Can't parse specification")

        return spec

    def get_dimensions_weight(self, selector):
        dict_dimensions_weight = {}

        width = None
        height = None
        length = None
        weight = None

        tag = selector.xpath("//p[strong[contains(text(), 'Dimensions')]]").get()
        if tag is not None:
            str = Selector(text=tag).xpath("//span/text()").get()
            if "/" in str:
                str_dimensions = str.split("/")[0]
                str_weight = str.split("/")[1]

                if "cm" in str_dimensions.lower():
                    dimens_list = str_dimensions.split("x")
                    if len(dimens_list) == 3:
                        width = Util.convertMMtoInches(
                            Util.extractFloatFromStr(dimens_list[0]) * 10
                        )
                        height = Util.convertMMtoInches(
                            Util.extractFloatFromStr(dimens_list[1]) * 10
                        )
                        length = Util.convertMMtoInches(
                            Util.extractFloatFromStr(dimens_list[2]) * 10
                        )

                if "g" in str_weight.lower() and "kg" not in str_weight.lower():
                    weight = Util.convertGramtoPound(Util.extractFloatFromStr(str_weight))
                elif "kg" in str_weight.lower():
                    weight = Util.convertGramtoPound(Util.extractFloatFromStr(str_weight) * 1000)

        dict_dimensions_weight = {
            "width": width,
            "height": height,
            "length": length,
            "weight": weight,
        }

        return dict_dimensions_weight

    def get_rating(self, selector):
        rating = None
        return rating

    def get_reviews(self, selector):
        i_review = None
        return i_review

    def get_valid_options(self, sel):
        return None

    def get_variants(self, sel, options, url):
        return None

    def get_edd_days_list(self, response):
        ship_days_list = []

        return ship_days_list

    def file_write_exception_log(self, url, message):
        file = open("Exception_Log.txt", "a", encoding="utf-8")
        file.write(url + " : " + message + "\n")
        file.close()

    def get_shipping_fee(self, response):
        return 0

    def get_product_id_from_response(self, response):
        return response.xpath("//div[@data-pf-type='ProductBox']/@data-product-id").get()

    def parse(self, response):
        prod = {}

        if response.status == 404:  # Not Found
            prod["existence"] = False
        elif response.status == 200:
            prod["existence"] = True
        else:
            prod["existence"] = False

        product_data_text_list = response.xpath(
            "//script[@type='application/ld+json']/text()"
        ).getall()

        product_data = None
        for product_data_text in product_data_text_list:
            product_data_temp = json.loads(product_data_text)
            if "@type" in product_data_temp and product_data_temp["@type"] == "Product":
                product_data = product_data_temp

        if product_data is None:
            self.file_write_exception_log(response.url, "Error can't find product_data")
            print("Error can't find product_data, will quit parse")
            return

        selector = Selector(response=response)
        dict_dimensions_weight = self.get_dimensions_weight(selector)

        prod.update(
            {
                "date": datetime.now().replace(microsecond=0).isoformat(),
                "url": response.url,
                "source": response.url.split("//").pop(1).split("/").pop(0).replace(".", "_"),
                "product_id": product_data.get("mpn")
                or self.get_product_id_from_response(response),
                "sku": product_data["sku"],
                "upc": None,
                "returnable": False,
                "weight": dict_dimensions_weight["weight"],
                "width": dict_dimensions_weight["width"],
                "height": dict_dimensions_weight["height"],
                "length": dict_dimensions_weight["length"],
            }
        )

        prod["title"] = self.get_title(product_data)
        if not prod["title"]:
            return None
        prod["title_en"] = None
        prod["brand"] = self.get_brand(product_data)

        prod["available_qty"] = self.get_stock_quantity(product_data, response.url)
        prod["price"] = self.get_price(product_data)
        prod["price_compare"] = self.get_price_compare(response)

        prod["images"] = self.get_product_images(selector)

        prod["summary"] = self.get_summary(selector)
        if prod["summary"] is None:
            prod["summary"] = prod["title"] + ", " + prod["brand"]

        prod["description"] = self.get_description(selector)
        prod["description_en"] = None

        min_de_to_us_ship_days = 5  # need to check
        max_de_to_us_ship_days = 8  # need to check

        # Shop site send ship in 1 day plus ship to DE -> US
        prod["shipping_days_min"] = 1 + min_de_to_us_ship_days
        prod["shipping_days_max"] = 1 + max_de_to_us_ship_days

        prod["shipping_fee"] = self.get_shipping_fee(selector)

        prod["videos"] = self.get_videos(selector)

        prod["categories"] = self.get_categories(selector)
        prod["specifications"] = self.get_specifications(selector, response.url)

        prod["reviews"] = self.get_reviews(selector)
        prod["rating"] = self.get_rating(selector)

        prod["options"] = self.get_valid_options(selector)
        if prod["options"] is not None:
            prod["variants"] = self.get_variants(selector, prod["options"], response.url)
            prod["has_only_default_variant"] = False
        else:
            prod["variants"] = None
            prod["has_only_default_variant"] = True

        prod["sold_count"] = None

        if (
            not prod["images"]
            or prod["images"].find(
                "Bild_folgt_apohealth_Gesundheit_aus_der_Apotheke_0f0eb96c-a780-4831-b025-2ced5656decf.jpg"
            )
            > -1
        ):
            prod["existence"] = False

        if prod["available_qty"] == 0:
            prod["existence"] = False

        return prod
