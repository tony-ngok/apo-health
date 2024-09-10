# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from datetime import datetime, timedelta
from itemadapter import ItemAdapter
import pymongo
from pymongo import MongoClient
from scrapy.exceptions import DropItem
from scrapy import Request
import logging
import json
import time

from elasticsearch import Elasticsearch
from elasticsearch import helpers
from elasticsearch.client import IndicesClient
from elasticsearch.exceptions import RequestError
from elasticsearch.exceptions import ConnectionTimeout
from elasticsearch.exceptions import ConnectionError
from elasticsearch.exceptions import SSLError
from elasticsearch.exceptions import TransportError, ElasticsearchException, NotFoundError
from elasticsearch.helpers.errors import BulkIndexError

from dropshipping.utils.es_service import es_retry
from .logger import get_logger

logger = get_logger(__name__, "app.log")


class Pipeline:
    def __init__(self, mongo_url, mongo_db):
        self.client = MongoClient(mongo_url)
        self.db = self.client[mongo_db]

    @classmethod
    def from_crawler(cls, crawler):
        crawler = cls(crawler.settings.get("MONGO_URI"), crawler.settings.get("MONGO_DATABASE"))
        return crawler

    def close_spider(self, spider):
        self.client.close()


class ElasticSearchPipeline:
    ELASTICSEARCH_BUFFER_LENGTH = 500
    ELASTICSEARCH_INDEX = None
    FORCE = False

    def __init__(self, settings, id_key=None):
        self.id_key = id_key
        self.max_retry = 3
        self.init_es_client(settings)
        self.items_buffer = []

    def init_es_client(self, settings):
        es_timeout = settings.get("ELASTICSEARCH_TIMEOUT", 60)
        es_servers = settings.get("ELASTICSEARCH_SERVERS", "localhost:9200")
        es_servers = es_servers if isinstance(es_servers, list) else [es_servers]

        es_settings = dict()
        es_settings["hosts"] = es_servers
        es_settings["timeout"] = es_timeout

        if settings.get("ELASTICSEARCH_USERNAME") and settings.get("ELASTICSEARCH_PASSWORD"):
            es_settings["http_auth"] = (
                settings["ELASTICSEARCH_USERNAME"],
                settings["ELASTICSEARCH_PASSWORD"],
            )

        self.es = Elasticsearch(**es_settings)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def update_item(self, item):
        index_name = item.pop("indice_name", self.ELASTICSEARCH_INDEX)
        update_action = dict()
        if "_id" in item:
            update_action["_id"] = item.pop("_id")
        else:
            if self.id_key is not None and self.id_key in item:
                update_action["_id"] = item[self.id_key]
        update_action.update(
            {
                "_index": index_name,
                "_type": "_doc",
                "_op_type": "update",
                "doc_as_upsert": True,
                "doc": dict(item),
            }
        )

        self.items_buffer.append(update_action)

        if len(self.items_buffer) >= self.ELASTICSEARCH_BUFFER_LENGTH:
            self.send_items()
            self.items_buffer = []

    def save_item(self, item, action="create"):
        item.pop("_id", None)
        index_name = item.pop("indice_name", self.ELASTICSEARCH_INDEX)
        index_action = {
            "_index": index_name,
            "_type": "_doc",
            "_op_type": action,
            "_source": dict(item),
        }

        if self.id_key is not None and self.id_key in item:
            index_action["_id"] = item[self.id_key]

        self.items_buffer.append(index_action)

        if len(self.items_buffer) >= self.ELASTICSEARCH_BUFFER_LENGTH:
            self.send_items()
            self.items_buffer = []

    def create_item(self, item):
        item.pop("_id", None)
        index_name = item.pop("indice_name", self.ELASTICSEARCH_INDEX)
        index_action = {
            "_index": index_name,
            "_type": "_doc",
            "_op_type": "create",
            "_source": dict(item),
        }

        if self.id_key is not None and self.id_key in item:
            index_action["_id"] = item[self.id_key]

        self.items_buffer.append(index_action)

        if len(self.items_buffer) >= self.ELASTICSEARCH_BUFFER_LENGTH:
            self.send_items()
            self.items_buffer = []

    def index_item(self, item):
        item.pop("_id", None)
        index_name = item.pop("indice_name", self.ELASTICSEARCH_INDEX)
        index_action = {
            "_index": index_name,
            "_type": "_doc",
            "_op_type": "index",
            "_source": dict(item),
        }

        if self.id_key is not None and self.id_key in item:
            index_action["_id"] = item[self.id_key]

        self.items_buffer.append(index_action)

        if len(self.items_buffer) >= self.ELASTICSEARCH_BUFFER_LENGTH:
            self.send_items()
            self.items_buffer = []

    def send_items(self):
        retry = self.max_retry
        while retry > 0:
            try:
                res = helpers.bulk(self.es, self.items_buffer)
                logging.info(f"[Items Saved]: {self.items_buffer}")
                break
            except (ConnectionTimeout, ConnectionError, SSLError, TransportError):
                time.sleep(retry)
                retry -= 1
                continue
            except RequestError as e:
                break
            except BulkIndexError as e:
                for error in e.errors:
                    for _, value in error.items():
                        try:
                            logging.exception(value["_id"])
                        except Exception as e:
                            pass
                break
            except Exception as e:
                raise e

    def process_item(self, item, spider):
        if isinstance(item, list):
            for each in item:
                self.process_item(each, spider)
        else:
            if self.FORCE:
                self.save_item(item, "index")
            else:
                self.save_item(item)
            logging.debug("Item has been sent to Elastic Search %s", self.ELASTICSEARCH_INDEX)

        return item

    def ensure_indice(self, indice_name):
        ic = IndicesClient(self.es)
        if ic.exists(indice_name):
            return True

        ic.create(indice_name, {"settings": {"index.mapping.total_fields.limit": 100000}})
        return ic.exists(indice_name)

    def close_spider(self, spider):
        if len(self.items_buffer):
            self.send_items()


