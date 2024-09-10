import json
import unittest
from scrapy.utils.test import get_crawler
from scrapy.http import Request, Response, HtmlResponse
from apo_health.spiders.product_url import ProductUrlSpider

from apo_health.pipelines import ProductPipeline, ProductUrlPipeline
from scrapy.utils.project import get_project_settings
from urllib.parse import urlparse


class Testproduct_url(unittest.TestCase):
    def setUp(self):
        self.crawler = get_crawler(ProductUrlSpider)
        self.spider = self.crawler._create_spider()

        settings = get_project_settings()
        self.product_url_pipeline = ProductUrlPipeline(settings)
        self.product_url_pipeline.open_spider(self.spider)

    def tearDown(self):
        self.product_url_pipeline.close_spider(self.spider)

    def test_product_url(self):
        url = "https://www.apo-health.com/en-us/beauty/skincare"
        body = None
        with open("apo_health_test/pages/collections.html", "rb") as file:
            body = file.read()
        response = HtmlResponse(
            url=url,
            body=body,
        )
        result = list(self.spider.parse(response))
        for url_item in result:
            self.product_url_pipeline.process_item(url_item, self.spider)


if __name__ == "__main__":
    unittest.main()
