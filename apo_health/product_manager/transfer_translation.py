# from wemakeprice.pipelines import TranslationPipeline
# from wemakeprice.spiders.product import ProductSpider
# from scrapy.utils.project import get_project_settings
# from scrapy.utils.test import get_crawler

# from pymongo import MongoClient

# from wemakeprice.settings import MONGO_URI


# def connect_to_mongo_by_collection(db_name, collection_name):
#     client = MongoClient(MONGO_URI)
#     db = client[db_name]
#     collection = db[collection_name]
#     return collection


# def main():
#     db_name = "wemakeprice"
#     collection = connect_to_mongo_by_collection(db_name, "products")

#     settings = get_project_settings()
#     crawler = get_crawler(ProductSpider)
#     translation_pipeline = TranslationPipeline(settings)
#     spider = crawler._create_spider()
#     translation_pipeline.open_spider(spider)

#     query = {}
#     for doc in collection.find(query):
#         try:
#             if "title_en" not in doc:
#                 continue

#             translation = {
#                 "id": str(doc["_id"]),
#                 "title": doc["title"],
#                 "title_en": doc["title_en"],
#             }

#             translation_pipeline.process_item(translation, spider)
#         except Exception as e:
#             pass

#     translation_pipeline.close_spider(spider)


# if __name__ == "__main__":
#     main()
