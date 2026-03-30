---
name: workflow
description: 工作流执行器 - 执行预定义的工作流，自动化复杂任务序列
metadata:
  {
    "openclaw":
      {
        "emoji": "🔄",
        "requires": {
          "bins": ["bash", "python3"]
        }
      }
  }
---

# Workflow 🔄

工作流执行器，执行预定义的工作流，自动化复杂任务序列。

## 概述

`workflow` 让你可以：
- 定义多步骤工作流
- 执行复杂任务序列
- 支持条件分支
- 记录工作流执行日志

## 设置

### 前置要求
- Bash + Python 3

### 安装
```bash
cd ~/clawd
mkdir -p scripts
cp [path/to]/workflow.sh scripts/
chmod +x scripts/workflow.sh
mkdir -p memory/workflows
```

## 使用方法

### 执行工作流
```bash
./scripts/workflow.sh run "工作流名称"
```

### 列出所有工作流
```bash
./scripts/workflow.sh list
```

### 创建新工作流
编辑 `memory/workflows/工作流名称.json`：
```json
{
  "name": "每日检查",
  "steps": [
    {"cmd": "./scripts/evolution-report.sh"},
    {"cmd": "./scripts/quick-skill-check.sh"},
    {"cmd": "./scripts/project-check.sh list"}
  ]
}
```

## 工作流示例

### 每日检查
```json
{
  "name": "daily-check",
  "steps": [
    {"name": "进化报告", "cmd": "./scripts/evolution-report.sh"},
    {"name": "技能检查", "cmd": "./scripts/quick-skill-check.sh"},
    {"name": "项目检查", "cmd": "./scripts/project-check.sh list"}
  ]
}
```

### 社区互动
```json
{
  "name": "community-engagement",
  "steps": [
    {"name": "检查Moltbook", "cmd": "./check-moltbook.sh"},
    {"name": "分析兴趣", "cmd": "python3 tools/interest-analyzer.py"},
    {"name": "更新记录", "cmd": "echo '完成社区互动' >> memory/daily-log.md"}
  ]
}
```

## 使用场景

### 场景 1: 每日例行
```bash
./scripts/workflow.sh run "daily-check"
```

### 场景 2: 项目启动
```bash
./scripts/workflow.sh run "project-startup"
```

### 场景 3: 周期性维护
```bash
openclaw cron add \
  --name "weekly-workflow" \
  --schedule "0 9 * * 1" \
  --command "./scripts/workflow.sh run 'weekly-maintenance'"
```

## 仓库

https://github.com/90le/openclaw-skills-hub

---

**自动化复杂任务！** 🔄
