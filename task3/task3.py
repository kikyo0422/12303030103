# -*- coding: utf-8 -*-
"""task3/task3.py —— 第三题：Redis 学习信息与排行榜

连接实验五搭建的“三主三从”Redis Cluster（30103-30108）。
本人参数：SID=12303030103，S=3，C=3，本人成绩 = 70 + C = 73。
所有键统一使用前缀 exam:12303030103:
运行：python task3.py
"""
import sys
import time

from redis.cluster import RedisCluster

sys.stdout.reconfigure(encoding="utf-8")

SID = "12303030103"
S = 3
C = S % 5              # 3
MY_SCORE = 70 + C      # 73

PREFIX = "exam:" + SID + ":"
STUDENT_KEY = PREFIX + "student"
COMPLETED_KEY = PREFIX + "completed"
RANK_KEY = PREFIX + "rank"
SESSION_KEY = PREFIX + "session"

r = RedisCluster(host="127.0.0.1", port=30103, decode_responses=True)


def fmt_score(score):
    """把 redis 返回的浮点分数显示为整数（能整除时）。"""
    score = float(score)
    return int(score) if score.is_integer() else score


print("=== 1. 学生信息维护（Hash）===")
r.delete(STUDENT_KEY)
added = r.hset(STUDENT_KEY, mapping={
    "studentId": SID,
    "name": "张三",
    "className": "123030301",
    "courseId": "COURSE-" + SID + "-01",
    "status": "learning"
})
print("HSET 新建字段数 = %d" % added)
r.hset(STUDENT_KEY, "status", "completed")
print("HGET name = %s" % r.hget(STUDENT_KEY, "name"))
print("HGET status = %s" % r.hget(STUDENT_KEY, "status"))
print("HGETALL 完整Hash：")
for k, v in r.hgetall(STUDENT_KEY).items():
    print("  %s = %s" % (k, v))

print("=== 2. 已完成章节记录（Set）===")
r.delete(COMPLETED_KEY)
for chapter in ["CH01", "CH02", "CH02", "CH03"]:
    r.sadd(COMPLETED_KEY, chapter)
    print("提交 %s 后已完成章节数量 = %d" % (chapter, r.scard(COMPLETED_KEY)))
members = sorted(r.smembers(COMPLETED_KEY))
print("最终全部章节 = %s" % members)
print("CH02 是否已完成 = %s，CH04 是否已完成 = %s"
      % (bool(r.sismember(COMPLETED_KEY, "CH02")), bool(r.sismember(COMPLETED_KEY, "CH04"))))
before = r.scard(COMPLETED_KEY)
add_ret = r.sadd(COMPLETED_KEY, "CH02")
after = r.scard(COMPLETED_KEY)
print("重复提交 CH02：SADD 返回 %d，数量 %d -> %d" % (add_ret, before, after))

print("=== 3. 成绩排行榜（Sorted Set）===")
r.delete(RANK_KEY)
r.zadd(RANK_KEY, {
    "Student:" + SID: MY_SCORE,
    "demo:01": 85,
    "demo:02": 90,
    "demo:03": 60,
    "demo:04": 80
})


def show_top3():
    rows = r.zrevrange(RANK_KEY, 0, 2, withscores=True)
    text = "，".join("%s=%s" % (m, fmt_score(s)) for m, s in rows)
    print("前3名（从高到低）：" + text)


show_top3()
new_score = r.zincrby(RANK_KEY, 20, "Student:" + SID)
print("本人分数增加20分后 = %s" % fmt_score(new_score))
show_top3()
my_score = r.zscore(RANK_KEY, "Student:" + SID)
my_rank = r.zrevrank(RANK_KEY, "Student:" + SID)
print("本人更新后的分数 = %s，名次 = 第%d名" % (fmt_score(my_score), my_rank + 1))

print("=== 4. 会话生命周期（String + 过期）===")
session_value = "sess-" + SID + "-20261105"
r.set(SESSION_KEY, session_value, ex=5)
print("创建后：键值 = %s，TTL = %d，TYPE = %s"
      % (r.get(SESSION_KEY), r.ttl(SESSION_KEY), r.type(SESSION_KEY)))
print("等待 6 秒……")
time.sleep(6.2)
exists = r.exists(SESSION_KEY)
ttl = r.ttl(SESSION_KEY)
print("6秒后：EXISTS = %d，TTL = %d" % (exists, ttl))
print("过期验证：%s" % ("通过" if exists == 0 and ttl == -2 else "未通过"))

print("=== 5. 数据类型核验与说明 ===")
# 会话键已过期，重新创建一次以便在过期前检查其类型
r.set(SESSION_KEY, session_value, ex=5)
print("%s -> %s" % (STUDENT_KEY, r.type(STUDENT_KEY)))
print("%s -> %s" % (COMPLETED_KEY, r.type(COMPLETED_KEY)))
print("%s -> %s" % (RANK_KEY, r.type(RANK_KEY)))
print("%s -> %s" % (SESSION_KEY, r.type(SESSION_KEY)))
r.delete(SESSION_KEY)

r.close()
