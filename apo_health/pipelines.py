# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface

from em_product.resources.pipelines import (
    ESCategoryPipeline,
    ESProductUrlPipeline,
    ESProductPipeline,
    ESProductRecrawlPipeline,
    ESTranslationPipeline,
    ESSeedProductPipeline,
)


class CategoryPipeline(ESCategoryPipeline):
    ELASTICSEARCH_BUFFER_LENGTH = 1
    CATEGORY_INDEX = "apo_health_categories"
    ELASTICSEARCH_INDEX = CATEGORY_INDEX


class ProductUrlPipeline(ESProductUrlPipeline):
    FORCE = True
    CATEGORY_INDEX = "apo_health_categories"
    PRODUCT_URL_INDEX = "apo_health_product_urls"
    ELASTICSEARCH_INDEX = PRODUCT_URL_INDEX


class ProductPipeline(ESProductPipeline):
    FORCE = True
    PRODUCT_URL_INDEX = "apo_health_product_urls"
    PRODUCT_INDEX = "apo_health_products"
    ELASTICSEARCH_INDEX = PRODUCT_INDEX


class SeedProductPipeline(ESSeedProductPipeline):
    PRODUCT_URL_INDEX = "apo_health_product_urls"
    PRODUCT_INDEX = "apo_health_products"
    ELASTICSEARCH_INDEX = PRODUCT_INDEX


class RecrawlProductPipeline(ESProductRecrawlPipeline):
    PRODUCT_INDEX = "apo_health_products"
    ELASTICSEARCH_INDEX = PRODUCT_INDEX
    PRODUCT_ID_NAME = "product_id"


class TranslationPipeline(ESTranslationPipeline):
    TRANSLATION_INDEX = "apo_health_translation"
    # ELASTICSEARCH_BUFFER_LENGTH = 5
    ELASTICSEARCH_BUFFER_LENGTH = 1
    ELASTICSEARCH_INDEX = TRANSLATION_INDEX
