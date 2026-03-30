# Agent Skills Empirical Study：可行研究方向深度分析

> 基于团队已有的文献综述、数据基础设施（skillsmp.com 27万+ skills 元数据、GitHub 采样数据），以及最新学术进展（SkillsBench arXiv:2602.12670、安全漏洞研究等），提出以下可行的 empirical study 方向。

---

## 一、研究方向总览

| # | 方向 | 核心 RQ | 数据需求 | 新颖度 | 可行性 | 推荐度 |
|:--|:-----|:--------|:---------|:-------|:-------|:-------|
| 1 | Skills 生态大规模特征分析 | 社区创建的 Skills 长什么样？ | ★★☆ 已有 | ★★★★ | ★★★★★ | ⭐⭐⭐⭐⭐ |
| 2 | Skills 质量与有效性实证评估 | 什么样的 Skill 能真正提升 Agent 表现？ | ★★★ 需构建 | ★★★★★ | ★★★☆ | ⭐⭐⭐⭐ |
| 3 | Skills 安全漏洞大规模分析 | 社区 Skills 有多"危险"？ | ★★☆ 已有 | ★★★★ | ★★★★ | ⭐⭐⭐⭐⭐ |
| 4 | Skills 演化与社区动态研究 | Skills 生态如何发展变化？ | ★★★ 需 Git 历史 | ★★★★ | ★★★☆ | ⭐⭐⭐ |
| 5 | Skills vs. 其他 Prompt 技术对比 | Skills 比 system prompt / few-shot 有本质优势吗？ | ★★★★ 需实验 | ★★★★★ | ★★☆ | ⭐⭐⭐ |
| 6 | 跨平台互操作性实证研究 | Skills 真的"一次编写，随处运行"吗？ | ★★★ 需多平台 | ★★★★ | ★★☆ | ⭐⭐⭐ |

---

## 二、各方向详细分析

---

### 方向 1：Agent Skills 生态大规模特征分析（Mining Study）

#### 核心定位
**对 skillsmp.com 27万+ 社区 Skills 进行首次系统性的大规模挖掘与特征刻画。**

> [!IMPORTANT]
> 这是与团队现有数据基础设施最匹配、启动成本最低、且学术价值极高的方向。目前无任何论文对这一快速增长的生态进行过系统性实证分析。

#### 研究问题（RQs）

| RQ | 具体问题 | 分析方法 |
|:---|:---------|:---------|
| RQ1 | **Skills 的功能分布是什么样的？** 主要集中在哪些领域（开发工具、DevOps、文档、AI/ML...）？长尾分布如何？ | NLP 主题建模（LDA/BERTopic）、手动编码验证 |
| RQ2 | **Skills 的结构复杂度如何？** 有多少包含脚本/模板/引用？平均 token 数？YAML 元数据的规范遵循度如何？ | 静态分析、规范校验脚本 |
| RQ3 | **Skills 的质量分布如何？** 高星 vs 低星 Skills 有什么结构性差异？描述的清晰度、步骤的完整性？ | 质量评分框架（人工+LLM 混合编码） |
| RQ4 | **Skills 的重复与克隆现象有多严重？** 有多少 Skills 是复制粘贴或轻度修改的？ | 代码/文本克隆检测（D-ECT、SimHash） |
| RQ5 | **Skills 创作者的活跃模式？** 头部创作者贡献了多少？组织 vs 个人比例？ | 社区网络分析、Lorenz 曲线/Gini 系数 |

