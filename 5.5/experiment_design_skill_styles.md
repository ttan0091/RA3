# Skill 写法对比实验设计

## 0. 研究问题

**RQ: 同一任务的 SKILL.md 以不同写法呈现时，对 Agent 执行效果有怎样的影响？**

我们从三个维度量化"影响"：
1. **任务成功率**（binary：0/1）
2. **Token 消耗**（input + output tokens）
3. **响应时间**（API 首字节到结束的 wall-clock 时间）

核心假设：不同写法在任务成功率上差异不大（LLM 对自然语言的理解能力很强），但在 token 消耗和响应时间上会有显著差异——这意味着"写法"是一个被忽视的效率杠杆。

---

## 1. 自变量：写法类型（Style）

我们从已有的 2000 个 SKILL.md 中归纳出 **6 种写法原型（archetype）**。这些不是数据集自带的标签，而是我们的贡献。

| 编号 | 写法名称 | 英文标签 | 核心特征 | 典型长度 |
|---:|---|---|---|---:|
| S1 | **极简型** | `minimal` | 仅 YAML frontmatter + 1–3 句指令。无标题、无代码、无示例。 | 30–80 词 |
| S2 | **清单型** | `checklist` | 用 Markdown 标题 + 无序/有序列表组织。规则以 MUST/NEVER 短句列出，无长段落。 | 100–200 词 |
| S3 | **叙述型** | `narrative` | 以自然语言段落为主。解释 *为什么* 这样做、背景知识、注意事项，像一篇小教程。 | 200–400 词 |
| S4 | **示例驱动型** | `example-driven` | 极少散文，以多个 input→output 示例为主体。LLM 通过 few-shot 理解任务。 | 150–300 词 |
| S5 | **代码模板型** | `code-template` | 包含可执行的代码/脚本作为主要指令。自然语言只做胶水。 | 150–400 词 |
| S6 | **混合型** | `hybrid` | 标题 + 段落 + 列表 + 示例 + 代码均有。各部分都到位但各不占主导。最接近"理想文档"。 | 300–600 词 |

### 1.1 写法原型的操作性定义

为了保证不同人写出的同一类型的 SKILL.md 具有可比性，给出每种类型的 **模板骨架**：

**S1 minimal:**
```markdown
---
name: <skill-name>
description: <one-line description>
---
<1–3 句话描述功能和用法>
```

**S2 checklist:**
```markdown
---
name: <skill-name>
description: <one-line description>
---
# <Skill Name>
## When to Use
- <trigger condition>
## Rules
- MUST ...
- NEVER ...
## Steps
1. ...
2. ...
3. ...
```

**S3 narrative:**
```markdown
---
name: <skill-name>
description: <one-line description>
---
# <Skill Name>
<2–3 段散文，解释背景、动机、方法论>
<1 段散文，解释边界条件和注意事项>
```

**S4 example-driven:**
```markdown
---
name: <skill-name>
description: <one-line description>
---
# <Skill Name>
<1 句话概述>
## Examples
### Example 1: <scenario>
**Input:** ...
**Output:** ...
### Example 2: <scenario>
**Input:** ...
**Output:** ...
### Example 3 (edge case): <scenario>
**Input:** ...
**Output:** ...
```

**S5 code-template:**
```markdown
---
name: <skill-name>
description: <one-line description>
---
# <Skill Name>
<1 句话概述>
## Implementation
```python
def main(input):
    # ...
    return output
```
## Usage
```bash
python3 skill.py --input <file> --output <file>
```
```

**S6 hybrid:**
```markdown
---
name: <skill-name>
description: <one-line description>
---
# <Skill Name>
<1 段概述>
## When to Use
- ...
## Rules
- MUST ...
## Steps
1. ...
## Example
**Input:** ...
**Output:** ...
## Reference Code
```python
...
```
```

### 1.2 信息守恒原则

**关键约束：六种写法必须传达相同的语义信息量。**

具体来说，对于同一个任务 T：
- 所有写法都覆盖相同的 **功能描述**（做什么）
- 所有写法都覆盖相同的 **约束条件**（不做什么）
- 所有写法都覆盖相同的 **预期输出格式**
- 差异仅在于 **表达方式**（prose vs list vs code vs example）

违反此原则的变体在 QA 审查中应被退回重写。

---

## 2. 任务设计（Experimental Tasks）

### 2.1 任务选取原则

1. **可二元判定**：任务结果只有"对"和"错"，不需要主观评分
2. **确定性答案**：给定输入，正确输出唯一（或属于一个可枚举的等价集）
3. **领域多样性**：覆盖文本处理、数据变换、代码生成、分析推理
4. **复杂度梯度**：简单 / 中等 / 困难各占 1/3
5. **可重复执行**：每次给相同输入，期望相同输出

