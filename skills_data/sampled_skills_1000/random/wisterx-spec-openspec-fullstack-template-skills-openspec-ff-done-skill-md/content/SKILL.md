---
name: openspec-ff-done
description: 完成 Frontend-First 集成与归档。在 Step 7 使用——检查契约测试是否通过，生成前端切换指南，创建归档文档。标志着一个功能从 Mock 驱动到真实 API 的完整过渡。
license: MIT
compatibility: Works with any frontend project using the Frontend-First workflow.
metadata:
  author: openspec
  version: "1.0"
---

完成 Frontend-First 集成与归档：检查契约测试 → 验证前端切换 → 生成归档文档。

**前提条件：** Step 6（Backend Implementation）已完成，后端 API 已实现且契约测试已编写。

**Input**: 功能名称（feature name）。如果未提供，尝试从 `openspec/specs/` 目录中找到有 `ui-freeze.md` 和 `spec.md` 的功能；如果有多个，使用 AskUserQuestion 让用户选择。

**Steps**

1. **检查前置条件**

   验证以下文件/产出物存在：
   - `openspec/specs/<feature>/proposal.md` — 需求文档
   - `openspec/specs/<feature>/ui-freeze.md` — UI 冻结确认
   - `openspec/specs/<feature>/spec.md` — API 契约
   - `devtools/mocks/data/<feature>/` — Mock 数据（有冻结标记）

   如果缺少任何文件，报告缺失项并建议用户先完成前置步骤。

2. **检查契约测试状态**

   **方式 A：如果项目有测试命令**
   - 搜索 `package.json` 中的 test 脚本（`test:contract`、`test`）
   - 搜索 `tests/contract/` 目录下与功能相关的测试文件
   - 如果找到，提示用户运行测试并确认结果

   **方式 B：如果没有自动化测试**
   - 使用 AskUserQuestion 询问：
     ```
     契约测试状态：
     1. 已运行并全部通过
     2. 已运行但有失败
     3. 未编写契约测试
     ```
   - 如果选择 2（有失败），提示先修复再继续
   - 如果选择 3（未编写），警告但允许继续（记录到归档中）

3. **生成前端切换指南**

   分析前端代码中的 Mock 使用方式，生成切换步骤：

   ```markdown
   ## 前端切换指南

   ### 切换步骤

   1. 确认后端 API 地址配置正确
      - 检查 `.env.development` 中的 `VITE_API_BASE_URL`

   2. 移除/禁用 <feature> 的 Mock Handler
      - 文件：devtools/mocks/data/<feature>/handlers.ts
      - 从 devtools/mocks/handlers.ts 的汇总中移除 import

   3. 功能测试
      - [ ] 列表展示正常
      - [ ] 筛选功能正常
      - [ ] 搜索功能正常
      - [ ] 排序功能正常
      - [ ] 分页功能正常
      - [ ] 空数据展示正常
      - [ ] 错误情况有提示
      - [ ] 无 console 报错

   4. 如果测试通过
      - 可以删除 Mock Handler 文件
      - Mock 数据文件保留（作为归档参考）
   ```

4. **使用 AskUserQuestion 确认集成状态**

   ```
   集成验收：
   1. 前端已切换到真实 API 并测试通过
   2. 还在测试中（稍后再归档）
   3. 使用 Mock 作为最终数据源（frontend-only 模式）
   ```

   如果选择 2，提示用户完成测试后重新运行此 Skill。
   如果选择 3，跳过切换步骤，直接归档。

5. **生成归档文档**

   在 `openspec/specs/<feature>/` 目录下创建 `archive.md`：

   ```markdown
   # Archive: <功能名称>

   ## 完成时间
   <当前日期 YYYY-MM-DD>

   ## 工作流记录
   | 步骤 | 完成日期 | 说明 |
   |------|---------|------|
   | Step 1: Proposal | <从 proposal.md 提取> | 需求定义 |
   | Step 2: Frontend + Mock | <从 Mock 文件时间推断> | 前端设计 |
   | Step 3: UI Freeze | <从 ui-freeze.md 提取> | UI 冻结 |
   | Step 4: API Spec | <从 spec.md 提取> | 契约生成 |
   | Step 5: Spec Review | <从 spec.md 确认记录提取> | 契约确认 |
   | Step 6: Backend | <当前日期或用户提供> | 后端实现 |
   | Step 7: Integration | <当前日期> | 集成完成 |

   ## 功能总结
   <从 proposal.md 提取目标和用例>

   ## 技术实现

   ### 前端
   - 主要组件：<从 src/components/<Feature>/ 扫描>
   - Mock 数据：devtools/mocks/data/<feature>/

   ### 后端
   - API 列表：<从 spec.md 提取 endpoint 列表>
   - Spec 文件：openspec/specs/<feature>/spec.md

   ### 数据库
   - <从后端代码或 migration 文件推断，如果找不到写"见后端代码">

   ## 测试情况
   - 契约测试：<通过/未编写/部分通过>
   - 功能测试：<通过/手动通过>

   ## 一致性状态
   | 维度 | 状态 |
   |------|------|
   | Mock ↔ Spec | <一致/有偏差> |
   | Spec ↔ Backend | <一致/未验证> |
   | Mock ↔ Backend | <一致/未验证> |

   ## 遗留事项
   - <如果有未完成的测试、已知问题等>

   ## 相关文件
   - 需求：openspec/specs/<feature>/proposal.md
   - UI 冻结：openspec/specs/<feature>/ui-freeze.md
   - API 契约：openspec/specs/<feature>/spec.md
   - Mock 数据：devtools/mocks/data/<feature>/
   - 前端组件：src/components/<Feature>/
   ```

6. **清理和提示**

   ```
   ✅ 功能「<feature>」已完成归档

   归档文件：openspec/specs/<feature>/archive.md

   完成的文档链：
   proposal.md → ui-freeze.md → spec.md → archive.md

   建议：
   - 如果 Mock Handler 已不需要，可以删除 devtools/mocks/data/<feature>/handlers.ts
   - Mock 数据文件建议保留，作为归档参考
   - 考虑将归档内容也复制到 docs/archives/<feature>/（如果使用该目录结构）
   ```

**Output**

- 前端切换指南（内嵌在归档中或独立文件）
- `archive.md`（归档文档，包含完整工作流记录）
- 集成验收确认

**Guardrails**

- **不跳过检查**：即使用户急于归档，也要检查前置条件和契约测试状态
- **如实记录**：如果契约测试未编写或有失败，在归档中如实记录，不要隐瞒
- **自动提取信息**：尽可能从已有文件中自动提取信息（日期、字段、endpoint），减少用户手动输入
- **保留 Mock 数据**：归档不删除 Mock 数据文件，只移除 Handler（停止拦截请求）
