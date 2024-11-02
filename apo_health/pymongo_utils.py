import json
import os
import time
from datetime import datetime, timedelta

from pymongo import UpdateOne
from pymongo.collection import Collection
from pymongo.errors import ConnectionFailure, ExecutionTimeout, NetworkTimeout


def gen_uo(dat: dict):
    updates = {
        "date": dat["date"],
        "existence": dat["existence"],
        "price": dat["price"],
        "available_qty": dat["available_qty"]
    }

    dat.pop('date')
    dat.pop('existence')
    dat.pop('price')
    dat.pop('available_qty')

    query = { "_id": dat["product_id"] }
    return UpdateOne(query, {"$set": updates, "$setOnInsert": dat }, upsert=True)


def get_uos(dateiname: str):
    if os.path.exists(dateiname):
        with open(dateiname, 'r', encoding='utf-8') as f:
            ops = [gen_uo(json.loads(line.strip())) for line in f if line.strip()]
        return ops


def bulk_write(ops: list[UpdateOne], coll: Collection, max_tries: int) -> bool:
    for i in range(1, max_tries+1):
        try:
            bw = coll.bulk_write(ops)
            # print(bw)
            return True
        except (ConnectionFailure, ExecutionTimeout, NetworkTimeout) as op_f:
            print(f"({i}/{max_tries})", "Fehler beim Aktualisieren", str(op_f))
            time.sleep(2)
    return False


def ausverkaufte(coll: Collection, max_tries: int, d: int = 7) -> bool:
    """
    太久没更新的商品不删掉，标注为断货
    """

    jetzt = datetime.now()
    letzte_woche = (jetzt-timedelta(days=d)).strftime('%Y-%m-%dT%H:%M:%S')

    for i in range(1, max_tries+1):
        try:
            erg = coll.update_many(
                { "date": { "$lt": letzte_woche } },
                { "$set": {
                    "date": jetzt.strftime('%Y-%m-%dT%H:%M:%S'),
                    "existence": False,
                    "available_qty": 0
                }
                }
            )
            # print(erg)
            return True
        except Exception as e:
            print(f"({i}/{max_tries})", "Fehler beim Aktualisieren", str(e))
            time.sleep(2)
    return False