### 2.2 任务列表（15 个）

#### 类别 A：文本变换（Text Transformation）

| ID | 任务 | 难度 | 输入 | 正确输出判定标准 |
|---|---|---|---|---|
| T01 | Markdown 表格 → JSON 数组 | 简单 | 一个 3×4 的 Markdown 表格 | `json.loads()` 成功 + 字段名/值完全匹配 |
| T02 | 驼峰命名 → 蛇形命名批量转换 | 简单 | 5 个 camelCase 标识符 | 每个转换结果完全匹配 |
| T03 | 自然语言日期 → ISO 8601 | 中等 | 10 句含日期的英文句子 | 提取出的日期字符串完全匹配 |

#### 类别 B：数据处理（Data Processing）

| ID | 任务 | 难度 | 输入 | 正确输出判定标准 |
|---|---|---|---|---|
| T04 | CSV 去重并按某列排序 | 简单 | 20 行 CSV，含 3 个重复行 | 输出行数 = 17，排序正确 |
| T05 | JSON 嵌套结构展平 | 中等 | 3 层嵌套的 JSON 对象 | 展平后 key 格式 `a.b.c`，值不变 |
| T06 | 从非结构化日志中提取错误摘要 | 困难 | 50 行混合日志（INFO/WARN/ERROR） | 正确提取所有 ERROR 行 + 分类汇总 |

#### 类别 C：代码生成（Code Generation）

| ID | 任务 | 难度 | 输入 | 正确输出判定标准 |
|---|---|---|---|---|
| T07 | 写一个 Python 函数：两个有序列表合并 | 简单 | 函数签名 + 3 个 test case | 所有 test case 通过 |
| T08 | 写正则表达式匹配特定模式 | 中等 | 模式描述 + 10 个正/负例 | 所有正例匹配，所有负例不匹配 |
| T09 | 写一个 SQL 查询（3 表 JOIN + 聚合） | 困难 | 表结构 DDL + 预期结果 | 在 SQLite 上执行结果匹配 |

#### 类别 D：分析与推理（Analysis & Reasoning）

| ID | 任务 | 难度 | 输入 | 正确输出判定标准 |
|---|---|---|---|---|
| T10 | 从 requirements.txt 找出不安全的版本 | 中等 | 15 个依赖项（5 个有已知 CVE） | 正确识别 5 个 + 给出 CVE 编号 |
| T11 | 分析 git diff 判断是否为 breaking change | 中等 | 一段 diff（修改了公开 API 签名） | 二元判定 + 理由包含关键字段名 |
| T12 | 从 Dockerfile 中识别安全反模式 | 困难 | 含 4 个反模式的 Dockerfile | 识别出 ≥3 个反模式 |

#### 类别 E：文件操作规划（Operation Planning）

| ID | 任务 | 难度 | 输入 | 正确输出判定标准 |
|---|---|---|---|---|
| T13 | 给出迁移数据库的步骤 | 简单 | 旧/新 schema + 约束条件 | 步骤包含所有必要 DDL + 正确顺序 |
| T14 | 设计一个 CI pipeline 配置 | 困难 | 需求列表（lint/test/build/deploy） | YAML 语法正确 + 覆盖所有阶段 |
| T15 | 排查一个报错的 root cause | 困难 | stack trace + 相关代码片段 | 正确定位到出错行 + 给出修复方案 |

### 2.3 任务输入的固定化

每个任务准备一份 **固定输入文件** `tasks/T{id}/input.txt`，包含：
- 任务指令（一段自然语言，所有 style 共用）
- 输入数据（固定不变）

另有一份 **标准答案文件** `tasks/T{id}/expected.txt` 或 `tasks/T{id}/judge_prompt.txt`（用于 LLM 评判）。

---

## 3. 因变量与测量方法

### 3.1 任务成功率（Task Success）

**判定方式：自动 + LLM judge 双重验证**

- **类型 A/B/C**（有确定性答案的任务）：先用脚本做精确匹配或执行验证（如 `json.loads()`、`pytest`、SQL 执行）；若脚本判 FAIL 但输出看上去合理，再用 LLM judge 做柔性判定。
- **类型 D/E**（开放性更强的任务）：用 LLM judge（DeepSeek v4-flash）做二元判定。

**LLM judge prompt 模板：**
```
你是一个任务评判员。请判断以下 Agent 的输出是否正确完成了任务。

## 任务描述
{task_description}

## 预期输出要点
{expected_key_points}

## Agent 实际输出
{agent_output}

请回答 PASS 或 FAIL，并用一句话说明理由。
输出格式：{"verdict": "PASS" | "FAIL", "reason": "..."}
```

