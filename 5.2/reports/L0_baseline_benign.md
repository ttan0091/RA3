# Scanner matrix: `/Users/tan/Desktop/RA3/5.2/evaluation/L0_baseline_benign`

## Per-case matrix

| case | Cisco-S | Cisco-F | SF | SS-S | SS-LLM |
|---|---|---|---|---|---|
| BEN01 | E | M | M | D | M |
| BEN02 | E | M | D | D | M |
| BEN03 | E | M | M | M | M |
| BEN04 | E | M | M | M | M |
| BEN05 | E | M | M | M | M |
| BEN06 | E | M | M | M | M |
| BEN07 | E | M | M | M | M |
| BEN08 | E | M | M | D | M |
| BEN09 | E | M | D | M | M |
| BEN10 | E | M | M | M | M |

## Per-scanner detection rate

| scanner | detected | missed | errors | detect rate | miss rate |
|---|---:|---:|---:|---:|---:|
| Cisco-S | 0 | 0 | 10 | 0.0% | 0.0% |
| Cisco-F | 0 | 10 | 0 | 0.0% | 100.0% |
| SF | 2 | 8 | 0 | 20.0% | 80.0% |
| SS-S | 3 | 7 | 0 | 30.0% | 70.0% |
| SS-LLM | 0 | 10 | 0 | 0.0% | 100.0% |

**Legend**: `D` = detected (HIGH/CRITICAL finding or MALICIOUS verdict); `M` = missed; `E` = scanner error; `?` = no result.
