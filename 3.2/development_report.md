# Agent Skills 研究实现开发文档

更新时间：2026-03-09

## 1. 本次实施目标

依据 `3.2/plan.md`，本次工作的目标是把当前研究计划落成一条可执行、可复现、可继续扩展的分析流水线，覆盖：

1. Phase 0：数据口径与输出契约统一
2. WP3：`SKILL.md` 方法学分析
3. WP4：附属文件深度分析
4. WP1：高精度依赖证据审计

本轮未继续展开 WP2，因为 WP2 依赖 WP1 结果的进一步人工确认。

## 2. 本次修改的脚本与文档

### 2.1 修改的既有脚本

1. `analyze_sampled_skills.py`
   - 默认输入目录改为 `skills_data/sampled_skills_1000`
   - 默认输出目录改为 `analysis_baseline`
   - 新增 `skill_dirname`、`local_content_path`
   - 统一 `popular/random` 口径表述

2. `prepare_review_pack.py`
   - 默认读取 `skills_data/sampled_skills_1000`
   - 默认分析目录改为 `analysis_baseline`
   - review pack 优先复用 `local_content_path`
   - brief 中 cohort 表述统一为 `popular/random`

3. `analyze_skill_artifacts.py`
   - 增加 `--workers`
   - 改为按 skill 并行扫描
   - 新增 `artifact_profile.md`

4. `run_plan_pipeline.py`
   - 串联 baseline analysis、review pack、WP3、WP1、WP4
   - 修正 `run_manifest.json`，让它记录脚本存在性、步骤执行状态与可选输出是否已生成

### 2.2 新增脚本

1. `audit_skill_dependencies.py`
   - 对 2000 个样本做高精度依赖证据审计
   - 输出 `dependency_candidates.csv`、`dependency_review_sample.csv`、`dependency_audit.md`
   - 支持 `--workers`

2. `analyze_skillmd_method.py`
   - 负责 WP3 的 `SKILL.md` 方法学产物
   - 输出 `structuredness_score.csv`、`manual_labels.csv`、`method_results_skillmd.md`
   - 支持 `--workers`

### 2.3 新增文档

1. `3.2/annotation_schema.md`
   - 定义 WP3 pilot 的 codebook、字段规则与 structuredness score 映射

2. `3.2/data_protocol.md`
   - 记录样本范围、输入输出契约与 pipeline 顺序

3. `3.2/analysis_baseline.md`
   - 汇总 baseline 输出状态

4. `3.2/run_manifest.json`
   - 记录本轮执行的真实输入、脚本、状态和产物

## 3. 本次生成的核心产物

主输出目录：`skills_data/sampled_skills_1000/analysis_baseline`

### 3.1 Phase 0 / baseline

1. `features_all.csv`
2. `summary_metrics.json`
3. `taxonomy_distribution.csv`
4. `manual_review_candidates.csv`
5. `manual_review_template.csv`
6. `empirical_brief.md`

### 3.2 WP3：`SKILL.md` 方法学

1. `skillmd_pilot_sample.csv`
2. `manual_labels.csv`
3. `structuredness_score.csv`
4. `method_results_skillmd.md`

关键结果：

1. 全量 `structuredness_score.csv`：2000 行
2. manual pilot：12 条
3. blind dual coding 的 kappa：
   - `has_trigger_condition = 1.000`
   - `has_constraints = 1.000`
   - `has_error_fallback = 1.000`
   - `has_io_spec = 1.000`
   - `example_quality = 1.000`
   - `has_stepwise_procedure = 0.636`
   - `spec_form = 0.727`
4. 自动 structuredness：
   - `popular mean = 65.57`
   - `random mean = 57.94`

### 3.3 WP4：附属文件深度分析

1. `script_ops.csv`
2. `example_stats.csv`
3. `data_asset_stats.csv`
4. `artifact_profile.md`

关键结果：

