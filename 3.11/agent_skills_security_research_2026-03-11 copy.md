

### 3.2 动态

| 日期 | 来源 | 内容 | 意义 |
| --- | --- | --- | --- |
| 2026-03-16 | Vercel Docs, *Agent Skills* | 官方目录把 skill 定义为 `packaged capability`，并强调每个 skill 都是 `verified, documented, and ready to integrate` | skill 安全治理开始进入 `verified directory` 和目录准入阶段，不再只是本地安装前扫描 |
| 2026-03-11 | OpenAI, *Designing AI agents to resist prompt injection* | 把 prompt injection 更明确地表述为 `social engineering` 问题，强调 `source-sink analysis`、用户确认和 sandbox 侧防护 | 除了识别恶意文本意外，真正要控制的是被操纵后的行动 |
| 2026-03-11 | OpenAI, *From model to agent: Equipping the Responses API with a computer environment* | 更完整公开了 skill bundle 的装载、解包、上下文注入、容器执行 | 从 `SKILL.md` 扩展到 `skill loading pipeline` 与 runtime 资源边界 |
| 2026-03-09 | Microsoft Security, *Secure agentic AI for your frontier transformation* | 强调 `AI inventory`、`Inline DLP for prompts`、`runtime threat protection`、`real-time policy enforcement` | 强调运行时和数据流控制，不仅依赖文本扫描 |
| 2026-03-06 | OpenAI, *Codex Security now in research preview* | 强调从系统上下文、权限与工作流边界出发做 `security review` 和 `validation` | 要看 agent 的真实执行上下文 |
| 2026-03-04 | Snyk Live / Labs 页面与相关 agent 扫描材料 | 强调 `agent scan`、`skill inspector`、`supply chain` 视角 | skill 风险被纳入更大的 agent / MCP / tool 供应链问题中统一处理 |

只靠扫 `SKILL.md` 并不足以拦截风险

#### 4.1.1 SKILL-INJECT

`SKILL-INJECT` 是一个公开基准，回答把恶意指令写进 skill 文件，agent 是否会遭到注入攻击。

SKILL-INJECT 包含 202 组“注入—任务”配对，攻击形式从明显恶意的注入，到隐藏在看似正常指令中的、依赖上下文的隐蔽攻击。

结果表明，当今的Agent 非常脆弱，在前沿模型中攻击成功率最高可达 80%，且往往会执行极具危害性的指令，包括数据外泄、破坏性操作以及类似勒索软件的行为

项目主页给出的结论包括：

简单的输入过滤和 prompt-level defense 效果有限。

如果 scanner 只是“用一个更强的模型读 skill 文件，然后输出 safe/unsafe”，并不能自然提升防御效果。

如果 defense 主要停留在 prompt 模板层，它很可能和被测对象处于同一个攻击面里。

来源：<https://www.skill-inject.com/>

### 4.2 代表性工具

| 工具 | 主要对象 | 典型检测方式 |
| --- | --- | --- |
| `ClawKit ai-skill-scanner` | 单个 skill | 静态模式匹配、可疑模式检测 |
| `Clawned` | `SKILL.md` 与 skill 工件 | 解析 frontmatter、权限、依赖、脚本、系统提示、数据工件并做 threat pattern 检查 |
| `SkillScan / SkillRisk` | skill、更新流和风险追踪 | provider-agnostic 扫描、提交漂移监控、已知模式检查 |
| `AgentVerus` | skills、MCP、agents | 多 analyzer 并行，覆盖 permission、prompt injection、dependencies、behavior |
| `PRAQTOR MCP-S` | MCP / skills / configs | 多 engine：YAML、secrets、prompt、deps、exfil、permissions 等 |
| `Snyk Agent Scan / mcp-scan` | agents / MCP / 生态链路 | 确定性检查 + AI model 分析 |
| `Microsoft / Akto` 等 runtime guardrails | agent 运行时 | DLP、action policy、real-time enforcement |

## 5. 检测方式的技术分类

### 5.1 Rule-based / Signature-based

最常见的一类。典型做法是：

- 匹配危险命令、可疑 URL、下载执行链
- 匹配 secrets、token、entropy、高危字符串
- 匹配已知 prompt injection pattern
- 匹配高风险权限或可疑脚本组合

代表工具：

- `ClawKit ai-skill-scanner`
- 一部分 `Clawned` / `SkillScan` / `mcp-scan` 的确定性规则

### 5.2 结构化静态分析

这类方法不只是扫纯文本，而是把 skill 当成一个包含多个部件的工件：

- `SKILL.md`
- frontmatter / metadata
- 权限声明
- 依赖与脚本
- 数据文件
- 示例命令
- 外部链接和下载点

代表工具：

- `Clawned`
- `PRAQTOR MCP-S`
- `SkillScan`

优点：

- 能检查“skill 说自己做什么”和“skill 实际请求了什么”之间的一致性
- 能覆盖跨文件 风险

### 5.3 LLM-based 语义扫描

这类方法让模型直接读 skill 文本、说明、脚本片段或解析结果，然后判断：

- 是否存在隐藏指令
- 是否存在 instruction override
- 是否存在 social engineering
- 是否存在 purpose mismatch
- 是否有 prompt injection 风险

代表工具：

- `AgentVerus` 的部分 analyzer
- `mcp-scan` 的 AI-assisted checks
- 若干产品里的“AI risk reviewer”

优点：

- 能识别规则系统难以枚举的语义风险
- 能理解伪装性很强的自然语言说明

失效点：

- 如果把未净化的被扫文本直接喂给判定模型，scanner 自己就暴露在 prompt injection 面前
- 如果模型只返回一个自然语言 verdict，而没有证据片段与结构化理由，系统会非常脆弱

LLM 不是天然更强的 detector；如果架构不对，它会成为最容易被操纵的 detector。

### 5.4 Hybrid：规则 + 语义 + 策略

当前最稳健的方向是混合式：

- 先做确定性结构提取
- 再对高风险片段做语义分析
- 最后由外部 policy engine 做准入决策

代表工具：

- `Snyk mcp-scan`
- `PRAQTOR MCP-S`
- 企业侧 agent security 平台

优点：

- 比单一 LLM 判定更稳
- 比纯规则更能覆盖自然语言攻击

### 5.5 Runtime Guardrails

这类方法不把希望押在“上线前必须完全看懂恶意文本”，而是在 agent 真要执行动作时做限制：

- 调用 shell 前审批或拦截
- 敏感文件访问控制
- Prompt / response DLP
- 凭证与 secrets 隔离
- 网络外传和异常调用链审计

代表方向：

- Microsoft Security 的 agent inventory + DLP + runtime protection
- Akto 的 session-based / real-time guardrails

优点：

- 对文本级伪装不敏感
- 对 staged attack 更稳
- 能拦截真实危害而不是只拦“看起来像恶意的文字”

## 10. 综合判断

当前 skill security 的生态分成三条线：

-  `skill artifact scanning`
-  `agent runtime protection`
-  `registry governance`

gap：

当 scanner 自己也在读不可信 prompt-like 内容时，怎样设计能避免它被被扫对象本身操纵。

当 scanner、runtime guard 和 skills registry 一起构成防线时，哪些风险应该在文本层发现，哪些应该在动作层发现。




