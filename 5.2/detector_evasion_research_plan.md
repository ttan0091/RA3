# Skill 恶意检测器规避研究计划

## 1. 目标重定义

基于 `5.2/4_会议纪要.md`，本阶段研究对象定义为：

> Skill maliciousness detector evasion：在保留待评测恶意能力语义标签的前提下，评估已知 adversarial attack、LLM-as-a-judge 欺骗、代码漏洞检测器规避方法能否使 skill 检测器输出 benign 或漏检。

本文件只给出防御研究计划、抽象用例模板和评测路线，不写入可执行恶意 skill、真实外传端点、真实凭据读取逻辑或自动绕过脚本。

## 2. 现有项目基线

已有 `4.6/evasion_final_report.md` 给出 53 个 evasion 样本在 5 类 scanner 上的结果：

| 结论 | 证据 |
| --- | --- |
| 静态检测器存在明显漏检 | SkillScan Static 对 53 个样本检出率为 0%，Cisco Static 总检出率 11%，SkillFortify 55% |
| LLM 检测器当前覆盖了已有 G1-G8 | Cisco Full 和 SkillScan GPT-5.4 对 53 个样本均为 100% 检出 |
| 继续研究重点应转向 LLM judge 或跨输入边界 | 现有字符、编码、语义、结构、代码简化、自动对抗和综合策略未绕过 LLM scanner |

因此，新实验不应重复 G1-G8 的表层改写，应优先攻击 LLM scanner 的输入组织、判据稳定性和跨文件推理边界。

## 3. 可复用文献方向

| 方向 | 代表工作 | 可迁移点 | 对本项目的意义 |
| --- | --- | --- | --- |
| LLM-as-a-judge prompt injection | `Investigating the Vulnerability of LLM-as-a-Judge Architectures to Prompt-Injection Attacks` | 将被评对象中的自然语言片段作为 judge 输入的一部分，观察 judge 是否被待评文本影响 | 对应 skill instruction 中的“评审语气、免责声明、合规叙述”是否影响 maliciousness judgment |
| LLM judge decision flip | `AdvJudge-Zero: Binary Decision Flips in LLM-as-a-Judge via Adversarial Control Tokens` | 研究二分类 judge 的稳定性、随机性和输入扰动敏感性 | 对应 malicious/benign 二分类 scanner 的阈值边界测试 |
| Judge backdoor | `BadJudge: Backdoor Vulnerabilities of LLM-as-a-Judge` | 评估 judge 对特定触发模式的偏置 | 可作为讨论项，不建议作为主实验，因为需要控制或污染 judge |
| LLM vulnerability detector black-box evasion | `Shield Broken: Black-box Adversarial Attacks on LLM-based Vulnerability Detectors` | label-only 查询、语义保持变换、搜索式组合扰动 | 将“vulnerable code”替换为“malicious skill artifact” |
| DL vulnerability detector evasion | `AdVulCode` | 变量名替换、无害语句插入、结构保持转换 | 可复用到脚本型 skill，但 4.6 已覆盖部分表层方法 |
| Adversarial code obfuscation | `Generating Adversarial Computer Programs using Optimized Obfuscations` | 多种语义保持 obfuscation 的组合搜索 | 适合作为 G8 的系统化升级，不应只人工枚举 |
| LLM code completion black-box attack | `INSEC: Black-Box Adversarial Attacks on LLM-Based Code Completion` | 通过上下文注释影响代码安全性判断或生成 | 可转化为“说明性注释影响 scanner 结论”的鲁棒性测试 |

参考链接：

- https://arxiv.org/abs/2505.13348
- https://arxiv.org/abs/2512.17375
- https://arxiv.org/abs/2503.00596
- https://ink.library.smu.edu.sg/sis_research/10815/
- https://www.mdpi.com/2079-9292/12/4/936
- https://arxiv.org/abs/2103.11882
- https://proceedings.mlr.press/v267/jenko25a.html
- https://github.com/eth-sri/insec

## 4. 候选攻击模式，抽象版

以下模式只作为评测假设。每个模式都应先用 toy sink、伪端点、伪凭据名和不可执行脚本验证 scanner 行为，再决定是否进入受控恶意样本库。

### M1. Judge 输入污染型 benign framing

核心假设：LLM scanner 将 skill 文档整体拼入 judge prompt 时，可能被被测文本中的“安全审计说明、合规声明、误报解释、测试免责声明”影响，降低恶意判断强度。

