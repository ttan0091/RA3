

### 4.1 Static Analyzer

这是它的第一层基线。

核心方法包括：

- YAML signatures
- YARA 规则
- 文件清单与结构检查
- frontmatter / manifest 检查
- 工件一致性检查
- `allowed-tools` 与代码行为一致性检查

它关注的模式包括：

- prompt injection
- data exfiltration
- hardcoded secrets
- obfuscation
- supply chain
- unauthorized tool use
- social engineering
- resource abuse

它的一个关键特点是：不仅扫文档文本，还检查“skill 的声明”和“脚本的行为”之间是否一致。例如：

- 没声明 `Bash`，但脚本里实际执行 shell
- 没声明 `Read/Write`，但代码里实际读写文件
- skill 代码里存在 network usage，但文档里没有合理说明

这一层的优点是快、可解释、易接 CI。

这一层的局限是也很明显：

- 容易被变形文本、分阶段下载、远端内容拉取绕开
- 语义性很强的欺骗不容易只靠规则抓住

### 4.2 Pipeline Analyzer

这是这个项目里比较有价值的一层，因为它不是只扫单条命令，而是做 **命令管道级污点分析**。

它会把 shell pipeline 拆成 source、transform、sink 三类节点，例如：

- source：`cat`、`find`、`grep`、`env`
- transform：`base64`、`xxd`、`gzip`
- sink：`curl`、`wget`、`bash`、`python`、`tee`

然后跟踪 taint 的流动，例如：

- 敏感文件读取
- 用户输入
- 网络数据
- 混淆
- 执行
- 网络发送
- 文件系统写入

它的目标是抓这种“单看每一步不一定高危，但连起来就是攻击链”的模式，例如：

`read secret -> encode -> send`

所以它本质上在解决一个简单正则很难做好的问题：**多步组合攻击。**

### 4.3 Behavioral Analyzer

Behavioral analyzer 的核心是 **静态数据流和跨文件行为分析**。

它主要做：

- Python AST parsing
- function / script context extraction
- call graph construction
- cross-file correlation
- bash taint tracking
- markdown code blocks 的代码分析

这层不是看“你写了哪些危险词”，而是看：

- 代码真实的数据流是什么
- 哪些函数调用串起来构成能力
- skill 描述和真实行为是否一致

从研究角度看，这一层更接近：

- purpose-permission mismatch
- description-behavior mismatch
- source-to-sink analysis

它是该项目中最接近“语义程序分析”的一层。

### 4.4 LLM Analyzer

LLM analyzer 是一个 **LLM-as-a-judge** 模块，但不是最原始的那种直接裸判。

它有几个重要设计：

- provider abstraction
- prompt builder
- response parser
- structured schema output
- retry / timeout / rate limit handling
- 可多轮运行后做 consensus
- 接收 Phase 1 的 enrichment context

也就是说，它不是直接让模型从零看 skill，而是让模型带着：

- 文件分布
- magic mismatch
- 高优先级 static findings
- 其他摘要信息

去做更高层的 threat reasoning。

这比“直接把 skill 文本贴给模型然后问安不安全”更强一些，但本质上仍然属于 `LLM-based semantic analysis`。

### 4.5 Meta Analyzer

Meta analyzer 是第二层 LLM。

它不直接看原始 skill，而是看前面多个 analyzer 的 findings，再做：

- false positive filtering
- exploitability / impact prioritization
- cross-analyzer correlation
- missed threat detection
- remediation suggestion

换句话说，它在系统里的作用不是 primary detector，而是 **reviewer / triage / prioritizer**。

这是一个比较合理的架构选择，因为它把 LLM 放在“复核 findings”这个位置，而不是让它主导第一层 detection。

### 4.6 外部扫描器

这个项目还支持两个外部服务：

- VirusTotal analyzer
- Cisco AI Defense analyzer

前者主要用于二进制哈希与恶意样本校验。

后者相当于把部分文本内容送到 Cisco AI Defense 云侧做补充分析。

这说明它的整体策略不是纯本地扫描，而是：

- 本地静态分析
- 本地语义分析
- 云侧补充判断

三者结合。

## 5. 它的关键设计思想

### 5.1 多引擎而不是单引擎

这个项目最关键的思想是：没有假设某一种 detector 能单独搞定所有问题。

所以它把问题拆成：

- signature 问题
- program analysis 问题
- source-sink 问题
- semantic reasoning 问题
- malware / reputation 问题

然后分别交给不同 analyzer。

### 5.2 两阶段而不是一锅炖

它把 LLM 放到第二阶段，是个很重要的设计选择。

这样做的好处是：

- 先用便宜、确定性的 analyzer 做粗筛
- 再让模型看已经被结构化过的上下文
- 减少完全依赖 LLM 直接判决的脆弱性

这也是它比简单“LLM 扫 skill”更像工程系统的地方。

### 5.3 fail-closed analyzability

它明确考虑了一个现实问题：scanner 并不总能读懂所有内容。

所以它增加了 analyzability 评分，并对不可分析的内容给出：

- `UNANALYZABLE_BINARY`
- `LOW_ANALYZABILITY`

这背后的理念是：

**看不懂不等于安全。**

这个思路对 skill security 很重要，因为 skill 包里完全可能带：

