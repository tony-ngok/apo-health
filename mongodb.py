import json
import os
import time

from bson.objectid import ObjectId
from pymongo import MongoClient, UpdateOne
from pymongo.errors import ConnectionFailure, NetworkTimeout, OperationFailure

class ApohealthMongoDb:
    schluessel = "mongodb://mongouser:XSzY1nHbxi@34.172.204.102:27017/apo_health"
    quelle = "Produkte.txt"
    MAX_VERSUCHE = 10 # 最大可尝试次数

    def __init__(self):
        self.ops = [] # 存放批量操作数据
        self.sess_id = str(ObjectId()) # 当前存放的数据ID

    def connect(self) -> bool:
        for i in range(1, self.MAX_VERSUCHE+1):
            try:
                db = MongoClient(self.schluessel, serverSelectionTimeoutMS=60000)
                self.coll = db["produkte"]
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
                self.coll.bulk_write(self.ops)
            except OperationFailure as op_f:
                print(f"({i}/{self.MAX_VERSUCHE})", "Fehler beim Aktualisieren", str(op_f))
                time.sleep(2)
        return False

    def aktualisieren(self):
        if os.path.exists(self.quelle):
            with open(self.quelle, 'r', encoding='utf-8') as f:
                beenden = False # 操作完成
                for line in enumerate(f):
                    if line.strip():
                        dat = json.loads(line.strip())
                        self.ops.append(self.gen_uo(dat))
                    
                    if len(self.ops) >= 1000:
                        self.bulk_write()
                    
        else:
            print("Keine Daten")


if __name__ == '__main__':
    ApohealthMongoDb()