class ESCategoryPipeline(ElasticSearchPipeline):
    CATEGORY_INDEX = None
    PRODUCT_URL_KEY_NAME = "url"

    def __init__(self, settings, id_key="id"):
        super(ESCategoryPipeline, self).__init__(settings, id_key)

    def load_category_urls(self):
        params = {
            "index": self.CATEGORY_INDEX,
            "doc_type": "_doc",
            "size": 500,
            "query": {"query": {"match_all": {}}},
        }
        wrapped_scan = es_retry(helpers.scan)
        try:
            for item in wrapped_scan(self.es, **params):
                if isinstance(item["_source"], dict):
                    record = item["_source"]
                else:
                    record = json.loads(item["_source"])
                logging.debug(record)

                yield record
        except Exception as e:
            logging.exception(e)

    def open_spider(self, spider):
        if not self.ELASTICSEARCH_INDEX:
            raise Exception("Please provide es index")

        self.ensure_indice(self.CATEGORY_INDEX)
        self.ensure_indice(self.ELASTICSEARCH_INDEX)
        for doc in self.load_category_urls():
            spider.start_urls.append(doc[self.PRODUCT_URL_KEY_NAME])

    def process_item(self, item, spider):
        if isinstance(item, list):
            for each in item:
                self.process_item(each, spider)
        else:
            self.save_item(item, "index")
            logging.debug("Item has been sent to Elastic Search %s", self.ELASTICSEARCH_INDEX)

        return item


class ESProductUrlPipeline(ESCategoryPipeline):
    def __init__(self, settings, id_key="id"):
        super(ESProductUrlPipeline, self).__init__(settings, id_key)


class ESProductPipeline(ElasticSearchPipeline):
    PRODUCT_URL_INDEX = None
    PRODUCT_INDEX = None
    PRODUCT_URL_ID_NAME = "id"
    PRODUCT_URL_KEY_NAME = "url"
    FORCE = False

    def __init__(self, settings):
        super(ESProductPipeline, self).__init__(settings, "product_id")

    def search_products(self, product_ids, key="product_id"):
        query = {"bool": {"filter": [{"terms": {key: product_ids}}]}}
        params = {
            "index": self.PRODUCT_INDEX,
            "from_": 0,
            "size": 500,
            "body": {"query": query},
        }

        resp = None
        retry = self.max_retry
        while retry > 0:
            try:
                resp = self.es.search(**params)
                break
            except NotFoundError as e:
                break
            except RequestError as e:
                raise e
            except ConnectionTimeout:
                time.sleep(1)
            except (TransportError, ElasticsearchException) as e:
                resp = -1
                retry -= 1

                status_code = getattr(e, "status_code", None)
                if status_code == "N/A":
                    time.sleep(3)
            except Exception as e:
                resp = -1
                retry -= 1

        if resp is None:
            result = None
        elif resp == -1:
            result = False
        else:
            result = dict()
            for item in resp["hits"]["hits"]:
                result.setdefault(item["_source"][key], [])
                result[item["_source"][key]].append(item["_source"])

        return result

    def load_product_urls(self):
        params = {
            "index": self.PRODUCT_URL_INDEX,
            "doc_type": "_doc",
            "size": 500,
            "query": {"query": {"match_all": {}}},
        }
        wrapped_scan = es_retry(helpers.scan)
        try:
            for item in wrapped_scan(self.es, **params):
                if isinstance(item["_source"], dict):
                    record = item["_source"]
                else:
                    record = json.loads(item["_source"])
                logging.debug(record)

                yield record
        except Exception as e:
            logging.exception(e)

    def get_urls(self, product_urls):
        if not self.FORCE:
            date_format = "%Y-%m-%dT%H:%M:%S"
            result = self.search_products(list(product_urls.keys()))

            if result:
                for id, product in result.items():
                    if "dtate" in product[0]:
                        try:
                            parsed_date = datetime.strptime(product[0]["dtate"], date_format)
                            if datetime.now() - parsed_date < timedelta(days=7):
                                product_urls.pop(id)
                        except Exception as e:
                            pass

                    elif "date" in product[0]:
                        try:
                            parsed_date = datetime.strptime(product[0]["date"], date_format)
                            if datetime.now() - parsed_date < timedelta(days=7):
                                product_urls.pop(id)
                        except Exception as e:
                            pass
                    else:
                        product_urls.pop(id)

        if product_urls:
            return [url for _, url in product_urls.items()]

    def open_spider(self, spider):
        if not self.ELASTICSEARCH_INDEX:
            raise Exception("Please provide es index")

        self.ensure_indice(self.ELASTICSEARCH_INDEX)
        batch_size = 500
        product_urls = dict()

        for doc in self.load_product_urls():
            if len(product_urls) < batch_size:
                product_urls[str(doc[self.PRODUCT_URL_ID_NAME])] = doc[self.PRODUCT_URL_KEY_NAME]
                continue

            urls = self.get_urls(product_urls)
            if urls:
                spider.start_urls.extend(urls)
            product_urls = {}

        if product_urls:
            urls = self.get_urls(product_urls)
            if urls:
                spider.start_urls.extend(urls)


