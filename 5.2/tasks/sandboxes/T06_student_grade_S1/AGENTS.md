---
name: student-grader
description: 根据学校规则评定学生成绩等级。
---

加权分 weighted = homework×0.20 + midterm×0.25 + final×0.35 + project×0.20。出勤<60%→自动 F（覆盖一切）；出勤<80%→weighted×0.9；>=80%无惩罚。等级：>=90→A, >=80→B, >=70→C, >=60→D, <60→F（按调整后分数判定）。荣誉：grade=A 且四项单科均>=85。学业预警：grade 为 D 或 F 且任一单科<50。输出 grade(A-F)、honor(bool)、warning(bool)。