// task1/init.js —— 第一题初始化脚本（仅用于准备数据，与业务操作脚本分开）
// 运行：mongosh "mongodb://127.0.0.1:27017/?replicaSet=rs0" --quiet --file init.js
const SID = "12303030103";
const examDB = db.getSiblingDB("exam_" + SID);

examDB.courses.deleteMany({});
examDB.courses.insertMany([
  {
    _id: "COURSE-" + SID + "-01",
    title: "NoSQL数据库",
    teacher: "张老师",
    status: "OPEN",
    chapters: [
      { chapterId: "CH01", title: "MongoDB基础", hours: 2 },
      { chapterId: "CH02", title: "Redis基础", hours: 2 }
    ]
  },
  {
    _id: "COURSE-" + SID + "-02",
    title: "数据库原理",
    teacher: "张老师",
    status: "CLOSED",
    chapters: [
      { chapterId: "CH01", title: "关系模型", hours: 2 }
    ]
  },
  {
    _id: "COURSE-" + SID + "-03",
    title: "机器学习",
    teacher: "李老师",
    status: "OPEN",
    chapters: [
      { chapterId: "CH01", title: "分类", hours: 2 },
      { chapterId: "CH02", title: "聚类", hours: 2 }
    ]
  }
]);

print("初始化完成：exam_" + SID + ".courses 共 " + examDB.courses.countDocuments({}) + " 条课程");
