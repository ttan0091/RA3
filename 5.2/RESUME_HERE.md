# 5.2 实施进度 — 续作指南（2026-05-03 暂停）

## 当前状态

### ✅ 已完成
1. **5.2 目录结构搭好**：`benchmark/`、`scanners/`、`scripts/{common,runners,attacks}/`、`evaluation/`、`reports/`
2. **3 个 scanner 源码已复制到 `5.2/scanners/`**（Cisco、SkillFortify、SkillScan），各自的 venv 已 `uv sync`，确认本地可跑
3. **5 个 scanner runner 已写完并通过 sanity 测试**
   - `scripts/runners/run_cisco_static.py`
   - `scripts/runners/run_cisco_full.py` (DeepSeek v4-flash 作 judge)
   - `scripts/runners/run_skillfortify.py`
   - `scripts/runners/run_skillscan_static.py`
   - `scripts/runners/run_skillscan_llm.py` (DeepSeek v4-flash 作 judge)
   - `scripts/runners/run_all.py` 一次跑全部 5 个
4. **共享 DeepSeek 客户端** `scripts/common/deepseek.py` — 默认 `JUDGE_MODEL=deepseek-v4-flash`，`ATTACKER_MODEL=deepseek-v4-flash`（覆盖：export DS_JUDGE_MODEL=deepseek-v4-pro）
5. **9 个攻击实现已写完**（待跑）：
   - `scripts/attacks/A2_advjudge.py` — AdvJudge-Zero 候选短语搜索
   - `scripts/attacks/A3_paraphrase.py` — Adversarial Paraphrasing
   - `scripts/attacks/A4_pair.py` — PAIR 迭代攻击
   - `scripts/attacks/A5_insec.py` — INSEC 注释注入
   - `scripts/attacks/A6_svulattack.py` — Statement importance + 重写
   - `scripts/attacks/A7_simplify.py` — 反复杂度变换
   - `scripts/attacks/A8_transforms.py` — 7 种代码变换
   - `scripts/attacks/A9_mcts.py` — A8 变换的随机搜索
   - `scripts/attacks/A10_crossfile.py` — 跨文件 source-to-sink 稀释
   - `scripts/attacks/A12_permgap.py` — 权限超配
6. **L0 baseline 部分跑了**：
   - cisco_static: 24/24 ✅
   - skillfortify: 24/24 ✅
   - skillscan_static: 24/24 ✅
   - cisco_full: 8/24（中断）
   - skillscan_llm: 0/24（未开始）

### ⏸ 待办
1. **续跑 L0 baseline malicious**：cisco_full 还差 16 个，skillscan_llm 全部
2. **跑 L0 baseline benign**：10 个 BENxx × 5 scanner（用于 FPR）
3. **L1 攻击实验**：12 个攻击 × 4 个 AP（默认 AP01/05/07/08）= 48 样本
4. **L1 样本扫描**：48 个新样本 × 5 scanner = 240 次 scan
5. **A11 多 skill 攻击**（人工设计 3 套）— 还没写，等明天讨论
6. **聚合脚本** `scripts/aggregate.py`（出 4.6 风格的最终矩阵）— 还没写
7. **最终报告** `reports/L0_baseline.md` 与 `reports/L1_evasion.md`

## 明天恢复时的操作

### 续跑 L0 baseline（runner 自带 skip-if-exists，直接重跑即可）

```bash
cd /Users/tan/Desktop/RA3/5.2
# 续跑 cisco_full + skillscan_llm（已完成的会自动 skip）
python3 scripts/runners/run_cisco_full.py benchmark/L0_baseline/malicious evaluation/L0_baseline_malicious/cisco_full evaluation/L0_baseline_malicious/cisco_static
python3 scripts/runners/run_skillscan_llm.py benchmark/L0_baseline/malicious evaluation/L0_baseline_malicious/skillscan_llm

# 跑 benign baseline
python3 scripts/runners/run_all.py benchmark/L0_baseline/benign evaluation/L0_baseline_benign
```

### 跑 L1 攻击（每个攻击约 5–20 分钟，看 query 数）

```bash
cd /Users/tan/Desktop/RA3/5.2
python3 scripts/attacks/A2_advjudge.py
python3 scripts/attacks/A3_paraphrase.py
python3 scripts/attacks/A4_pair.py
python3 scripts/attacks/A5_insec.py
python3 scripts/attacks/A6_svulattack.py
python3 scripts/attacks/A7_simplify.py     # 不调 LLM，秒完
python3 scripts/attacks/A8_transforms.py   # 不调 LLM，秒完
python3 scripts/attacks/A9_mcts.py
python3 scripts/attacks/A10_crossfile.py
python3 scripts/attacks/A12_permgap.py
```

每个攻击会在 `benchmark/L1_single/<AP>_<aid>/` 下生成新的 skill 和 `attack.json`（含每轮迭代日志和 semantic_preservation 评判）。

### 跑 L1 scanner 矩阵

```bash
python3 scripts/runners/run_all.py benchmark/L1_single evaluation/L1_single
```

## 模型策略（DeepSeek）

- **Judge / detector**：`deepseek-v4-flash`（默认）— 快，成本低；如要做高保真复检改 `DS_JUDGE_MODEL=deepseek-v4-pro` 单独跑一遍。
- **Attacker / paraphraser / generator**：`deepseek-v4-flash`（默认）。
- 全部走 `scripts/common/deepseek.py`，没有任何代码硬编码模型名。

## 成本估算（剩余）

| 任务 | LLM 调用次数 | 备注 |
|---|---|---|
| L0 续跑（16 cisco_full + 24 skillscan_llm + 10 benign × 2 LLM） | ≈ 60 | |
| L1 攻击的 detector queries | ≈ 600（A2 ×13、A3 ×9、A4 ×11、A5 ×11、A6 ×30、A9 ×13，每攻击 4 个 AP） | |
| L1 攻击的 attacker queries | ≈ 100 | A3/A4/A6 |
| L1 样本扫描 | ≈ 96（48 sample × 2 LLM scanner） | |
| 语义保留判定 | ≈ 40 | 每个攻击样本 1 次 |
| **合计** | **≈ 900 调用** | v4-flash 平均每调 ~$0.005，总计 ~$5 |

## 已知 quirks

1. **SkillScan Static 对 benign 也会报 HIGH**（BEN01 在 sanity 时 issues=4 detected=True）— 与 4.6 报告一致，是 SkillScan Static 的固有问题。
2. **Cisco scanner 的 pyproject.toml** 改了 version 行（`dynamic` → `0.0.0+local`）和删掉了 hatch-vcs 段，让 `uv sync` 能跑。
3. **DeepSeek v4-pro 太慢**（推理模型，每次 4–10 分钟）— 默认改用 v4-flash，快约 10×。

## 还没写的东西（明天讨论后再写）

- A1 (JudgeDeceiver) — 需要本地 GPU，暂缓
- A11 (多 skill latent capability) — 需要人工设计 3 套各 ~3 个 skill
- `scripts/aggregate.py` — 把 evaluation/ 下的 JSON 汇总成 4.6 风格的矩阵 markdown
- `reports/L0_baseline.md`、`reports/L1_evasion.md`
- benign control 的 5 个"看似 evasion 但实际良性"样本
