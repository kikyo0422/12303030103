# -*- coding: utf-8 -*-
"""task2/task2.py —— 第二题：MongoDB 原子扣减与事务验证

本人参数：SID=12303030103，S=3，A=0，B=3，C=3
          Stock=5+C=8，Buy=1+A=1
运行：python task2.py
"""
import sys
import uuid

from pymongo import MongoClient
from pymongo.errors import PyMongoError

sys.stdout.reconfigure(encoding="utf-8")

SID = "12303030103"
S = 3
A = S % 3
B = S % 4
C = S % 5
STOCK = 5 + C       # 8
BUY = 1 + A         # 1

URI = "mongodb://127.0.0.1:27017/?replicaSet=rs0"
DB_NAME = "exam_" + SID
BOOK_ID = "BOOK-" + SID

client = MongoClient(URI)
db = client[DB_NAME]
inventory = db["inventory"]
orders = db["orders"]


def reset(initial_stock):
    """每个测试场景开始前单独重置 inventory 和 orders。"""
    inventory.delete_many({})
    orders.delete_many({})
    inventory.insert_one({
        "_id": BOOK_ID,
        "title": "NoSQL数据库教材",
        "stock": initial_stock
    })


def place_order(request_id, force_error=False, quantity=BUY):
    """在同一个事务、同一个会话中完成库存扣减和订单插入。

    返回字典：
      success=True                    扣减并插入订单均成功且事务已提交
      category='库存不足或教材不存在'  matched_count == 0
      category='数据库执行异常'        抛出异常并已回滚
    """
    session = client.start_session()
    try:
        session.start_transaction()

        # 条件检查与扣减合并为一次单文档原子更新：
        # 只有库存 >= quantity 时才匹配并扣减，不会出现负库存。
        result = inventory.update_one(
            {"_id": BOOK_ID, "stock": {"$gte": quantity}},
            {"$inc": {"stock": -quantity}},
            session=session
        )

        # 以数据库返回的 matchedCount 判断是否扣减成功，而不是根据程序执行到哪一行。
        if result.matched_count != 1:
            session.abort_transaction()
            return {
                "success": False,
                "category": "库存不足或教材不存在",
                "matched_count": result.matched_count,
                "modified_count": result.modified_count
            }

        if force_error:
            # 扣减已成功，但在订单插入前主动抛出异常，用于验证事务回滚。
            raise RuntimeError("forceError=true：库存扣减后、订单插入前主动抛出异常")

        orders.insert_one({
            "_id": request_id,
            "bookId": BOOK_ID,
            "studentId": SID,
            "quantity": quantity
        }, session=session)

        # 只有 commit 成功返回后，才返回订购成功。
        session.commit_transaction()
        return {
            "success": True,
            "category": "扣减成功",
            "matched_count": result.matched_count,
            "modified_count": result.modified_count
        }

    except (PyMongoError, RuntimeError) as exc:
        if session.in_transaction:
            session.abort_transaction()
        return {
            "success": False,
            "category": "数据库执行异常",
            "error": str(exc)
        }
    finally:
        session.end_session()


def run_scenario(name, initial_stock, attempts, force_error=False):
    """运行一个测试场景，并依据本人参数计算预期值、与实际结果比较。"""
    reset(initial_stock)

    succeeded = 0
    failed = 0
    last_failure = None

    for i in range(attempts):
        # 每次订购使用不同的唯一请求编号
        request_id = "%s-%02d-%s" % (name, i + 1, uuid.uuid4().hex[:8])
        outcome = place_order(request_id, force_error=force_error)
        if outcome["success"]:
            succeeded += 1
        else:
            failed += 1
            last_failure = outcome

    final_stock = inventory.find_one({"_id": BOOK_ID})["stock"]
    final_orders = orders.count_documents({})

    # 预期值由本人参数计算得到：
    if force_error:
        expected_success = 0
    elif initial_stock < BUY:
        expected_success = 0
    else:
        expected_success = min(attempts, initial_stock // BUY)
    expected_failed = attempts - expected_success
    expected_stock = initial_stock - expected_success * BUY
    expected_orders = expected_success

    passed = (
        succeeded == expected_success
        and failed == expected_failed
        and final_stock == expected_stock
        and final_orders == expected_orders
    )

    print("%s | 初始库存=%d | 购买数量=%d | 成功次数=%d | 失败次数=%d | "
          "最终库存=%d | 最终订单数量=%d | 核验=%s"
          % (name, initial_stock, BUY, succeeded, failed,
             final_stock, final_orders, "PASS" if passed else "FAIL"))
    if last_failure and name == "T3":
        print("  T3 失败原因：%s（%s）" % (last_failure["category"], last_failure.get("error", "")))
    return passed


def main():
    print("本人参数：SID=%s，S=%d，A=%d，B=%d，C=%d，Stock=%d，Buy=%d"
          % (SID, S, A, B, C, STOCK, BUY))
    print("场景 | 初始库存 | 购买数量 | 成功次数 | 失败次数 | 最终库存 | 最终订单数量 | 核验")

    results = []
    # T1 正常订购：初始库存 Stock，执行一次正常订购
    results.append(run_scenario("T1", STOCK, 1))
    # T2 库存不足：初始库存 Buy-1，执行一次正常订购
    results.append(run_scenario("T2", BUY - 1, 1))
    # T3 中途异常：初始库存 Stock，forceError=true
    results.append(run_scenario("T3", STOCK, 1, force_error=True))
    # T4 连续购买：初始库存 Stock，连续发起 floor(Stock/Buy)+1 次正常订购
    results.append(run_scenario("T4", STOCK, STOCK // BUY + 1))

    print("全部场景核验：%s" % ("PASS" if all(results) else "FAIL"))


if __name__ == "__main__":
    try:
        main()
    finally:
        client.close()
