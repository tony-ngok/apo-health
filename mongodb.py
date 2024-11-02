import json
import os
import time
from datetime import datetime, timedelta

from bson.objectid import ObjectId
from pymongo import MongoClient, UpdateOne
from pymongo.errors import ConnectionFailure, NetworkTimeout, OperationFailure

class ApohealthMongoDb:
    schluessel = "mongodb://mongouser:XSzY1nHbxi@34.172.204.102:27017"
    quelle = "Produkte.txt"
    MAX_VERSUCHE = 10 # 最大可尝试次数

    def __init__(self):
        self.ops = [] # 存放批量操作数据
        self.sess_id = str(ObjectId()) # 当前存放的数据ID

    def connect(self) -> bool:
        for i in range(1, self.MAX_VERSUCHE+1):
            try:
                db = MongoClient(self.schluessel, serverSelectionTimeoutMS=60000)
                self.coll = db["apo_health"]["produkte"]
                print("Apohealth-Datenbank verbunden")
                return True
            except (ConnectionFailure, NetworkTimeout) as c_err:
                print(f"({i}/{self.MAX_VERSUCHE})", "Fehler beim Verbinden zur Apohealth-Datenbank:", str(c_err))
                time.sleep(2)
        return False

    def gen_uo(self, dat: dict) -> UpdateOne:
        updates = {
            "date": dat["date"],
            "existence": dat["existence"],
            "price": dat["price"],
            "available_qty": dat["available_qty"]
        }
        query = { "product_id": dat["product_id"] }
        return UpdateOne(query, {"$set": updates, "$setOnInsert": dat }, upsert=True)

    def bulk_write(self) -> bool:
        for i in range(1, self.MAX_VERSUCHE+1):
            try:
                bw = self.coll.bulk_write(self.ops)
                print(bw)
            except OperationFailure as op_f:
                print(f"({i}/{self.MAX_VERSUCHE})", "Fehler beim Aktualisieren", str(op_f))
                time.sleep(2)
        return False

    def aktualisieren(self):
        if os.path.exists(self.quelle):
            switch = True # 操作完成
            with open(self.quelle, 'r', encoding='utf-8') as f:
                for i, line in enumerate(f):
                    if not (switch or self.ops):
                        switch = True

                    if line.strip():
                        dat = json.loads(line.strip())
                        self.ops.append(self.gen_uo(dat))
                    
                    if len(self.ops) >= 1000:
                        if self.bulk_write():
                            switch = False
                            self.ops.clear()

            if switch:
                if not self.bulk_write():
                    print("bulk_write Fehler")

            jetzt = datetime.now()
            letzte_woche = (jetzt-timedelta(days=7)).strftime('%Y-%m-%dT%H:%M:%S')
            self.coll.update_many(
                { "date": { "$lt": letzte_woche } },
                { "$set": {
                    "date": jetzt.strftime('%Y-%m-%dT%H:%M:%S'),
                    "existence": False,
                    "available_qty": 0
                }
                }
            )

        else:
            print("Keine Daten")


if __name__ == '__main__':
    ApohealthMongoDb()