#### 数据利用
- **直接利用**：已采集的 [skills_metadata.json](file:///Users/tan/Desktop/RA3/skills_data/skills_metadata.json)（125MB）、[skills_metadata.csv](file:///Users/tan/Desktop/RA3/skills_data/skills_metadata.csv)（95MB）
- **需要补充**：下载更多 Skills 的完整 `SKILL.md` 内容（当前 sampled 约 500 份）
- 可扩大采样规模至 2000-5000 份进行深度内容分析

#### 方法论设计
```
Phase 1: 全量元数据统计分析（RQ1, RQ5）
  ↓ 27万+ metadata 记录
Phase 2: 分层采样 + 内容深度分析（RQ2, RQ3）
  ↓ 2000-5000 份完整 SKILL.md
Phase 3: 克隆/重复检测（RQ4）
  ↓ 全文相似度矩阵
Phase 4: 质量评估框架构建与验证
  ↓ 人工编码 + Cohen's Kappa
```

#### 可参考的论文范式
- GitHub Actions 的 Mining Study（ICSE 2021）
- npm/PyPI 生态系统分析（FSE/ESEC 系列）
- Docker Hub 镜像分析（MSR 系列）

#### 投稿目标
MSR (Mining Software Repositories)、ESEC/FSE、ICSE-SEIP

---

### 方向 2：Skills 质量与有效性实证评估（Effectiveness Study）

#### 核心定位
**系统地回答"什么样的 Skill 设计特征决定了它对 Agent 表现的提升效果"。**

#### 与 SkillsBench 的差异化

> [!NOTE]
> SkillsBench (arXiv:2602.12670) 已经证明了 *curated skills > no skills > self-generated skills* 的大方向。但它仅使用了 86 个精心设计的 task-skill 对，没有分析 **wild skills**（社区实际创建的 skills）的有效性。

| 维度 | SkillsBench | 本研究（差异化） |
|:-----|:------------|:-----------------|
| 数据源 | 研究者精心编写的 86 个 curated skills | 社区实际创建的 "in-the-wild" skills |
| 分析粒度 | 有/无 skills 的 pass rate 对比 | 分析 skill 内部哪些**设计特征**（长度、结构、脚本化程度）驱动了效果 |
| 领域覆盖 | 11 个预定义 domain | 来自 skillsmp.com 的自然领域分布 |
| 核心贡献 | 证明 skills 有用 | 回答**怎样的 skills 更有用**（可操作的设计指南） |

#### 研究问题（RQs）

| RQ | 具体问题 |
|:---|:---------|
| RQ1 | Skill 的 **长度**（token 数）与任务成功率之间是什么关系？是否存在"甜蜜点"？ |
| RQ2 | Skill 中包含 **可执行脚本** vs 纯指令文本，对任务可靠性的影响如何？ |
| RQ3 | Skill 的 **结构化程度**（步骤编号、错误处理、输入输出示例）与效果的相关性？ |
| RQ4 | **多 skill 组合** 的效果：协同增益还是 context 污染？最优数量是多少？ |

#### 实验设计（草案）
1. 从 skillsmp.com 采样 200-500 个真实 skills（按领域/质量分层）
2. 为每类 skill 设计 3-5 个评估任务（手动 + LLM 辅助生成）
3. 控制变量实验：相同任务下，分别使用 {无skill, 原始skill, 精简skill, 扩展skill}
4. 多模型测试：Claude 3.5 Sonnet, GPT-4o, Codex, 开源模型
5. 多维度指标：任务完成率、token 效率、输出一致性、首次正确率

#### 挑战与应对
- **评估任务的构造成本高** → 复用 SkillsBench 的 Harbor 容器化框架
- **实验规模 vs 成本权衡** → 先在开源模型上大规模筛选，再在商业模型上精细验证

---

### 方向 3：Agent Skills 安全漏洞大规模分析（Security Study）

#### 核心定位
**对社区 Skills 进行首次大规模安全漏洞分析，揭示 Agent Skills 生态的安全风险全景。**

> [!WARNING]
> 搜索结果显示，已有一篇 "Agent Skills in the Wild: An Empirical Study of Security Vulnerabilities at Scale"（2026.01-02）在 arXiv 上。需要确认其具体内容，评估是否仍有空间。如果该论文已覆盖核心贡献，则需要进一步差异化（如关注 supply chain attack、权限提升等更细分的安全主题）。

#### 研究问题（RQs）

| RQ | 具体问题 |
|:---|:---------|
| RQ1 | 社区 Skills 中包含**可执行脚本**的比例是多少？这些脚本存在哪些安全漏洞类型？ |
| RQ2 | Skills 的**权限声明**（如 tools: [Bash, Read, Write]）是否遵循最小权限原则？过度权限声明的普遍程度？ |
| RQ3 | 是否存在**PromptInjection**风险——恶意 skill 指令是否可能劫持 Agent 行为？ |
| RQ4 | Skills 依赖的**外部资源**（API、URL、npm 包）存在供应链攻击风险吗？ |

#### 方法论
1. **静态分析**：对所有含脚本的 skills 运行 CodeQL / Semgrep / Bandit
2. **权限分析**：解析 YAML 元数据中的 `tools` 字段，评估权限合理性
3. **Prompt 注入检测**：构建 adversarial prompt 模式库，检测 skill 指令中的注入模式
4. **依赖安全审计**：提取外部依赖列表，交叉比对已知漏洞库（CVE/npm audit）

#### 数据利用
- 从 27万+ skills 中筛选含脚本的子集（预估 5-15%）
- 对筛选后的脚本进行自动化扫描

#### 投稿目标
CCS、USENIX Security、S&P（安全方向），或 ICSE/FSE（SE 安全方向）

---

### 方向 4：Skills 生态演化与社区动态研究（Evolution Study）

#### 核心定位
**通过 Git 历史追踪 Skills 的创建、修改、传播模式，揭示这一新兴生态的演化规律。**

#### 研究问题（RQs）

| RQ | 具体问题 |
|:---|:---------|
| RQ1 | Skills 的**修订频率**如何？创建后被持续维护还是"写完即弃"？ |
| RQ2 | Skills 的**跨项目传播**路径是什么？高影响力 skills 如何被 fork/借鉴/标准化？ |
| RQ3 | Skills 生态的**增长速率**和**淘汰率**随时间如何变化？ |
| RQ4 | **重大平台事件**（如 Anthropic 开放标准发布、SkillsBench 发布）如何影响 skills 发展？ |

#### 数据需求
- 需要采集 skills 所在 GitHub 仓库的 **commit 历史**
- skillsmp.com 的 `updatedAt` 时间戳可作为近似指标
- 需定期快照采集以建立时间序列

#### 挑战
- Git 历史采集成本较高（需 clone 大量 repo）
- 可能需要 GitHub API 配额管理

---

### 方向 5：Skills vs. 替代 Prompt 技术的对比实验（Comparative Study）

#### 核心定位
**严格控制变量，对比 Skills 机制与其他 LLM 引导技术的效果差异。**

#### 实验条件

| 条件 | 描述 |
|:-----|:-----|
| Baseline | 裸模型 + 基本任务描述 |
| System Prompt | 将 skill 内容嵌入 system message |
| Few-shot | 等量 token 的输入-输出示例 |
| RAG | 将 skill 内容作为检索文档注入 |
| **Agent Skill** | 标准 skill 格式（SKILL.md + 渐进披露） |
| Hybrid | Skill + RAG 混合 |

#### 测量维度
- 任务完成率、token 消耗、响应延迟
- 多轮对话中的一致性保持
- 对陌生领域的泛化能力

#### 挑战
- 需要底层模型 API 的精细控制（如控制 context 注入方式）
- 公平对比的实验设计（等 token 预算约束）

---

### 方向 6：跨平台互操作性实证研究（Interoperability Study）

#### 核心定位
**评估 Skills 在不同 Agent 平台（Claude Code, Codex, Cursor, Goose 等）之间的实际可移植性。**

#### 研究问题

| RQ | 具体问题 |
|:---|:---------|
| RQ1 | 同一 Skill 在不同平台上的**功能等价性**如何？ |
| RQ2 | 平台特定扩展（如 Claude 的 `allowedTools`、Codex 的 `agents/openai.yaml`）对互操作性的影响？ |
| RQ3 | agentskills.io v0.9 标准草案的**实际采纳度**和**兼容性差距**？ |

---

## 三、综合推荐

### 🔥 最强推荐组合：方向 1 + 方向 3（Mining + Security）

**理由**：
1. **数据复用最大化**：两个方向共享同一数据源（skillsmp.com），采集成本摊薄
2. **互相增强**：方向 1 的结构分析自然提供安全分析的输入特征
3. **学术空白清晰**：目前无任何论文对 27万+ skills 生态做过系统刻画
4. **可拆分为两篇论文**：方向 1 → MSR/ESEC/FSE（SE 社区），方向 3 → CCS/USENIX（安全社区）
5. **与团队能力匹配**：已有数据采集脚本，可快速启动

### 📋 建议的工作计划

```
Phase 1 (Month 1-2): 数据基础设施完善
  - 扩大 SKILL.md 下载规模至 5000+
  - 构建元数据统计分析 pipeline
  - 构建多维度质量分类编码体系

Phase 2 (Month 2-4): 方向 1 核心分析
  - 全量元数据统计（RQ1, RQ5）
  - 采样内容深度分析（RQ2, RQ3）
  - 克隆检测（RQ4）

Phase 3 (Month 3-5): 方向 3 安全分析
  - 脚本提取与静态扫描
  - 权限声明分析
  - Prompt 注入风险评估

Phase 4 (Month 5-6): 论文撰写
  - 两篇论文并行撰写
```

### 备选：如果团队有算力预算

优先加入 **方向 2（有效性评估）**，这是学术影响力最高的方向，但需要大量 API 调用预算。可以考虑：
- 先在开源模型（Llama 3, Qwen 2.5）上做初步实验
- 再用商业 API 做验证性实验
- 复用 SkillsBench 的 Harbor 评估框架降低基建成本

---

## 四、与 SkillsBench 论文的关系定位

> [!TIP]
> SkillsBench 是一个重要的相关工作，但它**不是竞争对手**。本研究的定位是**互补**关系：
> - SkillsBench 回答 "Skills 有没有用"（benchmark quantification）
> - 本研究回答 "社区实际创建了什么样的 Skills"（ecological characterization）和 "什么样的 Skills 更有用/更安全"（design guidelines）
> 
> 可以在论文中明确引用 SkillsBench 的发现，并指出本研究从 "in-the-wild" 视角的独特贡献。