### 3.2 Token 消耗

从 API 返回的 `usage` 字段直接读取：
- `prompt_tokens`（输入 token 数）
- `completion_tokens`（输出 token 数）
- `total_tokens` = prompt + completion

分析时分别报告 prompt/completion，因为：
- prompt_tokens 主要由 SKILL.md 长度决定（与写法直接相关）
- completion_tokens 反映 LLM 的"思考量"和"输出冗余度"（可能受写法间接影响）

### 3.3 响应时间

记录两个时间戳：
- `t_start`：发起 API 请求的时刻
- `t_end`：收到完整响应的时刻
- `latency_ms` = `t_end - t_start`

注意：DeepSeek API 的响应时间受服务器负载影响。为降低噪声：
- 所有实验在 **同一时间窗口**（如连续 3–4 小时内）完成
- 每组实验开始前插入一个 **warm-up 请求**（丢弃结果）
- 如果某次请求 latency 超过 p99 × 3，标记为 outlier 并重跑

---

## 4. 实验流程

### 4.1 总体设计

**被试内设计（within-subjects）**：每个任务都接受全部 6 种写法 + 1 个无 skill baseline。

实验矩阵：

```
15 任务 × (6 写法 + 1 baseline) × 3 重复 = 315 次 API 调用
```

**Baseline（S0）**：不提供 SKILL.md，直接把任务指令作为 user message 发给 LLM。用于衡量 skill 本身带来的增益（或开销）。

### 4.2 SKILL.md 生成流程

#### Step 1：定义功能规格

对每个任务写一份 **功能规格书**（1 页），列出：
- 功能描述
- 输入/输出格式
- 约束条件
- 边界情况

这份规格书是 **内部文档，不给 LLM 看**，仅用于指导写法生成。

#### Step 2：LLM 辅助生成 + 人工审校

用 DeepSeek v4-flash 为每个任务生成 6 种写法的 SKILL.md：

```
请为以下功能写一个 SKILL.md，遵循 {style_name} 风格。

功能规格：
{spec}

风格要求：
{style_template}

请输出完整的 SKILL.md 内容（含 YAML frontmatter）。
```

生成后，**人工审校**确保：
1. 信息守恒：6 种写法传达了相同的功能信息
2. 风格合规：每种写法确实符合其原型定义
3. 无幻觉：不包含规格书中没有的信息

不合格的退回重写，直到通过审校。

#### Step 3：Token 预检

在正式实验前，统计每份 SKILL.md 的 token 数（用 tiktoken cl100k_base），确认：
- 同一任务的 6 种写法之间的 token 数差异在预期范围内
- S1 < S2 ≈ S4 < S3 ≈ S5 < S6（大致趋势）

### 4.3 执行流程

```python
for task in tasks:                    # 15 个任务
    for style in [S0, S1, ..., S6]:   # 7 种条件（含 baseline）
        for rep in range(3):          # 3 次重复
            prompt = build_prompt(task, style)
            t_start = time.time()
            response = deepseek_call(prompt)
            t_end = time.time()
            
            record = {
                "task_id": task.id,
                "style": style,
                "rep": rep,
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "latency_ms": (t_end - t_start) * 1000,
                "raw_output": response.content,
            }
            save(record)
```

#### Prompt 构造规则

- **S0 (baseline)**：`system=""`, `user="{task_instruction}\n\n{task_input}"`
- **S1–S6**：`system="You are an AI agent. You have the following skill loaded:\n\n{skill_md_content}"`, `user="{task_instruction}\n\n{task_input}"`

### 4.4 成功率判定

```python
for record in all_records:
    # Step 1: 精确验证（对有确定性答案的任务）
    if task.has_exact_checker:
        record["success"] = exact_check(record["raw_output"], task.expected)
    
    # Step 2: LLM judge（对开放性任务 或 精确验证 FAIL 的）
    if not task.has_exact_checker or not record["success"]:
        verdict = llm_judge(task, record["raw_output"])
        record["success"] = (verdict == "PASS")
        record["judge_reason"] = verdict.reason
```

---

## 5. 统计分析计划

### 5.1 描述统计

对每个任务 × 写法，报告：
- 成功率（3 次中成功几次）
- Token 消耗：mean ± std（分 prompt / completion / total）
- 响应时间：mean ± std

汇总表示例：

