# 5.2 — Skill Maliciousness Detector Evasion (实施)

研究计划见 [detector_evasion_research_plan_v3_easy.md](detector_evasion_research_plan_v3_easy.md)。

## 目录布局

```
5.2/
├── benchmark/
│   ├── L0_baseline/{malicious,benign}/   # 24 + 10 baseline cases
│   ├── L1_single/                        # 12 attacks × 4 APs evasion samples
│   └── manifest.yaml                     # ground truth (3.24 manifest copy)
├── scanners/
│   ├── cisco/                            # Cisco skill-scanner (本地副本)
│   ├── skillfortify/                     # SkillFortify (本地副本)
│   └── skillscan/                        # MaliciousAgentSkillsBench (本地副本)
├── scripts/
│   ├── common/
│   │   ├── deepseek.py                   # 共享 DeepSeek client
│   │   ├── skill_io.py                   # 读取 skill 为 LLM input
│   │   ├── cisco_threat_prompt.md        # Cisco LLM judge prompt
│   │   ├── cisco_protection_prompt.md
│   │   └── skillscan_audit_prompt.txt    # SkillScan LLM judge prompt
│   ├── runners/                          # 5 个 scanner runner
│   │   ├── run_cisco_static.py           # static-only Cisco
│   │   ├── run_cisco_full.py             # static + DeepSeek LLM judge
│   │   ├── run_skillfortify.py
│   │   ├── run_skillscan_static.py
│   │   ├── run_skillscan_llm.py          # DeepSeek LLM judge (SkillScan prompt)
│   │   ├── run_all.py                    # 一键跑全部 5 scanner
│   │   └── run_l1.py                     # 跑 L1 evasion samples
│   ├── attacks/                          # 12 个攻击实现
│   │   ├── _helpers.py                   # benign_score / 语义判定 / 路径
│   │   ├── A2_advjudge.py                # AdvJudge-Zero 候选短语搜索
│   │   ├── A3_paraphrase.py              # Adversarial Paraphrasing
│   │   ├── A4_pair.py                    # PAIR 迭代 (默认未跑)
│   │   ├── A5_insec.py                   # INSEC 注释注入
│   │   ├── A6_svulattack.py              # 行重要性 + 重写
│   │   ├── A7_simplify.py                # 反复杂度变换
│   │   ├── A8_transforms.py              # 7 种代码变换
│   │   ├── A9_mcts.py                    # A8 变换的随机搜索
│   │   ├── A10_crossfile.py              # 跨文件稀释
│   │   ├── A12_permgap.py                # 权限超配
│   │   └── run_serial.py                 # 串行批跑
│   ├── aggregate.py                      # 单一 evaluation 目录的矩阵
│   └── build_final_report.py             # baseline + L1 综合报告
├── evaluation/                           # scanner 输出 JSON
│   ├── L0_baseline_malicious/{cisco_static,cisco_full,skillfortify,skillscan_static,skillscan_llm}/
│   ├── L0_baseline_benign/...
│   └── L1_single/...
└── reports/
    ├── L0_baseline_malicious.{md,csv}
    ├── L0_baseline_benign.{md,csv}
    ├── L1_single.{md,csv}
    └── L1_final.{md,csv}                 # 主结果
```

## 模型策略（DeepSeek）

| 角色 | 模型 | 备注 |
|---|---|---|
| Judge / detector | `deepseek-v4-flash` | 快、便宜；export `DS_JUDGE_MODEL=deepseek-v4-pro` 可换强模型 |
| Attacker / paraphraser | `deepseek-v4-flash` | 同上 |

所有 LLM 调用走 `scripts/common/deepseek.py`。`v4-pro` 是推理模型，单次 4–10 分钟；`v4-flash` 单次 ≈ 25 秒。

## 跑起来的命令

### L0 baseline

```bash
python3 scripts/runners/run_all.py benchmark/L0_baseline/malicious evaluation/L0_baseline_malicious
python3 scripts/runners/run_all.py benchmark/L0_baseline/benign  evaluation/L0_baseline_benign
python3 scripts/aggregate.py evaluation/L0_baseline_malicious --out reports/L0_baseline_malicious.md
python3 scripts/aggregate.py evaluation/L0_baseline_benign  --out reports/L0_baseline_benign.md
```

### L1 攻击（生成新 evasion 样本）

```bash
# 串行跑全部攻击（A2 -> A3 -> A5 -> A6 -> A9，每个独立子进程，避免并发触发限流）
python3 scripts/attacks/run_serial.py
# 或逐个跑：
python3 scripts/attacks/A2_advjudge.py
python3 scripts/attacks/A3_paraphrase.py
# ... 等等
```

每个攻击会在 `benchmark/L1_single/<AP>_<aid>/` 下生成 SKILL.md（必要时还有附加文件）+ `attack.json`（含每轮迭代日志和 LLM 给的 semantic_preservation 评判）。

### 扫所有 L1 样本

```bash
python3 scripts/runners/run_l1.py
python3 scripts/aggregate.py evaluation/L1_single --out reports/L1_single.md
python3 scripts/build_final_report.py
```

## 关键文件清单（最重要的几个）

- [scripts/common/deepseek.py](scripts/common/deepseek.py) — 全部 LLM 调用集中处
- [scripts/runners/run_all.py](scripts/runners/run_all.py) — 5 scanner 一键跑
- [scripts/attacks/_helpers.py](scripts/attacks/_helpers.py) — `benign_score()` / `judge_semantic_preservation()`
- [scripts/build_final_report.py](scripts/build_final_report.py) — 最终矩阵与攻击成功率表

## 已知 quirks

- **Cisco scanner pyproject.toml**：把 `dynamic = ["version"]` 换成了 `version = "0.0.0+local"`，移除了 hatch-vcs 块，这样 `uv sync` 可以无 git 仓库地构建。
- **SkillScan Static** 对 benign 也会高频报警（4.6 报告也观察到，是规则过于宽松）。
- **DeepSeek v4-flash** 是推理模型，`max_tokens` 必须 ≥ 几百，否则全部 token 用在 reasoning 上、output 为空。
