# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
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

from dropshipping.utils.es_service import es_retry


class ElasticSearchLoder:
    ELASTICSEARCH_BUFFER_LENGTH = 1000
    ELASTICSEARCH_INDEX = None
    PRODUCT_INDEX = None
    TRANSLATION_INDEX = None
    PRODUCT_URL_INDEX = None

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

    def save_item(self, item, action="index"):
        index_name = item.pop("indice_name", self.ELASTICSEARCH_INDEX)
        index_action = dict()
        if "_id" in item:
            index_action["_id"] = item.pop("_id")
        else:
            if self.id_key is not None and self.id_key in item:
                index_action["_id"] = item[self.id_key]

        if action == "index":
            index_action.update(
                {
                    "_index": index_name,
                    "_type": "_doc",
                    "_op_type": action,
                    "_source": dict(item),
                }
            )
        elif action == "update":
            index_action.update(
                {
                    "_index": index_name,
                    "_type": "_doc",
                    "_op_type": action,
                    "doc": dict(item),
                }
            )

        self.items_buffer.append(index_action)

        if len(self.items_buffer) >= self.ELASTICSEARCH_BUFFER_LENGTH:
            self.send_items()
            self.items_buffer = []

    def send_items(self):
        helpers.bulk(self.es, self.items_buffer)
        retry = self.max_retry
        while retry > 0:
            try:
                helpers.bulk(self.es, self.items_buffer)
                break
            except (ConnectionTimeout, ConnectionError, SSLError, TransportError):
                time.sleep(retry)
                retry -= 1
                continue
            except RequestError as e:
                break
            except Exception as e:
                raise e

    def ensure_indice(self, indice_name):
        ic = IndicesClient(self.es)
        if ic.exists(indice_name):
            return True

        ic.create(indice_name, {"settings": {"index.mapping.total_fields.limit": 100000}})
        return ic.exists(indice_name)

    def search_content(self, ids, content_type="product"):
        index = self.PRODUCT_INDEX
        match content_type:
            case "product":
                index = self.PRODUCT_INDEX
            case "translation":
                index = self.TRANSLATION_INDEX
            case "_":
                raise Exception("content type not supped")

        query = {"terms": {"_id": ids}}
        params = {
            "index": index,
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
                result.setdefault(item["_id"], [])
                result[item["_id"]].append(item["_source"])

        return result

    def search_products(self, product_ids):
        query = {"terms": {"_id": product_ids}}
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
                result.setdefault(item["_id"], [])
                result[item["_id"]].append(item["_source"])

        return result

    def load_content(self, type="product", query=None):
        index_name = None
        match type:
            case "product":
                index_name = self.PRODUCT_INDEX
            case "translation":
                index_name = self.TRANSLATION_INDEX
            case "product_url":
                index_name = self.PRODUCT_URL_INDEX
            case "_":
                raise Exception("provide type")
        if index_name is None:
            raise Exception("provide type")

        params = {
            "index": index_name,
            "doc_type": "_doc",
            "size": 500,
            "query": {"query": {"match_all": {}}},
            "_source": True,
        }
        if query is not None:
            params["query"].update(query)

        wrapped_scan = es_retry(helpers.scan)
        try:
            for item in wrapped_scan(self.es, **params):
                if isinstance(item["_source"], dict):
                    record = item["_source"]
                else:
                    record = json.loads(item["_source"])
                record["_id"] = item["_id"]
                logging.debug(record)

                yield record
        except Exception as e:
            logging.exception(e)