| 任务 | S0 | S1 | S2 | S3 | S4 | S5 | S6 |
|---|---|---|---|---|---|---|---|
| T01 成功率 | 2/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 |
| T01 avg tokens | 324 | 412 | 567 | 823 | 601 | 689 | 945 |
| T01 avg latency (ms) | 1200 | 1450 | 1800 | 2300 | 1900 | 2100 | 2800 |

### 5.2 假设检验

#### (a) 成功率差异

- 由于每个 cell 只有 3 次重复，单个任务的成功率差异统计效力很低。
- 因此我们做 **跨任务汇总**：将所有 15 个任务的成功率汇总（每种写法 45 次试验），用 **Cochran's Q 检验** 判断 7 种条件之间是否有整体差异。
- 如果 Q 检验显著，做 **McNemar 事后配对检验**（Bonferroni 校正）。

#### (b) Token 消耗差异

- **Friedman 检验**（非参数被试内 ANOVA）：以 15 个任务为被试，7 种写法为条件，median total_tokens 为因变量。
- 如果 Friedman 显著，做 **Wilcoxon signed-rank 事后配对检验**（Holm-Bonferroni 校正）。
- 额外分析：prompt_tokens vs completion_tokens 分别检验，观察 token 差异主要来自输入还是输出。

#### (c) 响应时间差异

- 同 Token 消耗，用 Friedman + Wilcoxon。
- 额外分析：latency 与 total_tokens 的 **Spearman 相关**——如果 r > 0.8，说明 latency 差异主要是 token 差异的副产品，不是独立效应。

### 5.3 效率指标

定义 **单位 token 成功率**（Token Efficiency）：

```
TE(style, task) = success_rate / mean_total_tokens × 1000
```

这个指标回答："花 1000 个 token 能买到多少成功概率"。如果所有写法成功率都是 100%，那 TE 越高的写法越有价值。

类似地，定义 **单位时间成功率**（Time Efficiency）：

```
TimeE(style, task) = success_rate / mean_latency_sec
```

### 5.4 写法特征与效果的关联分析

利用已有的 annotation schema 中的 6 个维度（trigger_condition, constraints, stepwise_procedure, error_fallback, io_spec, example_quality），对 90 份 SKILL.md（15 任务 × 6 写法）进行打分，然后做：

- **Spearman 相关矩阵**：6 个结构化维度分别与 success / tokens / latency 的相关性
- **逐步回归**：哪些结构化维度是 token 消耗的显著预测因子

这将回答：**哪些写法特征对效率有贡献，哪些是噪声？**

---

## 6. 控制变量与威胁

### 6.1 需要控制的变量

| 变量 | 控制方法 |
|---|---|
| LLM 版本 | 固定为 DeepSeek v4-flash，记录 model_id |
| Temperature | 固定为 0.0（贪婪解码，最大化可重复性） |
| Max tokens | 固定为 4096（所有任务足够） |
| System prompt | 除 S0 外，system prompt 只有固定前缀 + SKILL.md 内容 |
| 任务指令措辞 | 所有写法共用同一份 task instruction |
| API 服务器负载 | 集中在同一时间窗口执行 + outlier 重跑 |
| 评判一致性 | LLM judge 使用固定 prompt + temperature=0 |

### 6.2 效度威胁

| 威胁 | 缓解措施 |
|---|---|
| **构念效度**：我们定义的 6 种写法是否覆盖了真实世界的变异？ | 从 2000 个真实 SKILL.md 中归纳得出，而非凭空设计。可在论文中报告 2000 个 skill 在 6 类中的分布频率。 |
| **内部效度**：LLM 辅助生成的变体可能引入非写法层面的差异 | 人工审校 + 信息守恒检查。此外，3 次重复帮助稀释单次噪声。 |
| **外部效度**：只在 DeepSeek v4-flash 上做，结论能否推广？ | 论文中明确声明，鼓励后续工作在其他模型上复现。预算允许时加跑 1–2 个模型做 robustness check。 |
| **统计结论效度**：15 任务 × 3 重复 样本量偏小 | 采用非参数检验（对分布假设要求低）+ 效应量报告（不仅看 p 值）。 |

---

## 7. 预算估算

### 7.1 API 调用量

| 用途 | 调用次数 | 预估 tokens/call | 小计 tokens |
|---|---:|---:|---:|
| 主实验（15 × 7 × 3） | 315 | ~2000 | 630,000 |
| SKILL.md 生成（15 × 6） | 90 | ~1500 | 135,000 |
| LLM judge 判定 | ~315 | ~800 | 252,000 |
| 语义保留审校 | ~90 | ~1000 | 90,000 |
| warm-up + 重跑 | ~50 | ~2000 | 100,000 |
| **合计** | **~860** | | **~1,207,000** |

### 7.2 费用

