# -*- coding: utf-8 -*-

from peewee import *


def to_upload(product, price_caculator):

    src_offer = {
        "price": round(float(product.get("price", 0)), 2),
        "currency": product.get("currency", "USD"),
    }
    product["cost_price"] = src_offer["price"]
    product["cost_currency"] = src_offer["currency"]
    offer = price_caculator.calc_offer(src_offer)
    if offer:
        product["price"] = offer["price"]
        product["quantity"] = offer["quantity"]
    else:
        product["price"] = 0
        product["quantity"] = 0

    if not product["variants"]:
        return product

    variants = []
    for variant in product["variants"]:
        src_offer = {
            "price": round(float(variant.get("price", 0)), 2),
            "currency": variant.get("currency", "USD"),
        }
        offer = price_caculator.calc_offer(src_offer)
        variant["cost_price"] = src_offer["price"]
        variant["cost_currency"] = src_offer["currency"]

        if offer and offer["price"]:
            variant["price"] = offer["price"]
            variant["quantity"] = offer["quantity"]
        else:
            variant["price"] = 0
            variant["quantity"] = 0

        if variant["quantity"]:
            variants.append(variant)

    product["variants"] = variants
    return product
