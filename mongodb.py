import json
import os
import time
from datetime import datetime, timedelta

# from bson.objectid import ObjectId
from pymongo import MongoClient, UpdateOne
from pymongo.errors import BulkWriteError, ConnectionFailure, NetworkTimeout

class ApohealthMongoDb:
    schluessel = "mongodb://mongouser:XSzY1nHbxi@34.172.204.102:27017"
    quelle = "Produkte.txt"
    MAX_VERSUCHE = 10 # 最大可尝试次数

    def __init__(self, batch_size: int = 1000):
        self.start = time.time()
        self.ops = [] # 存放批量操作数据
        # self.sess_id = str(ObjectId()) # 当前存放的数据ID
        self.batch_size = batch_size

    def connect(self) -> bool:
        for i in range(1, self.MAX_VERSUCHE+1):
            try:
                db = MongoClient(self.schluessel, serverSelectionTimeoutMS=60000)
                self.coll = db["apo_health"]["produkte_test"]
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

        dat.pop('date')
        dat.pop('existence')
        dat.pop('price')
        dat.pop('available_qty')

        query = { "_id": dat["product_id"] }
        return UpdateOne(query, {"$set": updates, "$setOnInsert": dat }, upsert=True)


    def bulk_write(self) -> bool:
        for i in range(1, self.MAX_VERSUCHE+1):
            try:
                bw = self.coll.bulk_write(self.ops)
                # print(bw)
                return True
            except BulkWriteError as op_f:
                print(f"({i}/{self.MAX_VERSUCHE})", "Fehler beim Aktualisieren", str(op_f))
                time.sleep(2)
        return False

    def ausverkaufte(self) -> bool:
        """
        太久没更新的商品不删掉，标注为断货
        """

        jetzt = datetime.now()
        letzte_woche = (jetzt-timedelta(days=7)).strftime('%Y-%m-%dT%H:%M:%S')

        for i in range(1, self.MAX_VERSUCHE+1):
            try:
                erg = self.coll.update_many(
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
                print(f"({i}/{self.MAX_VERSUCHE})", "Fehler beim Aktualisieren", str(e))
                time.sleep(2)
        return False


    def aktualisieren(self):
        if os.path.exists(self.quelle):
            switch = True # 操作完成
            stufe = 0
            with open(self.quelle, 'r', encoding='utf-8') as f:
                for i, line in enumerate(f):
                    # if i in {0, 101, 387}: # 随机跳过数据，测试断货更新
                    #     continue
                    if not (switch or self.ops):
                        switch = True

                    if line.strip():
                        dat = json.loads(line.strip())
                        self.ops.append(self.gen_uo(dat))

                    if len(self.ops) >= self.batch_size:
                        stufe += 1
                        print("Stufe", stufe)
                        if self.bulk_write():
                            switch = False
                            self.ops.clear()
                        else:
                            print("bulk_write Fehler")
                        print(f"Zeit: {time.time()-self.start:_.3f} s".replace(".", ",").replace("_", "."))

            if switch:
                print("Stufe", stufe+1)
                if not self.bulk_write():
                    print("bulk_write Fehler")
                print(f"Zeit: {time.time()-self.start:_.3f} s".replace(".", ",").replace("_", "."))

            if not self.ausverkaufte():
                print("Fehler")
            print(f"Zeit: {time.time()-self.start:_.3f} s".replace(".", ",").replace("_", "."))
        else:
            print("Keine Daten")


if __name__ == '__main__':
    md = ApohealthMongoDb()
    if md.connect():
        md.aktualisieren()
    print(f"Zeit: {time.time()-md.start:_.3f} s".replace(".", ",").replace("_", "."))