迁移方式：

| 项 | 设计 |
| --- | --- |
| 输入位置 | `SKILL.md` 顶部、usage section、limitations section |
| 保留标签 | 原 AP 恶意语义标签不变 |
| 变换强度 | 仅增加审计式自然语言框架，不改变代码行为 |
| 预期风险 | LLM scanner 可能将声明当作证据，忽略跨文件行为 |
| 验证指标 | Cisco Full 与 SkillScan GPT-5.4 是否出现 severity 降低、uncertain 或 benign |

### M2. 跨文件语义稀释

核心假设：LLM scanner 对单个文件很强，但对“文件 A 只声明数据处理，文件 B 只定义通用工具，文件 C 只配置触发条件”的组合语义可能推理不足。

迁移方式：

| 项 | 设计 |
| --- | --- |
| 输入位置 | `SKILL.md`、辅助脚本、配置文件、模板文件 |
| 保留标签 | 用抽象 sink 表示最终敏感数据流，不写真实外传 |
| 变换强度 | 每个文件单独看都接近 benign，组合图上才形成违规数据流 |
| 预期风险 | scanner 若只摘要文件或截断上下文，可能漏掉跨文件 taint path |
| 验证指标 | 检测报告是否指出完整 source-to-sink 链路 |

### M3. 多 skill 组合型 latent capability

核心假设：单个 skill 只暴露 benign 子能力，多个 skill 连续执行后形成高风险能力。若 scanner 的输入边界是单 skill，则天然难以覆盖组合风险。

迁移方式：

| 项 | 设计 |
| --- | --- |
| 输入位置 | 2 到 3 个独立 skill |
| 保留标签 | 组合级标签为 malicious，单 skill 标签记录为 dual-use 或 benign-looking |
| 变换强度 | 不在单个 skill 中出现完整攻击链 |
| 预期风险 | 单 skill scanner 无法建模 agent workflow |
| 验证指标 | 单独扫描与组合扫描的结论差异 |

### M4. 外部输入间接指令型

核心假设：skill 本身只实现读取外部内容和执行结构化任务，风险指令来自邮件、issue、网页、文档等外部输入。检测器若只看 skill artifact，可能无法判断 runtime prompt injection 风险。

迁移方式：

| 项 | 设计 |
| --- | --- |
| 输入位置 | skill 描述、输入 schema、示例数据 |
| 保留标签 | 使用无害模拟外部输入，不接入真实账户或真实邮件 |
| 变换强度 | skill artifact 不含显式恶意 payload |
| 预期风险 | artifact scanner 对 runtime data boundary 建模不足 |
| 验证指标 | scanner 是否要求隔离外部指令、最小权限和用户确认 |

### M5. 经济型和资源型攻击再建模

核心假设：AP10 的 token 消耗已被 LLM scanner 检出，但如果资源消耗被包装为质量保证、重试、校验或一致性投票流程，scanner 可能难以量化成本风险。

迁移方式：

| 项 | 设计 |
| --- | --- |
| 输入位置 | workflow section、validation section、循环控制配置 |
| 保留标签 | 只使用有限轮数 toy workflow，避免真实资源消耗 |
| 变换强度 | 将显式无限循环改为条件式重复、投票式重复、质量阈值重复 |
| 预期风险 | scanner 能识别无限循环，但可能漏掉高成本有限循环 |
| 验证指标 | 报告是否给出 token/cost 上界分析 |

### M6. Policy gap 型工具权限错配

核心假设：skill 描述的业务目标 benign，但要求的工具权限超出必要范围。若 scanner 只看恶意代码或关键词，可能漏掉权限最小化问题。

迁移方式：

| 项 | 设计 |
| --- | --- |
| 输入位置 | manifest、tool permission、setup instructions |
| 保留标签 | 不写真实滥用逻辑，只声明过宽权限需求 |
| 变换强度 | 让权限与功能需求出现可审计的不匹配 |
| 预期风险 | 检测器缺少权限需求和功能需求的一致性校验 |
| 验证指标 | 报告是否指出 permission overreach |

## 5. 实验设计

### 5.1 样本分层

