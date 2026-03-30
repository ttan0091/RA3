---
name: wt-merge
description: 合并当前分支到目标分支（默认 main/master）。自动检测合并冲突，推送合并结果。触发条件：用户输入 "/wt-merge" 或请求合并分支/完成工作流。
---

# wt-merge

将当前分支合并到目标分支（默认 main/master），自动处理冲突检测和推送。

## 工作流程

1. **确认目标分支**
2. **检查分支状态**
3. **切换到目标分支并拉取最新代码**
4. **执行合并**
5. **推送合并结果**
6. **清理（可选）**

## 执行步骤

### 1. 确认目标分支

```bash
# 检查仓库的主分支名称
git remote show origin | grep "HEAD branch" | awk '{print $3}'
# 或使用默认值
```

默认目标分支优先级：`main` > `master`

### 2. 检查分支状态

```bash
# 获取当前分支
git branch --show-current

# 检查未提交更改
git status --porcelain

# 检查远程同步状态
git status -sb
```

### 3. 切换到目标分支

```bash
# 保存当前工作（如有未提交更改）
git stash push -m "wt-merge stash"

# 切换到目标分支
git checkout main

# 拉取最新代码
git pull origin main
```

### 4. 执行合并

```bash
# 合并当前分支
git merge --no-ff <source-branch> --no-edit

# 如果失败，尝试解决冲突（参考 wt-resolve 逻辑）
# 或中止合并
git merge --abort
```

### 5. 推送合并结果

```bash
# 推送到远程
git push origin main

# 输出成功信息
```

### 6. 可选清理

```bash
# 询问是否删除已合并的源分支
git branch -d <source-branch>      # 本地删除
git push origin --delete <source-branch>  # 远程删除
```

## 合并策略

| 场景 | 处理方式 |
|------|----------|
| 无冲突 | 直接合并并推送 |
| 有冲突 | 提示用户，尝试自动解决或中止 |
| 分支已过期 | 先同步目标分支最新代码 |
| 未提交更改 | 询问是否提交或暂存 |

## 安全提示

合并前会检查：
- ✅ 是否有未提交的更改
- ✅ 当前分支是否已推送到远程
- ✅ 目标分支是否有新的提交
- ✅ 用户确认（重要操作）

## 示例流程

```
当前分支：feat/login-page
目标分支：main

1. 检查完成，准备合并
2. 切换到 main 并拉取最新代码
3. 合并 feat/login-page 到 main
4. 推送 main 到远程
5. 删除 feat/login-page 分支？ [y/N]
✅ 合并完成
```

## 注意事项

- 合并前会要求用户确认（重要操作）
- 如果合并失败，提供中止选项
- 支持 `--squash` 选项（如果用户要求）
- 合并后询问是否清理源分支
- 保留源分支直到用户确认删除
