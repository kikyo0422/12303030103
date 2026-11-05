# -*- coding: utf-8 -*-
"""task2/init.py —— 第二题初始化脚本（与业务操作分开）

重置 exam_12303030103 的 inventory 和 orders 两个集合，
库存按本人参数 Stock = 5 + C = 8 写入。
运行：python init.py
"""
import sys

from pymongo import MongoClient

sys.stdout.reconfigure(encoding="utf-8")

SID = "12303030103"
S = 3
A = S % 3          # 0
B = S % 4          # 3
C = S % 5          # 3
STOCK = 5 + C      # 8
BUY = 1 + A        # 1

URI = "mongodb://127.0.0.1:27017/?replicaSet=rs0"
client = MongoClient(URI)
db = client["exam_" + SID]

db.inventory.delete_many({})
db.orders.delete_many({})
db.inventory.insert_one({
    "_id": "BOOK-" + SID,
    "title": "NoSQL数据库教材",
    "stock": STOCK
})

print("初始化完成：库存 = %d，订单数 = %d" % (STOCK, db.orders.count_documents({})))
client.close()