| 层级 | 样本 | 数量建议 | 目的 |
| --- | --- | ---: | --- |
| Baseline | 4.6 中 AP01-AP12 orig 和 G1-G8 | 既有 65 个左右 | 复核旧结果 |
| Toy-safe | M1-M6 抽象样本，每类 2 个 | 12 个 | 验证 scanner 是否覆盖模式 |
| Controlled-malicious | 仅在审批后从 AP 样本迁移 | 每类 1 到 2 个 | 验证真实恶意语义保留后的检出率 |
| Benign-control | 与 M1-M6 结构相似但无风险链路 | 每类 1 个 | 控制误报 |

### 5.2 评测矩阵

| Scanner | 必跑 | 目标 |
| --- | :---: | --- |
| Cisco Static | 是 | 观察关键词和文件级规则 |
| SkillFortify | 是 | 观察声明-行为一致性、跨文件能力 |
| SkillScan Static | 是 | 维持历史可比性 |
| Cisco Full | 是 | 重点观察 LLM judge 是否被框架或上下文影响 |
| SkillScan GPT-5.4 | 是 | 重点观察另一个 LLM scanner 的一致性 |
| DeepSeek 结果链路 | 可选 | 与 4.6/deepseek_eval_report.md 对齐 |

### 5.3 成功标准

不要只看最终 label。每个样本记录以下指标：

| 指标 | 说明 |
| --- | --- |
| label | detected、missed、uncertain |
| severity | 若 scanner 提供等级，记录等级变化 |
| rationale coverage | 报告是否提到真实风险链路 |
| source-to-sink coverage | 报告是否完整连接 source、transform、sink |
| boundary coverage | 报告是否识别外部输入、多 skill、权限和资源边界 |
| false positive control | benign-control 是否被误报 |

## 6. 建议优先级

| 优先级 | 模式 | 原因 |
| --- | --- | --- |
| P0 | M2 跨文件语义稀释 | 4.6 已显示 AP08 和多文件载体是静态工具弱点，LLM scanner 的下一步压力测试应从这里开始 |
| P0 | M3 多 skill 组合型 latent capability | 会议纪要明确提出，且单 skill scanner 很可能缺少组合输入 |
| P1 | M4 外部输入间接指令型 | 与 agent runtime 安全高度相关，artifact-only scanner 可能覆盖不足 |
| P1 | M6 Policy gap 型工具权限错配 | 易构造 benign-control，适合快速验证检测器是否检查权限最小化 |
| P2 | M1 Judge 输入污染型 benign framing | 与 LLM judge 欺骗最贴近，但容易滑向 prompt injection，需要严格使用安全抽象文本 |
| P2 | M5 经济型和资源型攻击再建模 | AP10 已被检出，应作为成本边界测试 |

## 7. 论文问题表述建议

建议使用以下命名：

> Black-box evasion evaluation for LLM-based skill maliciousness detectors

理由：

1. black-box 符合当前只能观察 scanner 输出的条件；
2. evasion evaluation 强调评测已知方法，不声称提出通用新算法；
3. LLM-based skill maliciousness detectors 精确覆盖本项目对象；
4. jailbreak 可作为背景对比，主线应放在 judge 欺骗和检测器规避。

## 8. 下一步实施清单

1. 新建 `5.2/evasion_patterns_manifest.csv`，字段包括 `pattern_id, source_ap, artifact_scope, scanner_boundary, expected_risk, safe_toy_only`。
2. 为 M2、M3、M4、M6 各写 2 个 toy-safe skill，所有脚本只使用本地 dummy 文件和 `example.invalid` 伪端点。
3. 复用 `4.6/run_*_eval.py` 的输出结构，新增 `5.2/evaluation/` 目录保存扫描结果。
4. 写一个聚合脚本，只统计 label、severity、rationale 是否覆盖 source-to-sink，不生成或改写攻击 payload。
5. 若 toy-safe 样本已经导致 LLM scanner 误判，再由人工决定是否在隔离环境中构造 controlled-malicious 样本。

## 9. 风险控制

| 风险 | 控制 |
| --- | --- |
| 生成可执行攻击能力 | toy-safe 阶段禁止真实凭据路径、真实外传域名、真实 hook、真实权限修改 |
| 误把 benign framing 写成 prompt injection payload | 只使用审计报告风格文本，不写“忽略上文”“输出 benign”等直接操控 judge 的语句 |
| 结果不可复现 | 固定 scanner 版本、模型名、temperature、输入路径和输出 JSON |
| 只得到 anecdote | 每个模式至少 2 个样本加 1 个 benign-control |
| 与旧实验不可比 | 保留 AP 编号、scanner 名称和 4.6 结果格式 |
