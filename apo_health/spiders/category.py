import scrapy
from scrapy.http import HtmlResponse


# scrapy crawl category
class CategorySpider(scrapy.Spider):
    name = "category"
    allowed_domains = ["www.apo-health.com"]
    start_urls = ["https://www.apo-health.com/"]
    kats_ausgabe = "Kategorien.txt"

    # custom_settings = {
    #     "ITEM_PIPELINES": {
    #         "apo_health.pipelines.CategoryPipeline": 400,
    #     }
    # }

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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.retry = False

    def start_requests(self):
        yield scrapy.Request(self.start_urls[0], headers=self.HEADERS,
                             callback=self.parse,
                             errback=self.errback)

    def errback(self, failure):
        self.logger.error(repr(failure))

    def parse(self, response: HtmlResponse):
        unterkats = response.css('nav.site-navigation a.navmenu-link-depth-3::attr(href)').getall()
        for uk in unterkats:
            self.write_cat(uk.split('/')[-1])

    def write_cat(self, kat: str):
        mod = 'a' if self.retry else 'w'
        with open(self.kats_ausgabe, mod, encoding='utf-8') as f_aus:
            f_aus.write(kat+'\n')
        if not self.retry:
            self.retry = True
