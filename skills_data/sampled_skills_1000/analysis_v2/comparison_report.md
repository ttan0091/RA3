# Popular vs Random Skills （n=1000 × 2）

#### 一、独立作者数：Popular 高度集中，Random 高度分散

Popular 的 1000 个 skills 只来自 73 个作者, Random 有 788 个独立作者

Popular 列表反映的是谁的仓库 stars 最多——一个 24 万 stars 的 React 仓库里塞进去的任何 skill 都会排在 Popular 前列，而这跟 skill 自身的设计质量或使用频率没有必然关联。

#### 二、内容字符数

| | Popular | Random |
|:--|:--------|:-------|
| 中位字符数 | 7,416 | 4,484 |
| 平均字符数 | 9,123 | 6,818 |

#### 三、有约束/禁止 与 有触发条件

##### 有约束/禁止（Popular 68.1% vs Random 56.7%，+11.4pp）

"有约束/禁止"指的是 SKILL.md 中出现了 "never"、"must not"、"do not"、"don't"、"important"、"warning"、"caution"、"critical" 这类词。这个 skill 明确告诉了 Agent 什么不能做。

Popular ——PyTorch 的 pr-review skill：

```markdown
2. Focus on what CI cannot check - Don't comment on formatting, linting, or type errors
6. Assume competence - The author knows PyTorch; explain only non-obvious context
```

Popular ——openclaw 的 coding-agent skill：

```markdown
8. NEVER start Codex in ~/.openclaw/ - it'll read your soul docs and get weird ideas
9. NEVER checkout branches in ~/Projects/openclaw/ - that's the LIVE OpenClaw instance!
```

这些约束精确地告诉 Agent 不要碰特定目录、不要重复 CI 已检查的内容。这是一种用"负向经验"约束 Agent 行为的工程实践。

##### 有触发条件（Popular 79.3% vs Random 66.9%，+12.4pp）

有触发条件指的是 SKILL.md 中出现了 "trigger"、"use when"、"invoke"、"activate"、"use this skill" 这类词，明确定义了什么时候应该激活。

Popular ——React 的 fix skill YAML：

```yaml
description: Use when you have lint errors, formatting issues, or before committing code to ensure it passes CI.
```

Popular ——VS Code 的 accessibility skill：

```markdown
Applies to both new interactive UI surfaces and updates to existing features.
Use when creating new UI or updating existing UI features.
```

这些触发条件的作用是让 Agent可以在面对特定场景时自动选中正确的 skill，而不需要用户手动指定。如果一个 skill 没有明确的触发条件，Agent 就不知道在什么场景下加载它，它要么永远不被使用，要么被错误地使用。

#### 四、功能类型分布

通过对 SKILL.md 内容的关键词/语义分析，将每个 skill 归入一个功能类型：

| 类型 | Popular | Random | 差异 |
|:-----|--------:|-------:|:-----|
| testing | 636（63.6%） | 572（57.2%） | Popular +6.4pp |
| security | 257（25.7%） | 236（23.6%） | 基本持平 |
| code-quality | 30（3.0%） | 67（6.7%） | Random 是 Popular 的 2.2 倍 |
| documentation | 20（2.0%） | 23（2.3%） | 基本持平 |
| code-review | 16（1.6%） | 21（2.1%） | 基本持平 |
| frontend | 6（0.6%） | 23（2.3%） | Random 明显更多 |
| devops | 11（1.1%） | 13（1.3%） | 基本持平 |
| git-workflow | 8（0.8%） | 13（1.3%） | 基本持平 |
| api-development | 9（0.9%） | 11（1.1%） | 基本持平 |
| ai-ml | 1（0.1%） | 6（0.6%） | Random 更多 |
| refactoring | 1（0.1%） | 4（0.4%） | — |
| other | 3（0.3%） | 10（1.0%） | — |

#### 五、结构特征

| 结构特征 | Popular | Random | 差异 |
|:---------|--------:|-------:|:-----|
| 有 YAML frontmatter | 100.0% | 99.2% | 几乎全覆盖 |
| 有表格 | 50.5% | 46.2% | +4.3pp |
| 有 checkbox（清单） | 18.6% | 19.6% | 基本持平 |
| 有脚本 | 13.9% | 16.1% | 基本持平 |
| 有错误处理指导 | 64.7% | 59.2% | +5.5pp |
| 有示例 | 70.2% | 66.1% | +4.1pp |
| **有约束/禁止** | 68.1% | 56.7% | +11.4pp |
| **有触发条件** | 79.3% | 66.9% | +12.4pp |

