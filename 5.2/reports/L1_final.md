# 5.2 Skill Detector Evasion — final report

## L0 baseline detection rates

| scanner | malicious detect | benign FPR |
|---|---:|---:|
| Cisco-S | 2/24 (8.3%) | 2/10 (20.0%) |
| Cisco-F | 18/24 (75.0%) | 0/10 (0.0%) |
| SF | 10/24 (41.7%) | 2/10 (20.0%) |
| SS-S | 14/24 (58.3%) | 3/10 (30.0%) |
| SS-LLM | 23/24 (95.8%) | 0/10 (0.0%) |

## L1 attack roll-up (miss = scanner classified as benign)

| attack | N | sem=full | Cisco-S miss | Cisco-F miss | SF miss | SS-S miss | SS-LLM miss | both LLM miss | all 5 miss |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| a10 | 4 | 4/4 | 0/4 | 0/4 | 4/4 | 0/4 | 0/4 | 0/4 | 0/4 |
| a12 | 4 | 0/4 | 4/4 | 1/4 | 4/4 | 0/4 | 0/4 | 0/4 | 0/4 |
| a2 | 4 | 4/4 | 3/4 | 0/4 | 2/4 | 0/4 | 0/4 | 0/4 | 0/4 |
| a3 | 4 | 4/4 | 4/4 | 0/4 | 2/4 | 0/4 | 0/4 | 0/4 | 0/4 |
| a5 | 4 | 4/4 | 3/4 | 0/4 | 2/4 | 0/4 | 0/4 | 0/4 | 0/4 |
| a6 | 4 | 3/4 | 3/4 | 1/4 | 3/4 | 1/4 | 1/4 | 1/4 | 1/4 |
| a7 | 4 | 3/4 | 3/4 | 0/4 | 2/4 | 0/4 | 0/4 | 0/4 | 0/4 |
| a8 | 4 | 4/4 | 3/4 | 0/4 | 2/4 | 0/4 | 0/4 | 0/4 | 0/4 |
| a9 | 3 | 1/3 | 2/3 | 0/3 | 1/3 | 0/3 | 0/3 | 0/3 | 0/3 |

## L1 per-case matrix

| case | Cisco-S | Cisco-F | SF | SS-S | SS-LLM | semantic |
|---|---|---|---|---|---|---|
| AP01_a10 | D | D | M | D | D | full |
| AP01_a12 | M | M | M | D | D | n/a (permission gap is the test) |
| AP01_a2 | D | D | D | D | D | full |
| AP01_a3 | M | D | D | D | D | full |
| AP01_a5 | D | D | D | D | D | full |
| AP01_a6 | D | D | D | D | D | full |
| AP01_a7 | D | D | D | D | D | full |
| AP01_a8 | D | D | D | D | D | full |
| AP01_a9 | D | D | D | D | D | ? |
| AP05_a10 | D | D | M | D | D | full |
| AP05_a12 | M | D | M | D | D | n/a (permission gap is the test) |
| AP05_a2 | M | D | D | D | D | full |
| AP05_a3 | M | D | D | D | D | full |
| AP05_a5 | M | D | D | D | D | full |
| AP05_a6 | M | M | M | M | M | lost |
| AP05_a7 | M | D | D | D | D | full |
| AP05_a8 | M | D | D | D | D | full |
| AP05_a9 | M | D | D | D | D | ? |
| AP07_a10 | D | D | M | D | D | full |
| AP07_a12 | M | D | M | D | D | n/a (permission gap is the test) |
| AP07_a2 | M | D | M | D | D | full |
| AP07_a3 | M | D | M | D | D | full |
| AP07_a5 | M | D | M | D | D | full |
| AP07_a6 | M | D | M | D | D | full |
| AP07_a7 | M | D | M | D | D | full |
| AP07_a8 | M | D | M | D | D | full |
| AP07_a9 | M | D | M | D | D | full |
| AP08_a10 | D | D | M | D | D | full |
| AP08_a12 | M | D | M | D | D | n/a (permission gap is the test) |
| AP08_a2 | M | D | M | D | D | full |
| AP08_a3 | M | D | M | D | D | full |
| AP08_a5 | M | D | M | D | D | full |
| AP08_a6 | M | D | M | D | D | full |
| AP08_a7 | M | D | M | D | D | ? |
| AP08_a8 | M | D | M | D | D | full |

**Legend**: D = detected; M = missed; E = scanner error; ? = no result.
