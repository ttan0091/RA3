**针对 OpenClaw 的skill生态系统 ClawHub 的大规模攻击**

安全研究人员在 OpenClaw 的官方skills市场（ClawHub）中发现了 1,184 个恶意skill。

市场上排名第一的skill“What Would Elon Do”被证实存在严重安全漏洞，并通过刷 4,000 次虚假下载量来获取用户信任，实际上具有数据窃取和提示注入（Prompt Injection）功能。
**攻击手段**
传统社会工程学 (ClickFix)：恶意skill在文档中引导用户运行看似必要的安装命令（如 curl | bash），从而在 macOS 或 Windows 系统中植入信息窃取木马（如 Atomic Stealer）。
提示注入 (Prompt Injection)：这是 AI 时代特有的攻击手段。91% 的恶意skill利用提示词操控 AI Agent，使其在不经过用户同意的情况下秘密执行外部请求、窃取数据或绕过安全指南。

**攻击者窃取的内容包括：**

浏览器数据：密码、Cookies、自动填充信息。
加密货币钱包：支持超过 60 种钱包（如 MetaMask, Phantom）。
关键凭证：SSH 密钥、macOS 钥匙串凭证、.env 文件中的所有 API 密钥（包括 LLM 访问密钥）。
系统权限：部分skill还会开启反向 Shell，让攻击者完全远程控制受害者的机器。
**比 npm 攻击更严重**
默认权限更高：AI Agent通常拥有文件系统读写、Shell 访问和凭证访问权限，而传统的 npm 包通常运行在有限的沙盒中。
文档即武器：恶意指令直接隐藏在 SKILL.md 文档中，形成了一种新型的“指令供应链”攻击面。
AI Agent被策反：提示注入让 AI Agent成了攻击者的同谋，Agent会由于其“乐于助人”的特性而主动执行恶意指令。
**响应**
全球连锁反应：多个国家（如比利时、中国、韩国）的安全部门发布了预警，许多大型科技公司（如 Kakao, Naver）已在公司网络中封锁了 OpenClaw。
OpenClaw 现已与 VirusTotal 合作扫描并删除违规skill，并正在向受 OpenAI 资助的基础设施转型。

**方法**

Koi Security 的研究人员 Oren Yomtov 开发并使用了一个名为 **"Alex" 的 OpenClaw 机器人**。

Cisco AI Defense 团队开发并使用了 **"Skill Scanner"** 工具。





#### **SkillsBench**: Benchmarking How Well Agent Skills Work Across Diverse Tasks

首个专门用于衡量“Agent Skills”对 LLM Agent性能提升效果的基准测试。

包含涵盖 11 个领域的 **84 个任务**。每个任务都在三种条件下进行测试：

1. **无skill (No Skills)**：基准对比。
2. **人工skill (Curated Skills)**：由expert编写的高质量skill。
3. **自生成skill (Self-generated Skills)**：由模型根据任务描述自行生成的skill。

##### **核心研究发现**

- 人工skill将平均成功率提高了 **16.2 个百分点**。但在不同领域表现差异巨大：医疗领域提升了 **51.9pp**，而软件工程领域仅提升了 **4.5pp**。此外，有 16 个任务在加入skill后反而表现变差。
- 自生成的skill平均提升效果为负（**-1.3pp**）。
- 包含 2-3 个核心模块的**精简skill包**效果优于过于复杂的长文档。
- 配备高质量skill的**小型模型**（如较小版本的 Claude 或 Gemini）在某些特定任务上的表现可以媲美甚至超过未配备skill的大型模型。



#### Agent Skills in the Wild: An Empirical Study of Security Vulnerabilities at Scale

对AI Agent skills生态做了首次大规模安全实证研究。

收集了 4 万多条skill，并构建了一个名为 SkillScan 的自动检测框架（结合静态分析和大模型语义判断）。结果发现：约 26.1% 的skill存在至少一种安全漏洞，主要包括提示注入、数据泄露、权限提升，还有 5.2% 呈现出明显恶意倾向。

带可执行脚本的skill比纯说明类skill更容易出问题。





