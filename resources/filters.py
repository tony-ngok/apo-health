import re

from utils.site_product import fetch_source_ids, fetch_blacklist_keywords


def filters(product) -> bool:
    def is_food(product) -> bool:
        keywords = ["food", "drink", "bathrobe", "cotton"]
        keys = ["title", "brand", "categories"]
        for key in keys:
            if key not in product:
                continue
            if product[key] is None:
                continue

            for keyword in keywords:
                if keyword in product[key].lower():
                    return True

        return False

    def oversize(product) -> bool:
        if "weight" not in product:
            return False

        if product["weight"] is None:
            return False
        if product["weight"] > 3:
            return True
        return False

    def oversize_by_title(product) -> bool:
        pattern = r"(\d+(?:\.\d+)?)(g|kg|ml|l|L)(x\d+)?"
        match = re.search(pattern, product["title"])
        if not match:
            return False

        weight = float(match.group(1))
        unit = match.group(2)
        quantity = match.group(3)

        if unit in ["kg", "l", "L"]:
            weight_in_g = weight * 1000
        else:
            weight_in_g = weight

        if quantity:
            weight_in_g = weight_in_g * int(quantity.replace("x", ""))

        if weight_in_g > 800:
            return True
        else:
            return False

    blacklist_keywords = fetch_blacklist_keywords()

    def is_blacklist(product):
        for keyword in blacklist_keywords:
            if keyword.lower() in product["title"].lower():
                return True

        return False

    checklist = [is_food, oversize, oversize_by_title, is_blacklist]

    for check in checklist:
        if check(product) is True:
            return True

    return False


product_filer = filters
product_filter = filters


def doc_filer(doc):
    if (
        not doc
        or not doc.get("price")
        or not doc.get("images")
        or not doc.get("title")
        or doc.get("existence") is False
        or doc.get("options")
        or doc.get("variants")
        or doc.get("available_qty") == 0
    ):
        return True
