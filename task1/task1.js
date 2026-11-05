// task1/task1.js —— 第一题业务操作脚本（可重复执行，不需要重新初始化）
// 运行：mongosh "mongodb://127.0.0.1:27017/?replicaSet=rs0" --quiet --file task1.js
const SID = "12303030103";
const S = 3;   // 学号最后两位 03 -> 3
const A = 0;   // S mod 3 = 0

const examDB = db.getSiblingDB("exam_" + SID);
const courses = examDB.courses;
const courseId = "COURSE-" + SID + "-01";

print("=== 1. 查询张老师讲授且状态为 OPEN 的课程 ===");
const result = courses.aggregate([
  { $match: { teacher: "张老师", status: "OPEN" } },
  { $project: { _id: 0, courseId: "$_id", title: 1, chapterCount: { $size: "$chapters" } } },
  { $sort: { courseId: 1 } }
]).toArray();
result.forEach(c => print("课程编号=" + c.courseId + " | 课程名称=" + c.title + " | 章节数量=" + c.chapterCount));

print("=== 2. 将 01 号课程 CH02 章节标题改为 Redis基础与应用-" + S + " ===");
const upd2 = courses.updateOne(
  { _id: courseId, "chapters.chapterId": "CH02" },
  { $set: { "chapters.$[ch].title": "Redis基础与应用-" + S } },
  { arrayFilters: [{ "ch.chapterId": "CH02" }] }
);
print("更新结果：matchedCount=" + upd2.matchedCount + ", modifiedCount=" + upd2.modifiedCount);
const docAfter = courses.findOne({ _id: courseId });
print("更新后的课程文档：");
print("  _id=" + docAfter._id + " | title=" + docAfter.title + " | teacher=" + docAfter.teacher + " | status=" + docAfter.status);
docAfter.chapters.forEach(c => print("  " + c.chapterId + " | " + c.title + " | hours=" + c.hours));

print("=== 3. 连续两次新增 CH03 章节（防止重复）===");
const newChapter = { chapterId: "CH03", title: "Redis高级操作", hours: 2 + A };
function addCh03Once() {
  return courses.updateOne(
    { _id: courseId, chapters: { $not: { $elemMatch: { chapterId: "CH03" } } } },
    { $push: { chapters: newChapter } }
  );
}
const add1 = addCh03Once();
print("第1次新增：matchedCount=" + add1.matchedCount + ", modifiedCount=" + add1.modifiedCount);
const add2 = addCh03Once();
print("第2次新增：matchedCount=" + add2.matchedCount + ", modifiedCount=" + add2.modifiedCount);

print("=== 4. 验证与解释 ===");
const doc = courses.findOne({ _id: courseId });
const ch02 = doc.chapters.find(c => c.chapterId === "CH02");
const ch03Count = doc.chapters.filter(c => c.chapterId === "CH03").length;
print("(1) 修改后 CH02 的标题：" + ch02.title);
print("(2) 两次新增后 CH03 的数量：" + ch03Count);
print("(3) 最终章节总数：" + doc.chapters.length);
print("(4) teacher=" + doc.teacher + "，status=" + doc.status);

const pass = ch02.title === "Redis基础与应用-" + S
  && ch03Count === 1
  && doc.chapters.length === 3
  && doc.teacher === "张老师"
  && doc.status === "OPEN";
print("核验结果：" + (pass ? "PASS" : "FAIL"));