- 压缩包
- 二进制
- 混淆脚本
- extension/content mismatch 文件

### 5.4 taxonomy 映射

它把 findings 映射到 Cisco AI Security Framework 的 `AITech / AISubtech`。

这使得它不只是一个“报风险字符串”的工具，而是一个有统一 threat model 的系统。映射的类别包括：

- Prompt Injection
- Transitive Trust Abuse
- Data Exfiltration
- Tool Chaining Abuse
- Hardcoded Secrets
- Command Injection
- Code Execution
- Supply Chain Attack
- Unauthorized Tool Use
- Resource Abuse
- Social Engineering

这对于研究工作很有价值，因为它提供了：

- 标准化 threat categories
- 跨工具比较的标签基础
- 自定义 taxonomy / cross-framework mapping 的扩展点

## 6. 它能解决什么问题

这个工具最适合处理的，是以下几类问题：

- 明显的 prompt injection / override 文本
- `allowed-tools` 与真实行为不一致
- shell pipeline 形式的数据读取、混淆和外传
- Python / bash 里的可疑 source-sink 行为
- skill 包里的秘密、混淆、可疑二进制、结构异常
- 多 analyzer 汇总后能进一步确认的高风险 finding

它尤其适合：

- skill marketplace 准入前扫描
- CI / pre-commit 扫描
- 企业内部第三方 skill intake 流程

## 7. 它解决不了什么问题

README 也明确承认，这是 `best-effort detection`，不是认证系统。

从方法上看，它的主要局限包括：

- 静态规则仍然容易被文本变形、拆分表达、远端二阶段加载绕过
- behavioral analyzer 虽然更强，但仍然是静态分析，不是真实执行
- LLM analyzer 仍可能受输入内容和上下文设计影响
- 即便是两阶段结构，也不能彻底避免新型攻击与漏报
- 它主要是在做“准入扫描”和“风险提示”，不是 runtime containment

也就是说，它擅长在 skill 上线前发现很多问题，但不等于可以替代：

- runtime guardrails
- egress control
- secret sandboxing
- human review

## 8. 对研究的启发

从 `agent skill security` 研究角度看，这个仓库最有价值的地方在于，它已经把常见方案从单点 scanner 推进到了一个更接近实际部署的框架。

它给出的几个重要启发是：

### 8.1 skill 检测对象应该是 package，不只是 `SKILL.md`

这个项目从 loader 到 analyzers 都在强调：

- `SKILL.md`
- scripts
- markdown code blocks
- archives
- binaries
- references / assets

都属于 skill 的攻击面。

这和只扫一份 markdown 的做法差别很大。

### 8.2 scanner 不应只依赖单个 LLM judge

这个项目虽然用了 LLM，但它没有把 LLM 放在唯一 detector 的位置。

它先做静态与结构分析，再让 LLM 做语义补充和 meta review。这一点本身就是对“纯 LLM 扫描器”局限的工程性回应。

### 8.3 source-sink 与 tool-chain 分析很关键

这个项目里最值得继续研究的，不一定是 prompt pattern 本身，而是：

- pipeline taint
- behavioral dataflow
- cross-file correlation
- allowed-tools vs real behavior mismatch

这些都更接近真实风险。

### 8.4 仍然缺 runtime 层

尽管它做了很多静态和半语义分析，但它主要还是 pre-deployment scanner。

所以如果做后续研究，一个自然的方向是：

- skill scanner + runtime guard 的联合评测

即：

- skill scanner 负责前置筛查
- runtime 层负责拦截实际外传、危险执行和 secrets 滥用

## 9. 我的判断

如果把当前公开的 agent skill 检测工具做一个层次划分，Cisco 这个项目属于比较完整的一档，因为它已经具备：

- 统一 skill loader
- 多 analyzer 编排
- 两阶段扫描
- LLM enrichment
- meta filtering
- policy system
- taxonomy mapping
- CI / API / pre-commit 接入能力

它不是一个简单 demo，而是一个已经相当工程化的 skill security scanner。

但它的边界也很明确：它更像一个 **准入审查和风险发现系统**，而不是一个完整的 end-to-end 安全闭环。

如果把它放进更大的 agent security 体系里，比较合理的位置是：

- 上游：marketplace / registry intake
- 中游：CI / code review / security review
- 下游：runtime guardrails, DLP, egress control, secret isolation

## 10. 关键源码位置

- 架构总览：`docs/architecture/index.md`
- 扫描流程：`docs/architecture/scanning-pipeline.md`
- taxonomy：`docs/architecture/threat-taxonomy.md`
- orchestrator：`skill_scanner/core/scanner.py`
- analyzer factory：`skill_scanner/core/analyzer_factory.py`
- loader：`skill_scanner/core/loader.py`
- static analyzer：`skill_scanner/core/analyzers/static.py`
- behavioral analyzer：`skill_scanner/core/analyzers/behavioral_analyzer.py`
- pipeline analyzer：`skill_scanner/core/analyzers/pipeline_analyzer.py`
- llm analyzer：`skill_scanner/core/analyzers/llm_analyzer.py`
- meta analyzer：`skill_scanner/core/analyzers/meta_analyzer.py`
- rules pack：`skill_scanner/data/packs/core/`

