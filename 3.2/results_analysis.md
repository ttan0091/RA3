# Agent Skills 结果分析文档

更新时间：2026-03-09

## 1. 分析范围

本文档基于当前已经生成的研究产物做一轮中文结果分析，主要使用：

1. `skills_data/sampled_skills_1000/analysis_baseline/comparison_summary.md`
2. `skills_data/sampled_skills_1000/analysis_baseline/empirical_brief.md`
3. `skills_data/sampled_skills_1000/analysis_baseline/method_results_skillmd.md`
4. `skills_data/sampled_skills_1000/analysis_baseline/artifact_profile.md`
5. `skills_data/sampled_skills_1000/analysis_baseline/dependency_audit.md`
6. `structuredness_score.csv`、`script_ops.csv`、`example_stats.csv`、`data_asset_stats.csv` 的联合派生统计

本文档只做描述性和解释性分析，不做因果结论。

## 2. 总体结论

基于当前 `popular 1000` 与 `random 1000` 的对比，可以先得到 4 个较稳的判断：

1. `popular` skills 在 `SKILL.md` 层面的结构化表达更强，文本更长、模板化更明显、内嵌示例也更丰富。
2. `random` skills 在仓库文件层面更“厚”，更常带脚本、配置、数据资产，并且脚本里出现网络访问、凭据访问的比例更高。
3. skill-to-skill 依赖证据确实存在，但当前生态的显式依赖仍然偏稀疏、偏不标准化，大量候选边无法可靠解析。
4. “高结构化”不等于“低风险”。在两个 cohort 中，都能看到高结构化且带有网络/凭据/删除能力的 skills，尤其 `random` 更明显。

如果把这轮结果压缩成一句话，可以表述为：

`popular` 更像“把能力压缩进单个高结构化说明文档”，`random` 更像“把能力散布在脚本、配置和附属文件里”。

## 3. Baseline 对比

从 baseline 结果看，`popular` 与 `random` 的差异首先体现在文档组织方式，而不是简单的“复杂度越高越流行”。

### 3.1 `popular` 更偏向文档中心化

关键现象：

1. 平均 `SKILL.md` 词数：`popular 1105.2`，`random 833.0`
2. template presence：`popular 40.6%`，`random 11.6%`
3. docs-folder presence：`popular 24.4%`，`random 18.9%`

这说明 `popular` 的一个明显特点是：能力说明更容易被组织成模板化、文档化、可复用的规范文本。

### 3.2 `random` 更偏向仓库原生结构

关键现象：

1. 平均文件数：`popular 5.29`，`random 9.93`
2. script presence：`popular 15.2%`，`random 16.8%`
3. config files：`popular 4.5%`，`random 13.4%`

这说明 `random` skills 更经常以“一个小型项目目录”而不是“一个高压缩的说明文档”形式出现。

### 3.3 一个必须保留的解释限制

`popular` cohort 有明显集中度偏差：

1. unique repos：`popular 79`，`random 806`
2. `popular` 最大 repo 占比：`davila7/claude-code-templates = 37.4%`

因此，`popular` 与 `random` 的差异里，有一部分很可能是“头部仓库风格差异”，而不全是“流行 skill 的共性”。

## 4. WP3：`SKILL.md` 方法学结果

WP3 的结果相对最稳定，因为它同时有全量自动分数，也有一轮小规模 blind dual coding。

### 4.1 结构化程度差异是目前最清楚的发现

`structuredness_score.csv` 的结果：

1. `popular mean = 65.57`
2. `random mean = 57.94`
3. `popular median = 68`
4. `random median = 60`

这说明在当前样本中，`popular` 的确更常出现明确触发条件、约束语句、流程组织和示例组织。

### 4.2 自动 spec form 的差异

自动 spec form 分布显示：

1. `popular` 里 `mixed` 占比更高：`596`
2. `random` 里 `structured_template` 稍更多：`483`
3. `natural_language` 在 `random` 中更多：`52`，`popular` 为 `25`

一种合理解释是：

1. `popular` 更常把 prose、模板、命令、代码块混合进同一个 `SKILL.md`
2. `random` 更常落在“简单模板”或“偏自然语言说明”的两端

### 4.3 Pilot 标注说明这套方法可以继续扩展

pilot 结果：

1. 双标样本：12 条
2. `has_trigger_condition / has_constraints / has_error_fallback / has_io_spec / example_quality` 的 kappa 都是 `1.000`
3. `has_stepwise_procedure = 0.636`
4. `spec_form = 0.727`

这意味着：

1. “触发、约束、I/O、错误处理、示例”这些字段已经足够稳定，可以继续扩大标注
2. 最容易产生歧义的是“是不是 stepwise”和“主要 spec form 算哪一种”

换句话说，WP3 现在已经不是“想法”，而是一个可继续扩张的标注框架。

## 5. WP4：附属文件深度分析结果

WP4 的结果揭示了一个很重要的结构性差异：`random` 更像“能执行的小仓库”，`popular` 更像“文档驱动的技能包”。

### 5.1 脚本能力差异

在含脚本的 skills 内部，`random` 的敏感操作比例更高：

1. `op_network`：`popular 7.2%`，`random 20.8%`
2. `op_credentials_access`：`popular 17.1%`，`random 29.2%`
3. `op_read`：`popular 52.6%`，`random 60.1%`

