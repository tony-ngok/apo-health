import json
import os
from datetime import datetime

import requests
from bs4 import BeautifulSoup
import scrapy
from scrapy.http import HtmlResponse


class ProductSpider(scrapy.Spider):
    name = "product"
    allowed_domains = ["apo-health.com"]
    start_urls = []
    # prods_ausgabe = "Produkte.txt"

    HEADERS = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "accept-language": "de-DE,de;q=0.9",
        "dnt": "1",
        "priority": "u=0, i",
        "referer": "https://www.google.de/",
        "sec-ch-ua": "\"Chromium\";v=\"130\", \"Microsoft Edge\";v=\"130\", \"Not?A_Brand\";v=\"99\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "none",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0"
    }

    custom_settings = {
        "ITEM_PIPELINES": {
            "apo_health.pipelines.MongoPipeLine": 400,
        }
    }

    def __init__(self, retry: bool = False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.retry = retry
        self.errs = 0

        if not retry:
            urls_datei = "Produkt-URLs.txt"
            if os.path.exists(urls_datei):
                with open(urls_datei, 'r', encoding='utf-8') as f_urls:
                    for line in f_urls:
                        if line.strip():
                            self.start_urls.append(line.strip())
            else:
                print("Datei fehlt:", urls_datei)

        # https://open.er-api.com/v6/latest/EUR
        self.eur_rate = 1.084795

        # 获取实时汇率（测试中不用）
        try:
            exch = requests.get('https://open.er-api.com/v6/latest/EUR')
            if exch.ok:
                self.eur_rate = exch.json()['rates']['USD']
            else:
                raise Exception(f'Status {exch.status_code}')
        except Exception as e:
            print(f"Aktueller EUR/USD-Wechselkurs nicht erhalten ({str(e)})")
        finally:
            print(f"EUR/USD: {self.eur_rate}".replace(".", ","))

    def start_requests(self):
        for i, todo in enumerate(self.start_urls):
            kat, pname = todo.split()
            url = f'https://www.apo-health.com/collections/{kat}/products/{pname}'
            yield scrapy.Request(url, headers=self.HEADERS,
                                 meta={ "cookiejar": i },
                                 callback=self.parse,
                                 errback=self.errback)

    def errback(self, failure):
        self.logger.error(f"{failure.request.url}: {repr(failure)}")
        self.errs += 1

    def get_prod_data(self, response: HtmlResponse):
        scr_text = response.css('script[data-section-type="static-product"]::text').get()
        if scr_text:
            return json.loads(scr_text).get('product')

    def get_exist(self, response: HtmlResponse):
        return 'http://schema.org/InStock' in response.text

    def format_descr(self, raw_descr: str):
        descr = ""

        soup = BeautifulSoup(raw_descr, 'html.parser')
        for h3, li in zip(["Übersicht", "Details", "Inhalt"], soup.select('ul.tabs-content > li')):
            li_cont = ""
            for c in li.children:
                if c.name and (c.get_text(strip=True) or (c.name == 'br')): # 保留所有非空或换行符标签
                    cont = str(c).replace('/>', '>')
                    if h3 == 'Details': # 净化细节
                        conts = [cc for cc in cont.split('<br><br>')
                                 if not (('zuletzt überarbeitet' in cc) or (('Quelle: ' in cc) and ('Stand: ' in cc)))]
                        cont = "<br><br>".join(conts)

                    li_cont += cont
                elif isinstance(c, str): # 文字内容
                    li_cont += c

            li_cont = " ".join(li_cont.strip().split())
            if li_cont:
                descr += f"<h3>{h3}</h3><div>{li_cont}</div>"

        return f'<div class="apohealth-descr">{descr}</div>' if descr else None

    def get_brand(self, data: dict):
        brand = data.get("vendor")
        if brand and (brand != 'Nicht vorhanden'):
            return brand

    def get_category(self, response: HtmlResponse):
        breadcrumb = response.css('nav.breadcrumbs-container > a::text').getall()
        if len(breadcrumb) >= 2:
            return breadcrumb[1].strip()

    def get_images(self, img_list: list[str]):
        return ";".join(['https:'+img.split('?')[0] for img in img_list if 'Bild_folgt' not in img])

    def parse(self, response: HtmlResponse):
        i = response.meta["cookiejar"]
        print(f"{(i+1):_}/{len(self.start_urls):_}".replace("_", "."), response.url)

        if response.status == 404:
            print(f"{(i+1):_}/{len(self.start_urls):_}".replace("_", "."), "Produkt nicht gefunden")
            return

        data = self.get_prod_data(response)
        if not data:
            print("Keine Produktdaten")
            return

        images = self.get_images(data.get('images', []))
        if not images:
            print("Keine Bilder")
            return

        product_id = str(data["id"])
        existence = self.get_exist(response)
        categories = self.get_category(response)

        raw_descr = data.get("description") or ""
        description = self.format_descr(raw_descr)

        unique_var = data.get("variants", [{}])[0]
        sku = unique_var.get("sku", product_id)
        upc = unique_var.get("barcode") or None
        weight = round(unique_var["weight"]/453.59237, 2) if isinstance(unique_var.get("weight"), (int, float)) else None

        item = {
            "date": datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
            "url": response.url,
            "source": "apohealth",
            "product_id": product_id,
            "existence": existence,
            "title": data["title"],
            "title_en": None,
            "description": description,
            "description_en": None,
            "summary": None,
            "sku": sku,
            "upc": upc,
            "brand": self.get_brand(data),
            "specifications": None,
            "categories": categories,
            "images": images,
            "videos": None,
            "price": round(data["price"]*self.eur_rate/100.0, 2),
            "available_qty": None if existence else 0,
            "options": None,
            "variants": None,
            "has_only_default_variant": True,
            "returnable": False,
            "reviews": None,
            "rating": None,
            "sold_count": None,
            "shipping_fee": 0.00, # 网页上缺少邮费信息
            "shipping_days_min": 1, # https://www.apo-health.com/pages/faq
            "shipping_days_max": 2,
            "weight": weight,
            "length": None,
            "width": None,
            "height": None,
        }
        # self.write_prod(item)
        yield item

    # def write_prod(self, item: dict):
    #     mod = 'a' if self.retry else 'w'
    #     with open(self.prods_ausgabe, mod, encoding='utf-8') as f_aus:
    #         json.dump(item, f_aus, ensure_ascii=False)
    #         f_aus.write("\n")
    #     if not self.retry:
    #         self.retry = True
