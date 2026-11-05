《NoSQL数据库》上机测验

姓名：丁尚武
班级：123030301
学号：12303030103

一、个人参数
SID = 12303030103
S = 学号最后两位 03 -> 3
A = S mod 3 = 0
B = S mod 4 = 3
C = S mod 5 = 3
Stock = 5 + C = 8
Buy = 1 + A = 1
N = 1000 + 100*C + S = 1303
Q = 100

二、运行环境
- Windows 11
- MongoDB Community Server 8.0.32，单节点副本集 rs0，127.0.0.1:27017
- mongosh 2.12.0
- Redis 8.10.2（Windows 便携版，实验五搭建的三主三从集群，端口 30103-30108）
- Python 3.14.0
- pymongo 4.19.0
- redis-py 8.1.0

依赖安装：
    pip install pymongo redis

三、目录说明
task1/  MongoDB 课程信息查询与维护
        init.js       初始化脚本（仅准备数据）
        task1.js      业务操作脚本（可重复执行，不重新初始化）
        result_init.txt / result.txt  实际运行结果
        说明.txt      实现说明与结果解释
task2/  MongoDB 原子扣减与事务验证
        init.py       初始化脚本（重置 inventory、orders）
        task2.py      原子扣减、事务函数与 T1-T4 测试
        result_init.txt / result.txt  实际运行结果
        说明.txt      实现说明与结果解释
task3/  Redis 学习信息与排行榜
        task3.py      Hash、Set、Sorted Set、会话过期与类型核验
        result.txt    实际运行结果
        说明.txt      数据类型说明与结果解释
task4/  Redis Pipeline 与性能比较（选做）
        task4.py      逐条写入、普通 Pipeline 分批写入、计时与完整性核验
        result.txt    实际运行结果
        说明.txt      实现说明与结果解释

四、执行方法
task1：
    cd task1
    mongosh "mongodb://127.0.0.1:27017/?replicaSet=rs0" --quiet --file init.js
    mongosh "mongodb://127.0.0.1:27017/?replicaSet=rs0" --quiet --file task1.js

task2：
    cd task2
    python init.py
    python task2.py
    说明：task2.py 的每个测试场景开始前会单独重置 inventory 和 orders，
          init.py 用于独立准备初始数据。

task3：
    cd task3
    python task3.py
    说明：运行前需先启动实验五的三主三从 Redis 集群（30103-30108）。

task4：
    cd task4
    python task4.py
    说明：运行前需先启动 Redis 集群；程序会自动清理本人前缀下的旧键。

五、其他说明
1. 全部代码使用个人数据库 exam_12303030103 与 Redis 键前缀 exam:12303030103:。
2. 初始化代码与业务操作代码分开存放。
3. result*.txt 均为实际运行输出，不是预期值。
4. 源代码中未包含数据库账号、密码等连接凭据。
