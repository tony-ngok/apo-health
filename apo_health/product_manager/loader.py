from resources.product_manager.loader import ElasticSearchLoder


class ApoHealthElasticSearchLoder(ElasticSearchLoder):
    ELASTICSEARCH_INDEX = "apo_health_products"
    PRODUCT_INDEX = "apo_health_products"


class ApoHealthProductUrlElasticSearchLoder(ElasticSearchLoder):
    ELASTICSEARCH_INDEX = "apo_health_product_urls"
    PRODUCT_URL_INDEX = "apo_health_product_urls"


class TranslationElasticSearchLoder(ElasticSearchLoder):
    ELASTICSEARCH_BUFFER_LENGTH = 1
    TRANSLATION_INDEX = "apo_health_translation"
    ELASTICSEARCH_INDEX = "apo_health_translation"
