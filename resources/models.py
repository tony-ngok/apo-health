import os
from peewee import *
import json
from playhouse.shortcuts import ReconnectMixin
from urllib.parse import urlparse

from resources.settings import MYSQL_URI

database_proxy = Proxy()


class ReconnectMySQLDatabase(ReconnectMixin, MySQLDatabase):
    pass


def init_db():
    url = urlparse(MYSQL_URI)
    config = {
        "host": url.hostname,
        "port": url.port or 3306,
        "user": url.username,
        "password": url.password,
        "database": url.path.lstrip("/"),
    }

    db_connection = ReconnectMySQLDatabase(
        host=config.get("host"),
        user=config.get("user"),
        password=config.get("password"),
        database=config.get("database"),
    )
    database_proxy.initialize(db_connection)


init_db()


class BaseModel(Model):
    def __str__(self):
        r = {}
        for k in self._data.keys():
            try:
                r[k] = str(getattr(self, k))
            except:
                r[k] = json.dumps(getattr(self, k))
        return str(r)

    class Meta:
        database = database_proxy


class SpreeVariant(BaseModel):
    id = IntegerField()
    name = CharField()
    sku = CharField()
    cost_price = DecimalField(max_digits=10, decimal_places=2)
    created_at = DateTimeField()
    product_id = CharField()

    class Meta:
        table_name = "spree_variants"


class SpreePrice(BaseModel):
    id = IntegerField()
    variant_id = CharField()
    amount = DecimalField(max_digits=10, decimal_places=2)
    deleted_at = DateTimeField()

    class Meta:
        table_name = "spree_prices"


class SpreeProductSource(BaseModel):
    id = IntegerField()
    product_id = CharField()
    source = CharField()
    source_product_id = CharField()

    class Meta:
        table_name = "spree_product_sources"


class SpreeBlacklistKeywords(BaseModel):
    id = IntegerField()
    keywords = CharField()

    class Meta:
        table_name = "spree_blacklist_keywords"
