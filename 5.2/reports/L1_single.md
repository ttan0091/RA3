# Scanner matrix: `/Users/tan/Desktop/RA3/5.2/evaluation/L1_single`

## Per-case matrix

| case | Cisco-S | Cisco-F | SF | SS-S | SS-LLM |
|---|---|---|---|---|---|
| AP01_a10 | D | D | M | D | D |
| AP01_a12 | M | M | M | D | D |
| AP01_a2 | D | D | D | D | D |
| AP01_a3 | M | D | D | D | D |
| AP01_a5 | D | D | D | D | D |
| AP01_a6 | D | D | D | D | D |
| AP01_a7 | D | D | D | D | D |
| AP01_a8 | D | D | D | D | D |
| AP01_a9 | D | D | D | D | D |
| AP05_a10 | D | D | M | D | D |
| AP05_a12 | M | D | M | D | D |
| AP05_a2 | M | D | D | D | D |
| AP05_a3 | M | D | D | D | D |
| AP05_a5 | M | D | D | D | D |
| AP05_a6 | M | M | M | M | M |
| AP05_a7 | M | D | D | D | D |
| AP05_a8 | M | D | D | D | D |
| AP05_a9 | M | D | D | D | D |
| AP07_a10 | D | D | M | D | D |
| AP07_a12 | M | D | M | D | D |
| AP07_a2 | M | D | M | D | D |
| AP07_a3 | M | D | M | D | D |
| AP07_a5 | M | D | M | D | D |
| AP07_a6 | M | D | M | D | D |
| AP07_a7 | M | D | M | D | D |
| AP07_a8 | M | D | M | D | D |
| AP07_a9 | M | D | M | D | D |
| AP08_a10 | D | D | M | D | D |
| AP08_a12 | M | D | M | D | D |
| AP08_a2 | M | D | M | D | D |
| AP08_a3 | M | D | M | D | D |
| AP08_a5 | M | D | M | D | D |
| AP08_a6 | M | D | M | D | D |
| AP08_a7 | M | D | M | D | D |
| AP08_a8 | M | D | M | D | D |

## Per-scanner detection rate

| scanner | detected | missed | errors | detect rate | miss rate |
|---|---:|---:|---:|---:|---:|
| Cisco-S | 10 | 25 | 0 | 28.6% | 71.4% |
| Cisco-F | 33 | 2 | 0 | 94.3% | 5.7% |
| SF | 13 | 22 | 0 | 37.1% | 62.9% |
| SS-S | 34 | 1 | 0 | 97.1% | 2.9% |
| SS-LLM | 34 | 1 | 0 | 97.1% | 2.9% |

## Per-attack roll-up

| attack | N | Cisco-F miss | SS-LLM miss | both LLM miss | all 5 miss |
|---|---:|---:|---:|---:|---:|
| a10 | 4 | 0/4 | 0/4 | 0/4 | 0/4 |
| a12 | 4 | 1/4 | 0/4 | 0/4 | 0/4 |
| a2 | 4 | 0/4 | 0/4 | 0/4 | 0/4 |
| a3 | 4 | 0/4 | 0/4 | 0/4 | 0/4 |
| a5 | 4 | 0/4 | 0/4 | 0/4 | 0/4 |
| a6 | 4 | 1/4 | 1/4 | 1/4 | 1/4 |
| a7 | 4 | 0/4 | 0/4 | 0/4 | 0/4 |
| a8 | 4 | 0/4 | 0/4 | 0/4 | 0/4 |
| a9 | 3 | 0/3 | 0/3 | 0/3 | 0/3 |

**Legend**: `D` = detected (HIGH/CRITICAL finding or MALICIOUS verdict); `M` = missed; `E` = scanner error; `?` = no result.