DeepSeek v4-flash 定价（2026-05）：
- Input: ¥1 / 1M tokens
- Output: ¥2 / 1M tokens
- 预估 input:output ≈ 60:40

```
Input cost:  ~720K tokens × ¥1/1M  = ¥0.72
Output cost: ~487K tokens × ¥2/1M  = ¥0.97
Total ≈ ¥1.7
```

加上开发调试、预实验等，**总预算 ≤ ¥10**，基本可忽略。

---

## 8. 时间线

| 阶段 | 时长 | 内容 |
|---|---|---|
| Week 1 | 3 天 | 定义 15 个任务的功能规格 + 准备固定输入/预期输出 |
| Week 1–2 | 4 天 | 用 LLM 生成 90 份 SKILL.md + 人工审校 |
| Week 2 | 2 天 | 搭建实验脚本（prompt 构造、API 调用、结果记录） |
| Week 2–3 | 1 天 | 跑预实验（2 个任务 × 全部写法），验证流程 |
| Week 3 | 1 天 | 正式实验（315 次 API 调用） |
| Week 3 | 1 天 | LLM judge 判定 + 精确验证 |
| Week 3–4 | 3 天 | 数据分析 + 可视化 + 写结果章节 |
| **合计** | **~15 天** | |

---

## 9. 预期产出

### 9.1 图表

1. **热力图**（15 × 7）：每个 cell 是成功率，颜色深浅
2. **分组柱状图**：7 种写法的 mean total tokens，error bar 表示跨任务标准差
3. **散点图**：prompt tokens vs completion tokens，按写法着色
4. **雷达图**：6 种写法在 annotation schema 6 个维度上的打分对比
5. **Spearman 相关矩阵热力图**：结构化维度 × 效果指标
6. **Token Efficiency 排名图**：在所有写法成功率≈100% 的任务子集上，TE 从高到低排列

### 9.2 核心发现（预期方向）

- **成功率差异不大**：6 种写法在大多数任务上都能成功（LLM 理解力强），baseline（无 skill）可能在少数复杂任务上失败。
- **Token 消耗差异显著**：S1 最省，S6 最费，差距可能 2–5 倍。
- **边际收益递减**：从 S1 到 S2 的信息增量对成功率的提升最大；从 S3/S4 到 S6 的增量对成功率几乎无贡献，但 token 代价持续上升。
- **示例 > 散文**：S4（example-driven）可能在 token 效率和成功率的综合指标上表现最好。
- **代码模板有双重效应**：S5 在代码生成任务上成功率高，但在非代码任务上可能引入无效 token。

### 9.3 论文贡献声明

> 我们对 2000 个真实 Agent Skill 的写法进行了系统归纳，提出了 6 种写法原型（archetype），并通过 315 次受控实验量化了不同写法在成功率、token 消耗和响应时间上的差异。结果表明......（由实验结果填充）。这是首个针对 Agent Skill 写法效率的实证研究，为 skill 作者提供了可操作的写作指南。

---

## 10. 目录结构

```
5.2/
├── experiment_design_skill_styles.md    # 本文档
├── tasks/
│   ├── T01/
│   │   ├── spec.md                      # 功能规格（内部）
│   │   ├── input.txt                    # 固定输入
│   │   ├── expected.txt                 # 预期输出 / judge prompt
│   │   ├── S1.md                        # 极简型 SKILL.md
│   │   ├── S2.md                        # 清单型
│   │   ├── S3.md                        # 叙述型
│   │   ├── S4.md                        # 示例驱动型
│   │   ├── S5.md                        # 代码模板型
│   │   └── S6.md                        # 混合型
│   ├── T02/
│   │   └── ...
│   └── ...
├── scripts/
│   ├── gen_skill_variants.py            # LLM 辅助生成 SKILL.md 变体
│   ├── run_experiment.py                # 主实验执行脚本
│   ├── judge_results.py                 # LLM judge + 精确验证
│   └── analyze_styles.py               # 统计分析 + 可视化
├── results/
│   ├── raw/                             # 每次 API 调用的原始记录
│   ├── judged/                          # 判定后的结果
│   └── figures/                         # 图表
└── reports/
    └── style_experiment_report.md       # 最终报告
```

---

## 11. 与 RQ2（攻击实验）的协同

本实验（RQ1）产出的 90 份 SKILL.md 可直接复用于 RQ2 的攻击实验：
- 不同写法的 skill 是否对攻击的脆弱性不同？（如叙述型是否更容易被 adversarial paraphrasing 绕过？）
- 这将为两个 RQ 创造自然的关联，避免论文"两块皮"。

但这是延伸分析，不在本实验设计的必需范围内。
