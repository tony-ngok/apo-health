# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface

import json
import sys
import time

# from em_product.resources.pipelines import (
#     ESCategoryPipeline,
#     ESProductUrlPipeline,
#     ESProductPipeline,
#     ESProductRecrawlPipeline,
#     ESTranslationPipeline,
#     ESSeedProductPipeline,
# )
from itemadapter import ItemAdapter
import pymongo
from pymongo.errors import ConnectionFailure, NetworkTimeout
from scrapy import Spider
from scrapy.crawler import Crawler

from apo_health.pymongo_utils import ausverkaufte, bulk_write, get_uos


# class CategoryPipeline(ESCategoryPipeline):
#     ELASTICSEARCH_BUFFER_LENGTH = 1
#     CATEGORY_INDEX = "apo_health_categories"
#     ELASTICSEARCH_INDEX = CATEGORY_INDEX


# class ProductUrlPipeline(ESProductUrlPipeline):
#     FORCE = True
#     CATEGORY_INDEX = "apo_health_categories"
#     PRODUCT_URL_INDEX = "apo_health_product_urls"
#     ELASTICSEARCH_INDEX = PRODUCT_URL_INDEX


# class ProductPipeline(ESProductPipeline):
#     FORCE = True
#     PRODUCT_URL_INDEX = "apo_health_product_urls"
#     PRODUCT_INDEX = "apo_health_products"
#     ELASTICSEARCH_INDEX = PRODUCT_INDEX


# class SeedProductPipeline(ESSeedProductPipeline):
#     PRODUCT_URL_INDEX = "apo_health_product_urls"
#     PRODUCT_INDEX = "apo_health_products"
#     ELASTICSEARCH_INDEX = PRODUCT_INDEX


# class RecrawlProductPipeline(ESProductRecrawlPipeline):
#     PRODUCT_INDEX = "apo_health_products"
#     ELASTICSEARCH_INDEX = PRODUCT_INDEX
#     PRODUCT_ID_NAME = "product_id"


# class TranslationPipeline(ESTranslationPipeline):
#     TRANSLATION_INDEX = "apo_health_translation"
#     # ELASTICSEARCH_BUFFER_LENGTH = 5
#     ELASTICSEARCH_BUFFER_LENGTH = 1
#     ELASTICSEARCH_INDEX = TRANSLATION_INDEX


class MongoPipeLine:
    file_root = "Produkte{}.txt" # 临时存取抓到的批量数据
    
    def __init__(self, uri: str, batch_size: int, max_tries: int, days_bef: int):
        self.records = 0 # 抓取到的数据量
        self.batch_no = 0
        self.uri = uri
        self.batch_size = batch_size
        self.max_tries = max_tries
        self.errs = 0 # 记录数据库处理错误个数
        self.switch = False # 开始批量处理前关闭，写入数据库后打开
        self.days_bef = days_bef

    @classmethod
    def from_crawler(cls, crawler: Crawler):
        spider = cls(
            uri=crawler.settings.get("MONGO_URI"),
            batch_size=crawler.settings.getint("MONGO_BATCH_SIZE", 1000),
            max_tries=crawler.settings.getint("MONGO_MAX_TRIES", 10),
            days_bef = crawler.settings.getint("DAYS_BEF", 7)
        )
        return spider

    def open_spider(self, spider: Spider):
        for i in range(1, self.max_tries+1):
            try:
                self.client = pymongo.MongoClient(self.uri, serverSelectionTimeoutMS=60000)
                self.coll = self.client["apo_health"]["produkte"]
                print("Apohealth-Datenbank verbunden")
                return
            except (ConnectionFailure, NetworkTimeout) as c_err:
                spider.logger.error(f"{repr(c_err)} ({i}/{self.max_tries})")
                time.sleep(2)

        print("Fehler beim Verbinden zur Datenbank")
        # spider.crawler.engine.close_spider("MongoDB connexion fail")
        sys.exit(1)

    def process_item(self, item, spider: Spider):
        if self.switch:
            self.switch = False

        dat = ItemAdapter(item).asdict()
        self.records += 1
        
        # 连续写1000条记录到文件
        batchdatei = self.file_root.format(self.batch_no)
        with open(batchdatei, 'a', encoding='utf-8') as f:
            json.dumps(dat, f, ensure_ascii=False)
            f.write("\n")
        
        if self.records % self.batch_size == 0:
            self.batch_no += 1
            print("Stufe", self.batch_no)

            uos = get_uos(batchdatei)
            if bulk_write(uos, self.coll, self.max_tries):
                print("Stufe", self.batch_no, "erfolgreich")
            else:
                print("bulk_write Fehler")
                self.errs += 1
            self.switch = True

        return item

    def close_spider(self, spider: Spider):
        if not self.switch:
            self.batch_no += 1
            print("Stufe", self.batch_no)

            batchdatei = self.file_root.format(self.batch_no)
            uos = get_uos(batchdatei)
            if bulk_write(uos, self.coll, self.max_tries):
                print("Stufe", self.batch_no, "erfolgreich")
            else:
                print("bulk_write Fehler")
                self.errs += 1

        if not ausverkaufte(self.coll, self.max_tries, self.days_bef):
            print("Fehler bei den Ausverkauften")
            self.errs += 1

        self.client.close()
        sys.exit(1 if self.errs else 0)