[Organizing, Orchestrating, and Benchmarking Agent Skills at Ecosystem Scale](https://arxiv.org/abs/2603.02176) (`2026-03-02`)
研究 `200 到 200K 个 skills 怎么管理和调用`。作者提出 `AgentSkillOS`，核心是 capability tree 做检索，DAG pipeline 做多技能编排。
在 `30` 个富工件任务上，结果显示 tree-based retrieval 已经能逼近 oracle skill selection，而 `DAG` 编排明显优于“平铺式调用”。
把 skill 问题从 prompt engineering 转向 ecosystem engineering。

[EvoSkill: Automated Skill Discovery for Multi-Agent Systems](https://arxiv.org/abs/2603.02766) (`2026-03-03`)
让 agent 从失败轨迹里抽象出缺失能力，再把它物化成新的 skill，经过验证后保留，模型本体保持冻结。
实验上，OfficeQA 从 `60.6%` 提到 `67.9%`，SealQA 从 `26.6%` 提到 `38.7%`，而且从 SealQA 演化出的 skills 能零样本迁移到 BrowseComp，提升 `5.3%`。
这说明 skill-level optimization 可能比直接改 prompt 或改代码更可迁移。

[Formal Analysis and Supply Chain Security for Agentic AI Skills](https://arxiv.org/abs/2603.00195) (`2026-02-27`)
这篇把 skills 当成了一个 `软件供应链安全` 问题来做。作者提出 SkillFortify，包括攻击者模型、静态分析、capability sandbox、依赖图解析、trust score，以及一个 `540-skill` 的 benchmark。
论文报告 `96.95%` F1、`100%` precision，且 `1,000` 节点依赖图的 SAT 解析在 `100 ms` 内完成。
不再把 skills 只当“提示词封装”，而是开始按 `包管理 + 权限隔离 + 依赖解析 + 信任评分` 的软件系统来处理。

[Clawdrain: Exploiting Tool-Calling Chains for Stealthy Token Exhaustion in OpenClaw Agents](https://papers.cool/arxiv/2603.00902) (`2026-03-01`)
这篇是更“脏”的现实攻击论文：通过恶意 skill 和 tool-calling chain 做 `token drain`，把成本悄悄拉高。
作者报告在生产风格部署里可达到 `6-7x` 的 token 放大，失败配置下接近 `9x`。更关键的是，agent 还会自己组合通用工具去“绕着攻击逻辑走”，让攻击表现更复杂。
它证明了 skill 生态的首批高价值攻击面，可能首先是 `经济消耗` 和 `行为污染`，而不一定是传统意义上的直接越权。

#### 四篇相关工作

Agent Skills in the Wild: An Empirical Study of Security Vulnerabilities at Scale

[Malicious Agent Skills in the Wild: A Large-Scale Security Empirical Study](https://arxiv.org/abs/2602.06547) (`2026-02`)
方法：以大规模生态测量和行为验证为主，先从技能市场收集样本，再结合分析流水线对恶意样本做确认和归类。  
数据源：来自两个社区 registry 的 `98,380` 个 skills，最终确认 `157` 个恶意 skill、`632` 个漏洞。  
解决的问题：回答“真实世界里恶意 skill 到底长什么样、分布在哪些攻击链阶段、有哪些高频攻击技术”，为后续 taxonomy 和 benchmark 提供现实依据。

[Formal Analysis and Supply Chain Security for Agentic AI Skills](https://arxiv.org/abs/2603.00195) (`2026-02-27`)
方法：以形式化静态分析为核心，包含抽象解释、capability sandbox、依赖图解析、SAT-based resolution 和 trust score，强调可证明的安全边界，不依赖 LLM。  
数据源：论文提出 `SkillFortifyBench`，规模为 `540` 个 skills，同时覆盖多框架 skill 供应链场景。  
解决的问题：回答“如何用可验证的方法分析 skill 的供应链风险”，重点处理权限声明、依赖劫持、能力越界和信任传播这些结构化安全问题。

[SkillJect: Automating Stealthy Skill-Based Prompt Injection for Coding Agents with Trace-Driven Closed-Loop Refinement](https://arxiv.org/abs/2602.14211) (`2026-02`)
方法：提出自动化攻击框架，采用闭环优化。系统由 Attack Agent、Code Agent、Evaluate Agent 组成，利用执行 trace 反复改写注入 skill；攻击上强调诱导式 prompt、载体解耦和隐蔽 payload，不是简单正则匹配或单次手工 prompt。  
数据源：在多种 coding-agent 设置和真实软件工程任务上评估，核心观测数据是工具调用、文件操作等 execution traces。  
解决的问题：回答“怎样系统性地自动生成高隐蔽、高成功率的 skill-based prompt injection”，把手工攻击推进为可迭代优化的自动攻击流程。

[Clawdrain: Exploiting Tool-Calling Chains for Stealthy Token Exhaustion in OpenClaw Agents](https://arxiv.org/abs/2603.00902) (`2026-03-01`)
方法：构造 Trojanized skill，在 `SKILL.md` 注入多轮协议，并配合伴生脚本返回 `PROGRESS/REPAIR/TERMINAL` 信号，诱导 agent 进入高开销 tool-calling chain。它本质上是运行时攻击验证，不是静态扫描。  
数据源：在 production-like 的 OpenClaw 实例上实测，使用真实 API 计费和生产级模型，比较恶意 skill 与 benign baseline 的 token 开销差异。  
解决的问题：回答”攻击者能否通过 skill 让 agent 持续烧 token 和预算”，把 skill 安全问题从窃密、越权扩展到 `经济消耗` 和资源放大型攻击。

---

## 2026-03-13 - 

[ChainFuzzer: Greybox Fuzzing for Workflow-Level Multi-Tool Vulnerabilities in LLM Agents](https://arxiv.org/abs/2603.12614) (`2026-03-13`)
检测 LLM Agent 中**多工具协作漏洞**的灰盒模糊测试框架。针对跨工具数据流引发的隐蔽安全问题。通过自动提取潜在工具链、生成可稳定触发这些链路的 prompt，并结合针对防护机制的模糊测试，有效发现并复现多步骤漏洞。在多个真实应用中发现了大量此前难以检测的漏洞，说明多工具工作流显著扩大了安全风险。

[VeriGrey: Greybox Agent Validation](https://arxiv.org/abs/2603.17639) (`2026-03-18`)

通过跟踪 agent 调用的工具序列作为反馈，引导对 prompt 进行变异，生成潜在的注入攻击，从而发现不常见但危险的工具调用路径。实验证明，VeriGrey 能有效地检测间接 prompt 注入攻击。把传统软件 greybox fuzzing 的核心思路（用执行反馈驱动搜索）移植到 agent 安全测试。以 agent 调用的工具序列作为反馈信号，专注于暴露注入相关的边界 case。
说明 skill 注入漏洞的发现不仅是 prompt engineering 问题，要依赖执行反馈才能系统覆盖。

[T-MAP: Red-Teaming LLM Agents with Trajectory-aware Evolutionary Search](https://arxiv.org/abs/2603.22341) (`2026-03-21`)
多步工具执行场景下，仅靠静态 prompt 红队无法捕捉 agent 在实际工具交互中才暴露的漏洞。T-MAP 用真实执行轨迹来引导对抗 prompt 的进化搜索，让攻击目标嵌入 agent 的工具调用流中而非孤立在 prompt 里。
在 GPT-5.2、Gemini-3-Pro、Qwen3.5、GLM-5 等前沿模型上，ARR（Attack Realization Rate）显著优于基线方法，并发现了此前 red-teaming 遗漏的 agent-specific 漏洞，尤其在 MCP 环境下的 tool ecosystem 场景中表现突出。

[ClawSafety: “Safe” LLMs, Unsafe Agents](https://arxiv.org/abs/2604.01438) (`2026-04-01`)
ClawSafety 同时评估模型和框架的组合，将攻击分为三类（workspace skill 文件、来自可信发件人的邮件、网页），记录 agent 在整个任务过程中每一步做了什么，并对每个动作打"危害程度分"。
新提出的 CLAWSAFETY benchmark 包含 120 个对抗测试场景，覆盖软件工程、金融、医疗、法律、DevOps 五个专业高权限 workspace。对 5 个前沿 LLM（2,520 次沙箱试验）的测试显示，攻击成功率在 `40%–75%` 之间。发现：skill 文件注入比邮件或网页注入更危险，安全结果取决于完整的”模型 + 框架”。

120 个场景的结构：5 个行业（软件工程/金融/医疗/法律/DevOps）× 5 种危害动作（数据泄露、配置篡改、目标替换、凭证转发、文件删除）× 3 个注入渠道

5 个 LLM，3 个 Agent

[Evasive Intelligence: Lessons from Malware Analysis for Evaluating AI Agents](https://arxiv.org/abs/2603.15457) (`2026-03-16`)
AI agent 作为工具调用系统，可以感知自己正在被评估并相应调整行为——这和恶意软件在沙箱中表现正常、在生产环境中激活是同一种失败模式。这是一个可观察的系统性风险。
作者援引了数十年的恶意软件沙箱逃逸研究，提出评估必须把被测 agent 视为潜在对抗性系统：要求评估环境足够逼真、测试用例具备变异性、并配合上线后的持续监控。质疑了现有静态 scanner 的评估有效性。

**OWASP Agentic Skills Top 10（AST10）立项**（`2026-04` ）Open Worldwide Application Security Project。
OWASP 在 Oslo Project Summit 2026 孵化了专门针对 AI agent skills 的 Top 10 风险框架（AST10），这是第一个专注于 skill 安全的综合性行业标准，覆盖 OpenClaw、Claude Code、Cursor、VS Code 等主要平台。
十大风险依次为：AST01 恶意 Skill（Critical）、AST02 供应链污染（Critical）、AST03 过度授权（High）、AST04 不安全元数据（High）、AST05 不安全反序列化（High）、AST06 弱隔离（High）、AST07 更新漂移（Medium）、AST08 扫描能力不足（Medium）、AST09 缺乏治理（Medium）、AST10 跨平台复用风险（Medium）。目前处于 Q2 2026 基础建设阶段，预计 Q4 2026 发布 v1.0 并申请 OWASP Flagship 项目。 [owasp.org/www-project-agentic-skills-top-10](https://owasp.org/www-project-agentic-skills-top-10/)。