#### 六、总文件数与脚本文件数

| | Popular 中位 | Popular 均值 | Random 中位 | Random 均值 |
|:--|:------------|:------------|:------------|:------------|
| 总文件数 | 1 | 5.3 | 1 | 9.9 |
| 脚本文件数 | 0 | 0.73 | 0 | 4.03 |

两组的中位数都是 1 个文件（只有一个 SKILL.md 文件）。但 Random 的均值显著更高。

两种不同的 skill 设计：

大多数 skills（两组都是）采用纯指令型设计——只有一个 SKILL.md，依靠文字描述引导 Agent 行为

少量 Random skills 将 SKILL.md 与可执行脚本捆绑在一起，Agent 可以直接运行这些脚本。可能带来更多安全风险（可执行代码的注入面





## Anthropic 官方 Skills （n=16）

Anthropic 公开发布在 `anthropics/skills` GitHub 仓库中的 16 个官方 skills 进行同维度分析，其中 `docx`、`pdf`、`pptx`、`xlsx` 是 Claude.ai 文档创建功能的底层 skill（source-available）。

| Skill 名称 | 字符数 | 总文件数 | 脚本数 | 有约束 | 有触发 |
|:-----------|-------:|-------:|------:|:-----:|:-----:|
| algorithmic-art | 19,735 | 4 | 1 | yes | no |
| brand-guidelines | 2,235 | 2 | 0 | no | yes |
| canvas-design | 11,937 | 83 | 0 | yes | yes |
| doc-coauthoring | 15,815 | 1 | 0 | yes | yes |
| docx | 20,056 | 61 | 15 | yes | yes |
| frontend-design | 4,440 | 2 | 0 | yes | yes |
| internal-comms | 1,511 | 6 | 0 | yes | yes |
| mcp-builder | 9,059 | 10 | 2 | no | yes |
| pdf | 8,035 | 12 | 8 | yes | yes |
| pptx | 9,128 | 59 | 16 | yes | yes |
| skill-creator | 32,189 | 18 | 10 | yes | yes |
| slack-gif-creator | 7,841 | 7 | 4 | yes | yes |
| theme-factory | 3,124 | 13 | 0 | yes | yes |
| web-artifacts-builder | 3,073 | 5 | 2 | yes | no |
| webapp-testing | 3,861 | 6 | 4 | yes | yes |
| xlsx | 11,455 | 54 | 13 | yes | yes |

##### 横向对比

| 指标 | Popular (n=1000) | Random (n=1000) | **Official (n=16)** |
|:-----|:-----------------|:----------------|:--------------------|
| **中位字符数** | 7,416 | 4,484 | **9,059** |
| **平均字符数** | 9,123 | 6,818 | **10,218** |
| **有约束/禁止** | 68.1% | 56.7% | **87.5%** |
| **有触发条件** | 79.3% | 66.9% | **87.5%** |
| **总文件数（中位）** | 1 | 1 | **10** |
| **总文件数（均值）** | 5.3 | 9.9 | **21.4** |
| **脚本文件数（中位）** | 0 | 0 | **2** |
| **脚本文件数（均值）** | 0.73 | 4.03 | **4.7** |

##### 高频标题类型

| 标题类型                    |      出现率 | 典型标题                                                     |
| :-------------------------- | ----------: | :----------------------------------------------------------- |
| **Process/Workflow/Steps**  | 56%（9/16） | `Core Workflow`、`Stage 1: Context Gathering`、`Phase 1: Deep Research` |
| **Quick Start/Reference**   | 56%（9/16） | `Quick Reference`、`Quick Start`、`Reference Files`          |
| **Overview/Introduction**   | 44%（7/16） | `Overview`、`How to use this skill`                          |
| **Philosophy/Vision**       | 31%（5/16） | `DESIGN PHILOSOPHY CREATION`、`Philosophy`、`Design Thinking` |
| **Rules/Guidelines**        | 31%（5/16） | `Critical Rules for docx-js`、`Frontend Aesthetics Guidelines` |
| **Dependencies/Setup**      | 25%（4/16） | `Dependencies`                                               |
| **Best Practices/Pitfalls** | 19%（3/16） | `Best Practices`、`Common Pitfall`                           |
| **Output/Format**           | 19%（3/16） | `OUTPUT FORMAT`、`Requirements for Outputs`                  |