`popular` 虽然也大量执行外部命令与写文件，但 `random` 更常把网络与凭据访问直接落到脚本里。

### 5.2 示例组织差异

`popular` 的内嵌示例更丰富：

1. embedded example mentions：`popular 3.09`，`random 2.63`
2. embedded code fences：`popular 9.74`，`random 7.76`

但独立 `example files` 的数量差异不大：

1. `popular` skills with example files：`23`
2. `random` skills with example files：`29`

这说明 `popular` 更倾向于把示例直接塞进 `SKILL.md`，而不是拆成仓库中的独立示例资产。

### 5.3 数据资产差异

`random` 的数据资产更重：

1. has data assets：`popular 39`，`random 62`
2. avg data files：`popular 0.11`，`random 0.19`
3. avg data bytes：`popular 3898.2`，`random 6242.5`

同时，两组里都几乎没有真正值得单列的数据库文件，说明会议纪要中的“数据库分析”改写成“数据资产分析”是正确的。

## 6. WP1：依赖证据审计结果

WP1 的结论不是“依赖很多”，而是“依赖有，但显式化和标准化程度有限”。

### 6.1 依赖证据存在，但规模不算大

在 2000 个 skills 上，当前规则只抽到了 `539` 条候选证据。

其中：

1. `skill_path_reference = 309`
2. `explicit_skill_reference = 139`
3. `relative_skill_link = 71`
4. `workflow_invocation = 20`

这意味着现阶段最常见的依赖证据不是“稳定的调用协议”，而是路径引用和文本提及。

### 6.2 当前最大问题是解析率

resolution 分布：

1. `unresolved = 413`
2. `ambiguous = 53`
3. `same_repo_unique = 33`
4. `global_unique = 40`

也就是说，当前候选边里只有一小部分能被高置信度解析到具体 target skill。

这支持一个比较稳的判断：

当前 skill 生态里，cross-skill 依赖不是完全不存在，而是缺少统一命名、统一引用方式和统一声明格式。

### 6.3 `popular` 的解析率略高

按 cohort 粗看：

1. `popular` candidate rows：`230`，高置信解析率约 `16.5%`
2. `random` candidate rows：`309`，高置信解析率约 `11.3%`

这可能意味着 `popular` 里的依赖表述略更规范，或者更集中于少数风格一致的仓库。

## 7. WP3 与 WP4 的联合分析

把 `structuredness_score.csv` 与 `script_ops.csv / example_stats.csv / data_asset_stats.csv` 联合后，可以得到几个比单文件更有意思的结果。

### 7.1 高结构化通常伴随更丰富的示例

在两个 cohort 里，高 structuredness 组都有：

1. 更高的 embedded example mentions
2. 更多 code fences
3. 更高的数据资产量

例如：

1. `popular` 高结构化组的平均 embedded code fences 是 `14.16`，低结构化组是 `4.62`
2. `random` 高结构化组的平均 embedded code fences 是 `14.61`，低结构化组是 `4.22`

这说明 structuredness 不只是“语气更像规范”，而是和示例密度、材料丰富度一起出现的。

### 7.2 高结构化不等于低风险

定义“高结构化且存在敏感脚本风险”为：

1. structuredness `>= 80`
2. 且脚本中出现 `network / credentials_access / delete` 之一

结果：

1. `popular` 高结构化组中，这类 skill 有 `18` 个，占高结构化组的 `5.9%`
2. `random` 高结构化组中，这类 skill 有 `23` 个，占高结构化组的 `11.3%`

这说明一个值得继续挖掘的点：

结构化表达有时不是在“降低操作性”，而是在“更清楚地包装高操作性能力”。

### 7.3 `random` 的高结构化技能更值得警惕

`random` 不仅总体上更常带网络/凭据脚本，在高结构化组里这一倾向更明显。  
换句话说，`random` 里并不是“粗糙技能才危险”，相反，一部分最结构化、最像成熟说明书的技能，同样可能带有更高的执行风险。

## 8. 当前最值得保留的解释框架

基于现有结果，我认为目前最合适的论文式表述不是：

1. `popular skill 更好`
2. `结构化导致流行`
3. `依赖导致漏洞传导`

而是以下 3 句：

1. `popular` 与 `random` 在技能封装方式上存在稳定差异：前者更偏文档中心化，后者更偏仓库原生化。
2. skill-to-skill 依赖证据在样本中可见，但显式度与标准化程度有限，当前更像“弱依赖生态”而非“成熟依赖网络”。
3. 高结构化技能并不天然更安全，尤其在 `random` cohort 中，高结构化与高操作性能力可以同时出现。

## 9. 局限与下一步

### 9.1 当前局限

1. WP3 的 manual pilot 只有 12 条，足以校准框架，但不足以做强结论
2. WP1 当前还是候选边审计，不是人工确认后的依赖网络
3. `popular` cohort 的仓库集中度很高，风格偏差不能忽略
4. WP4 的风险识别仍是规则级，不是语义级行为理解

### 9.2 推荐下一步

1. 继续人工确认 `dependency_review_sample.csv`，决定是否启动 WP2
2. 扩大 WP3 pilot，优先提高 `spec_form` 和 `stepwise` 的稳定性
3. 基于联合结果，专门筛一批“高结构化-高风险”样本做 case study
4. 把本轮结果转成图表版本，形成论文 Results 章节的骨架
