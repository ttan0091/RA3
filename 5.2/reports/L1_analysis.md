# 5.2 L1 Evasion — Analysis (DeepSeek v4-flash judge)

## TL;DR

- **9 attacks × 4 APs = 35 evasion samples** (A9 only effective on AP07/AP08 because A1/A5 _orig have no `.py` files; AP08 timed out so A9 has 3 cases).
- **No genuine all-5-scanner evasion**. Only `AP05_a6` slipped past everyone, but its `semantic_preservation = lost` — the LLM rewriter deleted the malicious script. Not a real attack.
- **Cisco-F miss = 2/35; SS-LLM miss = 1/35** — both LLM scanners stay strong (consistent with 4.6's finding that LLM judges close static blind spots).
- Static scanners (Cisco-S, SF) **see more findings** under L1 than at baseline, because attacks add new files/symbols that pattern-rules pick up.
- **A12 permission-gap is the cleanest hit on rule-based scanners** (4/4 miss on Cisco-S and SF) — they don't audit `permissions:` overreach in YAML.
- **A10 cross-file dilution beats SkillFortify 4/4** (utils.py / cfg.json drains the source-to-sink chain out of view).

## L0 baselines (sanity check)

| scanner | malicious detect | benign FPR |
|---|---:|---:|
| Cisco-S | 2/24 (8.3%) | 2/10 (20.0%) |
| Cisco-F | 18/24 (75.0%) | 0/10 (0.0%) |
| SF | 10/24 (41.7%) | 2/10 (20.0%) |
| SS-S | 14/24 (58.3%) | 3/10 (30.0%) |
| SS-LLM | 23/24 (95.8%) | 0/10 (0.0%) |

LLM scanners (Cisco-F, SS-LLM) keep both high TPR and zero FPR. Static scanners are noisy in both directions.

## L1 attack rollup

| attack | source paper | N | sem=full | Cisco-S miss | Cisco-F miss | SF miss | SS-S miss | SS-LLM miss | both LLM miss | all 5 miss |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| **a2** AdvJudge candidates | arXiv:2512.17375 | 4 | 4/4 | 3/4 | 0/4 | 2/4 | 0/4 | 0/4 | 0/4 | 0/4 |
| **a3** Adv. Paraphrasing | NeurIPS 2025 (2506.07001) | 4 | 4/4 | 4/4 | 0/4 | 2/4 | 0/4 | 0/4 | 0/4 | 0/4 |
| **a5** INSEC comment | ICML 2025 (2408.02509) | 4 | 4/4 | 3/4 | 0/4 | 2/4 | 0/4 | 0/4 | 0/4 | 0/4 |
| **a6** SVulAttack | IEEE 2025 (Shield Broken) | 4 | 3/4 | 3/4 | 1/4 | 3/4 | 1/4 | 1/4 | 1/4 | **1/4 ⚠ semantic lost** |
| **a7** simplification | arXiv:2602.00305 | 4 | 3/4 | 3/4 | 0/4 | 2/4 | 0/4 | 0/4 | 0/4 | 0/4 |
| **a8** 7-transform pipeline | arXiv:2512.16538 | 4 | 4/4 | 3/4 | 0/4 | 2/4 | 0/4 | 0/4 | 0/4 | 0/4 |
| **a9** MCTS over a8 | AdVulCode (MDPI 2023) | 3 | 1/3 | 2/3 | 0/3 | 1/3 | 0/3 | 0/3 | 0/3 | 0/3 |
| **a10** cross-file dilution | IPI / Snyk | 4 | 4/4 | 0/4 | 0/4 | **4/4** | 0/4 | 0/4 | 0/4 | 0/4 |
| **a12** permission gap | OWASP Agentic Top 10 | 4 | n/a | **4/4** | 1/4 | **4/4** | 0/4 | 0/4 | 0/4 | 0/4 |

> "miss" = scanner classified the malicious skill as benign.
> "semantic preservation" was judged by deepseek-v4-flash on (orig, rewritten) pair.

## Findings

### 1. LLM judges are robust under all the SKILL.md / code rewrite attacks we tried
- Cisco-F miss = 2/35 (one A6 with lost semantics, one A12)
- SS-LLM miss = 1/35 (the same A6 case)
- Genuine all-5 miss with semantic preserved: **0/35**

This corroborates the 4.6 finding (0/53 genuine evasion) on a different attack family and a different LLM judge backbone (DeepSeek v4-flash vs gpt-5.4).

### 2. Single noisy "score=1.0" wins disappear on a second judge
- A3/AP01 round 1, A9/AP07 trial 1, A9/AP08 trial 1 each produced score=1.0 (n_findings=0) when the attack-internal Cisco-F judge was queried.
- After the attack picked the best variant, **the L1 scanner re-run by SS-LLM still flagged it MALICIOUS** in every case.
- Implication: a single LLM judge's verdict is fragile to noise; **defending with two independent LLM judges is meaningfully more robust** than either alone.

### 3. Cross-file dilution (a10) is the cleanest hit on a real scanner
- 4/4 SkillFortify miss when source-to-sink is split across `SKILL.md` → `helper.py` → `utils.py` + `cfg.json`.
- Other 4 scanners still detect — this is a SF-specific blind spot in scanning only manifest-level intent.

### 4. Permission-gap (a12) exposes a real defense gap
- Cisco-S 4/4 miss, SF 4/4 miss, even Cisco-F 1/4 miss.
- The skill body does only Markdown reformatting; the YAML declares broad `~/.aws/*` reads, `*` network. Static scanners pattern-match on body symbols, not on permission consistency.

### 5. Static scanners get more sensitive under L1, not less
- Cisco-S: baseline 8.3% → L1 28.6% detect (more triggers in injected helper code)
- SS-S: baseline 58.3% → L1 97.1% detect (transform pipelines create new files SS-S knows how to flag)
- SF stays roughly flat (41.7% → 37.1%): SF reads SKILL.md only, so file-level transforms don't help and don't hurt much.

### 6. SVulAttack-style line-importance rewriting (a6) is double-edged
- Best per-attack score on Cisco-F (1/4 miss) and SS-LLM (1/4 miss), but the same case had `semantic=lost`.
- Lesson: a strong attacker LLM rewriting "high-importance" lines tends to delete the actual malicious behavior. Without an external semantic-preservation oracle in the loop, this attack will overfit to the detector and break the payload.

## Cost summary

- Detector (judge) calls: ~600 (5 scanners × 35 samples + L0 baselines + iterative attack queries)
- Attacker / paraphrase calls: ~150 (A3 paraphrase, A6 rewrite, A4 not run)
- All on `deepseek-v4-flash` only (no `v4-pro`, no GPU).

## Caveats

- Only **4 APs** (AP01/AP05/AP07/AP08) — covers static-weak (AP07/AP08) and SKILL.md-only (AP01) cases but not all 12.
- Some semantic preservation judgments (`?`) are missing because either the attack didn't write `attack.json` or the judge call was skipped.
- A9 incomplete: AP08 hung on DeepSeek retries; only AP07 fully scored.
- "Best score" reported during attack is the detector judge's verdict on that single rewrite; it does **not** guarantee a second independent judge will agree (see §2).
- The single A6/AP05 "all-5 miss" is misleading because its semantic was destroyed. Real ASR with semantic preserved = **0**.

## Reusable artifacts

| What | Path |
|---|---|
| Per-case matrix CSV | `5.2/reports/L1_final.csv` |
| Per-attack-meta CSV | `5.2/reports/L1_attacks_meta.csv` |
| Per-attack iteration logs | `5.2/benchmark/L1_single/<AP>_<aid>/attack.json` |
| Generated evasion skills | `5.2/benchmark/L1_single/<AP>_<aid>/{SKILL.md,*.py,...}` |
| Scanner outputs | `5.2/evaluation/L1_single/{cisco_static,cisco_full,skillfortify,skillscan_static,skillscan_llm}/*.json` |
| Baselines | `5.2/evaluation/L0_baseline_{malicious,benign}/...` |
| L1 baseline reports | `5.2/reports/L0_baseline_{malicious,benign}.md` |
| Single-eval matrix | `5.2/reports/L1_single.md` |
| Final report | `5.2/reports/L1_final.md` |

## Possible next steps (not done)

1. Replace the in-loop judge with **a different model than the verifier** (currently both are deepseek-v4-flash). When attacker and verifier are the same model, occasional score=1.0 are likely just noise. Use `deepseek-v4-pro` as the verifier for fewer false-positive "wins".
2. Add a **fixed semantic-preservation oracle** before counting a sample as evasion. (Currently we judge after the fact and discover semantic-lost cases too late.)
3. Run on the remaining 8 APs (AP02/03/04/06/09/10/11/12) for full coverage.
4. Implement **A4 PAIR/TAP** (skipped here for cost) and **A11 multi-skill latent capability** (needs hand-crafted 2–3 skill bundles).
5. Add a **second LLM judge defense**: run any sample through Cisco-F AND SS-LLM, flag if either says malicious. Already in our matrix — confirms 0% all-5 miss with semantic preserved.
