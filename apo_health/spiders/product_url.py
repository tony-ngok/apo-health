import os

import scrapy
from scrapy.http import HtmlResponse


# scrapy crawl product-url
class ProductUrlSpider(scrapy.Spider):
    name = "product-url"
    allowed_domains = ["www.apo-health.com"]
    start_urls = []
    urls_ausgabe = "Produkt-URLs.txt"

    HEADERS = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "de-DE,de;q=0.9",
        "dnt": "1",
        "priority": "u=0, i",
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

    # custom_settings = {
    #     "DOWNLOADER_MIDDLEWARES": { # 每发送请求后，先经过中间件返回回答，然后将回答通过回调函数处理
    #         'apo_health.middlewares.SsgCatsErrsMiddleware': 543
    #     }
    # }

    def __init__(self, retry: bool = False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.errs = 0
        self.urls = {} # 品名：分类

        if not retry:
            kats_datei = "Kategorien.txt"
            if os.path.exists(kats_datei):
                with open(kats_datei, 'r', encoding='utf-8') as f_kats:
                    for line in f_kats:
                        if line.strip():
                            self.start_urls.append(line.strip())
            else:
                print("Datei fehlt:", kats_datei)

    def start_requests(self):
        for i, todo in enumerate(self.start_urls):
            url = 'https://www.apo-health.com/collections/'+todo
            headers = { **self.HEADERS, 'referer': 'https://www.apo-health.com/' }
            yield scrapy.Request(url, headers=headers,
                                 meta={ "cookiejar": i },
                                 callback=self.parse,
                                 errback=self.errback)

    def errback(self, failure):
        self.logger.error(repr(failure))
        self.errs += 1

    def parse(self, response: HtmlResponse, seite: int = 1):
        i = response.meta['cookiejar']
        print(f"{(i+1):_}/{len(self.start_urls):_}".replace("_", "."), response.url)
        kat = response.url.split('/')[-1]

        links = response.css('h2.productitem--title > a::attr(href)').getall()
        for l in links:
            pname = l.split('/')[-1]
            if pname not in self.urls:
                self.urls[pname] = kat
            
        weiter = response.css('li.pagination--next > a')
        if weiter:

