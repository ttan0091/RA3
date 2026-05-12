---
name: student-grader
description: 根据学校规则评定学生成绩等级。
---

# 学生成绩评定

加权分 weighted = homework×0.20 + midterm×0.25 + final×0.35 + project×0.20。出勤<60%→自动F；出勤<80%→weighted×0.9；>=80%无惩罚。等级：>=90→A, >=80→B, >=70→C, >=60→D, <60→F。荣誉：A且四项均>=85。预警：D/F且任一<50。

## 示例 1：优等生获荣誉
输入：homework=92, midterm=88, final=95, project=90, attendance=95
计算：weighted = 92×0.2+88×0.25+95×0.35+90×0.2 = 18.4+22+33.25+18 = 91.65
出勤>=80%，无惩罚。等级 A。四项均>=85 → honor=true
**输出：grade=A, honor=true, warning=false**

## 示例 2：出勤不足导致降级
输入：homework=88, midterm=92, final=86, project=90, attendance=75
计算：weighted = 88×0.2+92×0.25+86×0.35+90×0.2 = 17.6+23+30.1+18 = 88.7
出勤 75%<80%→adjusted = 88.7×0.9 = 79.83。等级 C（不是 B）
**输出：grade=C, honor=false, warning=false**

## 示例 3：出勤极低自动 F 但无预警
输入：homework=70, midterm=65, final=60, project=72, attendance=55
出勤 55%<60%→自动 F，不计算加权分等级
四项成绩(70,65,60,72)均 >= 50 → 不满足预警条件
**输出：grade=F, honor=false, warning=false**

## 示例 4：学业预警
输入：homework=45, midterm=52, final=48, project=55, attendance=85
计算：weighted = 45×0.2+52×0.25+48×0.35+55×0.2 = 9+13+16.8+11 = 49.8
出勤>=80%，无惩罚。等级 F（<60）。homework=45<50 → warning=true
**输出：grade=F, honor=false, warning=true**

## 示例 5：F 但无预警（分数恰好 50）
输入：homework=60, midterm=55, final=50, project=65, attendance=70
计算：weighted = 60×0.2+55×0.25+50×0.35+65×0.2 = 12+13.75+17.5+13 = 56.25
出勤 70%<80%→adjusted = 56.25×0.9 = 50.625。等级 F。
最低分=50，不<50 → warning=false
**输出：grade=F, honor=false, warning=false**