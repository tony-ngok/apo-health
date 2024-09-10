from resources.models import SpreeProductSource, SpreeVariant, SpreePrice, SpreeBlacklistKeywords


def fetch_blacklist_keywords():
    query = SpreeBlacklistKeywords.select(SpreeBlacklistKeywords.keywords)

    return {item.keywords for item in query}


def fetch_source_ids(sources_name, is_sample=False):
    if is_sample:
        query = (
            SpreeProductSource.select(SpreeProductSource.source_product_id)
            .where(SpreeProductSource.source.in_(sources_name))
            .order_by(SpreeProductSource.id.desc())
            .limit(10)
        )

    else:
        query = (
            SpreeProductSource.select(SpreeProductSource.source_product_id)
            .where(SpreeProductSource.source.in_(sources_name))
            .order_by(SpreeProductSource.id.desc())
        )

    return {item.source_product_id for item in query}


def get_variants(variant_ids):
    return SpreeVariant.select(SpreeVariant.product_id).where(SpreeVariant.id.in_(variant_ids))


def get_variant_ids_by_price(price, page, batch_size):
    query = (
        SpreePrice.select(SpreePrice.variant_id)
        .where(SpreePrice.amount > price)
        .order_by(SpreePrice.id)
        .paginate(page, batch_size)
    )
    return [spree_price.variant_id for spree_price in query]


if __name__ == "__main__":
    price = 500
    page = 0
    batch_size = 1000
    with open("product_id_0810.txt", "w") as file:
        while True:
            variant_ids = get_variant_ids_by_price(price, page, batch_size)
            if not variant_ids:
                break
            variants = get_variants(variant_ids)

            for variant in variants:
                file.write(variant.product_id + "\n")
            page += 1
