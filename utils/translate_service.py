import logging
from langdetect import detect
import os
from pymongo import MongoClient


from wemakeprice.settings import MONGO_URI

# 设置日志格式
FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


def get_logger(name, log_file):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter(FORMAT))

    logger.addHandler(file_handler)

    return logger


log_file_path = os.path.join(os.path.expanduser("~"), "logs", "translator.log")
os.makedirs(os.path.dirname(log_file_path), exist_ok=True)
logger = get_logger(__name__, log_file_path)


def connect_to_mongo_by_collection(db_name, collection_name):
    client = MongoClient(MONGO_URI)
    db = client[db_name]
    collection = db[collection_name]
    return collection


def check_content_language(content, supported_languages):
    return detect(content) in supported_languages


def check_option_length(option):
    option_length_limit = 50
    return len(option) <= option_length_limit


def check_title_language(title, supported_languages):
    return check_content_language(title, supported_languages)


def check_option_language(option, supported_languages):
    return check_content_language(option, supported_languages)


def check_title_length(title):
    title_length_limit = 200
    return len(title) <= title_length_limit


def get_option_translation(translations):
    trans_opt = {}
    for doc in translations.find():
        trans_opt[doc["key"]] = doc["value"]
    return trans_opt


def get_translator(
    translation_service, total_count, supported_languages=None, translate_type="title"
):
    if total_count is None:
        raise Exception("No total count")

    if supported_languages is None:
        supported_languages = ["ko"]

    left_count = total_count
    translations = connect_to_mongo_by_collection("wemakeprice", "translations")
    translated_options = get_option_translation(translations)
    translate_service_count = 0

    def translate_title(title):
        nonlocal left_count
        if left_count < 0:
            raise Exception("You have use all of the translation service")
        else:
            left_count -= 1
            logger.info(f"{left_count} translation request left")

        if not check_title_language(title, supported_languages) or not check_title_length(title):
            raise Exception(f"language or length does not match [source]: {title}")

        try:
            to_translate = [title]
            result = None

            try:
                nonlocal translate_service_count
                translate_service_count += 1
                print(f"try to use translate service {translate_service_count}")
                result = translation_service.translate(to_translate)
            except ValueError:
                pass
            except Exception as e:
                pass

            if result is None:
                return

            title_translation = result[0]
            title_en = title_translation["translatedText"]

            return title_en
        except Exception as e:
            pass

    def translate_option(option):
        nonlocal left_count
        nonlocal translated_options
        if option in translated_options:
            return translated_options[option]

        if left_count < 0:
            raise Exception("You have use all of the translation service")
        else:
            left_count -= 1
            logger.info(f"{left_count} translation request left")

        if not check_option_language(option, supported_languages) or not check_title_length(option):
            raise Exception("language or length does not match")

        try:
            to_translate = [option]
            result = None

            try:
                nonlocal translate_service_count
                translate_service_count += 1
                print(f"try to use translate service {translate_service_count}")
                result = translation_service.translate(to_translate)
            except ValueError:
                pass
            except Exception as e:
                pass

            if result is None:
                return

            translation = result[0]

            translated_options[option] = translation["translatedText"]
            translations.insert_one({"key": option, "value": translation["translatedText"]})
            return translation["translatedText"]

        except Exception as e:
            pass

    if translate_type == "title":
        return translate_title
    elif translate_type == "option":
        return translate_option
    else:
        raise Exception(f"unsuppored translate type {translate_type}")