class ESSeedProductPipeline(ElasticSearchPipeline):
    PRODUCT_URL_ID_NAME = "id"
    PRODUCT_URL_KEY_NAME = "url"
    FORCE = True

    def __init__(self, settings):
        super(ESSeedProductPipeline, self).__init__(settings, "product_id")

    def open_spider(self, spider):
        self.ensure_indice(self.ELASTICSEARCH_INDEX)


class ESProductRecrawlPipeline(ElasticSearchPipeline):
    PRODUCT_URL_INDEX = None
    PRODUCT_INDEX = None
    PRODUCT_URL_ID_NAME = "id"
    PRODUCT_URL_KEY_NAME = "url"

    def __init__(self, settings):
        super(ESProductRecrawlPipeline, self).__init__(settings, "product_id")

    def load_products(self):
        params = {
            "index": self.PRODUCT_INDEX,
            "doc_type": "_doc",
            "size": 500,
            "query": {"query": {"match_all": {}}},
        }
        wrapped_scan = es_retry(helpers.scan)
        try:
            for item in wrapped_scan(self.es, **params):
                if isinstance(item["_source"], dict):
                    record = item["_source"]
                else:
                    record = json.loads(item["_source"])
                logging.debug(record)

                yield record
        except Exception as e:
            logging.exception(e)

    def open_spider(self, spider):
        if not self.ELASTICSEARCH_INDEX:
            logger.exception("[Index Not Found] {self.ELASTICSEARCH_INDEX}")
            raise Exception("Please provide es index")

        if not self.PRODUCT_INDEX:
            logger.exception("[Index Not Found] {self.PRODUCT_INDEX}")
            raise Exception("Please provide product es index")

        for doc in self.load_products():
            if doc.get(self.PRODUCT_URL_KEY_NAME):
                spider.start_urls.append(doc[self.PRODUCT_URL_KEY_NAME])
            logger.debug("[Url Added] {doc[self.PRODUCT_URL_KEY_NAME]}")

    def process_item(self, item, spider):
        if isinstance(item, list):
            for each in item:
                self.process_item(each, spider)
        else:
            self.update_item(item)
            logging.debug("Item has been sent to Elastic Search %s", self.ELASTICSEARCH_INDEX)

        return item


class ESTranslationPipeline(ElasticSearchPipeline):
    PRODUCT_URL_INDEX = None
    PRODUCT_KEY_NAME = "id"
    TRANSLATION_INDEX = None

    def __init__(self, settings):
        self.translations = {}
        super(ESTranslationPipeline, self).__init__(settings, "id")

    def load_translation(self):
        params = {
            "index": self.TRANSLATION_INDEX,
            "doc_type": "_doc",
            "size": 500,
            "query": {"query": {"match_all": {}}},
        }
        wrapped_scan = es_retry(helpers.scan)
        try:
            for item in wrapped_scan(self.es, **params):
                if isinstance(item["_source"], dict):
                    record = item["_source"]
                else:
                    record = json.loads(item["_source"])
                logging.debug(record)

                yield record
        except Exception as e:
            logging.exception(e)

    def open_spider(self, spider):
        self.ensure_indice(self.TRANSLATION_INDEX)
        if not self.ELASTICSEARCH_INDEX:
            logger.exception("[Index Not Found] {self.ELASTICSEARCH_INDEX}")
            raise Exception("Please provide es index")

        if not self.TRANSLATION_INDEX:
            logger.exception("[Index Not Found] {self.PRODUCT_INDEX}")
            raise Exception("Please provide product es index")

        for doc in self.load_translation():
            if doc.get(self.PRODUCT_KEY_NAME):
                self.translations[self.PRODUCT_KEY_NAME] = doc

    def process_item(self, item, spider):
        if isinstance(item, list):
            for each in item:
                self.process_item(each, spider)
        else:
            self.create_item(item)
            logging.debug("Item has been sent to Elastic Search %s", self.ELASTICSEARCH_INDEX)

        return item
