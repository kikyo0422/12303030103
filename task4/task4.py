# -*- coding: utf-8 -*-
"""task4/task4.py —— 第四题（选做）：Redis Pipeline 与性能比较

本人参数：SID=12303030103，S=3，C=3
          N = 1000 + 100*C + S = 1303，每批最多 Q = 100 条。
键：exam:12303030103:seq:<i> / exam:12303030103:pipe:<i>，i 从 1 到 N。
运行：python task4.py
"""
import sys
import time

from redis.cluster import RedisCluster

sys.stdout.reconfigure(encoding="utf-8")

SID = "12303030103"
S = 3
C = S % 5
N = 1000 + 100 * C + S      # 1303
Q = 100

PREFIX = "exam:" + SID + ":"
SEQ_PREFIX = PREFIX + "seq:"
PIPE_PREFIX = PREFIX + "pipe:"

r = RedisCluster(host="127.0.0.1", port=30103, decode_responses=True)


def cleanup():
    """清理本人前缀下的旧键，保证每次运行结果可复现。"""
    for pattern in (SEQ_PREFIX + "*", PIPE_PREFIX + "*"):
        keys = list(r.scan_iter(match=pattern, count=500))
        for i in range(0, len(keys), 500):
            r.delete(*keys[i:i + 500])


def verify(prefix):
    """用非事务 Pipeline 分批读取并核对全部键值，返回(正确数, 总数)。"""
    correct = 0
    for start in range(1, N + 1, Q):
        end = min(start + Q, N + 1)
        p = r.pipeline(transaction=False)
        for i in range(start, end):
            p.get(prefix + str(i))
        values = p.execute()
        for offset, value in enumerate(values):
            i = start + offset
            if value == "value-%s-%d" % (SID, i):
                correct += 1
    return correct, N


cleanup()

print("本人参数：N = 1000 + 100*C + S = %d，Q = %d" % (N, Q))

# ---------------- 方案甲：逐条写入，收到上一条回复后再发下一条 ----------------
start_a = time.perf_counter()
for i in range(1, N + 1):
    r.set(SEQ_PREFIX + str(i), "value-%s-%d" % (SID, i))
end_a = time.perf_counter()
elapsed_a = (end_a - start_a) * 1000

# ---------------- 方案乙：普通 Pipeline 分批写入，transaction=False ----------------
start_b = time.perf_counter()
batches = 0
last_batch = 0
for start in range(1, N + 1, Q):
    end = min(start + Q, N + 1)
    p = r.pipeline(transaction=False)
    for i in range(start, end):
        p.set(PIPE_PREFIX + str(i), "value-%s-%d" % (SID, i))
    p.execute()          # 取得本批全部结果后，才提交下一批
    batches += 1
    last_batch = end - start
end_b = time.perf_counter()
elapsed_b = (end_b - start_b) * 1000

# ---------------- 核验 ----------------
ok_a, total_a = verify(SEQ_PREFIX)
ok_b, total_b = verify(PIPE_PREFIX)
check_a = (ok_a == total_a)
check_b = (ok_b == total_b)

print("命令总数 = %d" % N)
print("Pipeline批次数 = %d，最后一批数量 = %d" % (batches, last_batch))
print("方案甲（逐条写入）耗时 = %.2f ms" % elapsed_a)
print("方案乙（普通Pipeline）耗时 = %.2f ms" % elapsed_b)
print("核验甲：%d/%d 正确，%s" % (ok_a, total_a, "通过" if check_a else "未通过"))
print("核验乙：%d/%d 正确，%s" % (ok_b, total_b, "通过" if check_b else "未通过"))
if elapsed_b > 0:
    print("方案乙比方案甲快 %.2f 倍" % (elapsed_a / elapsed_b))
print("结论：%s" % ("方案乙（Pipeline）更快" if elapsed_b < elapsed_a else "本次测量中方案甲更快"))

r.close()