1. `script_ops.csv`：1200 行
2. `example_stats.csv`：2000 行
3. `data_asset_stats.csv`：2000 行
4. cohort 摘要：
   - `popular`：152 个 skills 含脚本，23 个 skills 含 example files，39 个 skills 含 data assets
   - `random`：168 个 skills 含脚本，29 个 skills 含 example files，62 个 skills 含 data assets

### 3.4 WP1：依赖证据审计

1. `dependency_candidates.csv`
2. `dependency_review_sample.csv`
3. `dependency_audit.md`

关键结果：

1. `dependency_candidates.csv`：539 行
2. `dependency_review_sample.csv`：86 行
3. evidence type 分布：
   - `skill_path_reference = 309`
   - `explicit_skill_reference = 139`
   - `relative_skill_link = 71`
   - `workflow_invocation = 20`
4. resolution 分布：
   - `same_repo_unique = 33`
   - `global_unique = 40`
   - `ambiguous = 53`
   - `unresolved = 413`

## 4. 人工标注的实现方式

`plan.md` 中的“人工”本轮解释为“主 agent + 子 agent”。

本次 WP3 pilot 使用了多 agent blind dual coding：

1. 两个子 agent 独立阅读同一批 12 个 `SKILL.md`
2. 两边分别返回结构化标签
3. 主 agent 仅对冲突字段做 adjudication
4. 最终写入正式 `manual_labels.csv`

本次实际 adjudication 的冲突字段共 4 处，主要集中在：

1. `spec_form`
2. `has_stepwise_procedure`

这也与最终 kappa 结果一致。

## 5. 并行化实现

你提到的“多线程并行文件扫描”已经落实。

本轮支持并行的脚本：

1. `audit_skill_dependencies.py`
2. `analyze_skill_artifacts.py`
3. `analyze_skillmd_method.py`

实现方式：

1. 以 skill 为粒度拆任务
2. 使用 `ThreadPoolExecutor`
3. 默认 `workers = min(8, cpu_count())`

这样做的原因是：

1. 读取大量小文件时，I/O 并行比串行更合适
2. 不会改变每个 skill 内部的分析逻辑
3. 结果仍可排序回稳定输出

## 6. 本次验证

### 6.1 语法与 smoke test

已通过：

1. `python3 -m py_compile`
2. `audit_skill_dependencies.py` smoke test
3. `analyze_skill_artifacts.py` smoke test
4. `analyze_skillmd_method.py` smoke test

### 6.2 全量重跑

已完成全量执行命令：

```bash
python3 /Users/tan/Desktop/RA3/run_plan_pipeline.py \
  --sample-dir /Users/tan/Desktop/RA3/skills_data/sampled_skills_1000 \
  --output-dir /Users/tan/Desktop/RA3/skills_data/sampled_skills_1000/analysis_baseline \
  --docs-dir /Users/tan/Desktop/RA3/3.2
```

全量执行完成后：

1. `run_manifest.json` 已正确记录 WP1/WP3/WP4 为已执行
2. `analysis_baseline.md` 已正确记录所有可选产物为 `present`

## 7. 当前限制

1. WP1 目前还是“证据审计”，不是最终确认后的依赖图
2. `dependency_candidates.csv` 中 `unresolved` 较多，说明 target normalization 仍有改进空间
3. WP3 的 manual pilot 规模目前是 12，足够起步，但还不是最终论文级标注规模
4. WP2 尚未展开，仍需基于 `dependency_review_sample.csv` 做进一步确认

## 8. 推荐下一步

如果继续按 `plan.md` 推进，建议顺序如下：

1. 基于 `dependency_review_sample.csv` 做一轮依赖真伪确认
2. 如果 WP1 precision 达标，再进入 WP2 的 mechanism / risk propagation
3. 扩大 WP3 manual pilot 样本，提升对 `spec_form` 和 `stepwise` 的稳定性
4. 基于 `structuredness_score.csv`、`script_ops.csv`、`data_asset_stats.csv` 做联合分析与图表输出
