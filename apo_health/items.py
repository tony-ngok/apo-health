# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ProductUrlItem(scrapy.Item):
    _id = scrapy.Field()
    id = scrapy.Field()
    name = scrapy.Field()
    url = scrapy.Field()
    date = scrapy.Field()


class CategoryUrlItem(scrapy.Item):
    _id = scrapy.Field()
    id = scrapy.Field()
    name = scrapy.Field()
    url = scrapy.Field()
    date = scrapy.Field()


class ProductItem(scrapy.Item):
    _id = scrapy.Field()
    date = scrapy.Field()
    url = scrapy.Field()
    source = scrapy.Field()
    product_id = scrapy.Field()
    existence = scrapy.Field()
    title = scrapy.Field()
    title_en = scrapy.Field()
    description = scrapy.Field()
    description_en = scrapy.Field()
    summary = scrapy.Field()
    sku = scrapy.Field()
    upc = scrapy.Field()
    brand = scrapy.Field()
    specifications = scrapy.Field()
    categories = scrapy.Field()
    images = scrapy.Field()
    videos = scrapy.Field()
    price = scrapy.Field()
    available_qty = scrapy.Field()
    options = scrapy.Field()
    variants = scrapy.Field()
    returnable = scrapy.Field()
    reviews = scrapy.Field()
    rating = scrapy.Field()
    sold_count = scrapy.Field()
    shipping_fee = scrapy.Field()
    shipping_days_min = scrapy.Field()
    shipping_days_max = scrapy.Field()
    weight = scrapy.Field()
    width = scrapy.Field()
    height = scrapy.Field()
    length = scrapy.Field()
    has_only_default_variant = scrapy.Field()
    data = scrapy.Field()
