# 53 个 evade_g skill 的 LLM 输入 token 统计

Token 统计使用 `tiktoken` 的 `cl100k_base` 编码，作为 OpenAI-compatible chat 输入长度的近似值。

## 固定 system prompt token

- SkillScan-style system prompt: `1010` tokens
- Cisco-style system prompt: `3029` tokens

## 总输入 token 汇总

| 配置 | Min | Median | Mean | P90 | Max |
|---|---:|---:|---:|---:|---:|
| SkillScan-style total | 1433 | 1790 | 1778.6 | 2019 | 2424 |
| Cisco-style total | 3434 | 3791 | 3779.6 | 4020 | 4425 |
| Skill files only | 423 | 780 | 768.6 | 1009 | 1414 |

## 每个 case

| Case | Group | Skill files | SkillScan total | Cisco total |
|---|---:|---:|---:|---:|
| `AP01_evade_g1` | G1 | 427 | 1437 | 3438 |
| `AP01_evade_g2` | G2 | 466 | 1476 | 3477 |
| `AP01_evade_g3` | G3 | 423 | 1433 | 3434 |
| `AP01_evade_g4` | G4 | 497 | 1507 | 3508 |
| `AP01_evade_g5` | G5 | 874 | 1884 | 3885 |
| `AP02_evade_g1` | G1 | 438 | 1448 | 3449 |
| `AP02_evade_g3` | G3 | 483 | 1493 | 3494 |
| `AP02_evade_g5` | G5 | 918 | 1928 | 3929 |
| `AP03_evade_g1` | G1 | 601 | 1611 | 3612 |
| `AP03_evade_g2` | G2 | 615 | 1625 | 3626 |
| `AP03_evade_g3` | G3 | 613 | 1623 | 3624 |
| `AP03_evade_g7` | G7 | 552 | 1562 | 3563 |
| `AP04_evade_g1` | G1 | 544 | 1554 | 3555 |
| `AP04_evade_g2` | G2 | 549 | 1559 | 3560 |
| `AP04_evade_g3` | G3 | 514 | 1524 | 3525 |
| `AP05_evade_g1` | G1 | 720 | 1730 | 3731 |
| `AP05_evade_g2` | G2 | 918 | 1928 | 3929 |
| `AP05_evade_g3` | G3 | 713 | 1723 | 3724 |
| `AP05_evade_g4` | G4 | 844 | 1854 | 3855 |
| `AP05_evade_g5` | G5 | 1394 | 2404 | 4405 |
| `AP05_evade_g6` | G6 | 968 | 1978 | 3979 |
| `AP05_evade_g7` | G7 | 753 | 1763 | 3764 |
| `AP05_evade_g8` | G8 | 973 | 1983 | 3984 |
| `AP06_evade_g1` | G1 | 432 | 1442 | 3443 |
| `AP06_evade_g2` | G2 | 542 | 1552 | 3553 |
| `AP06_evade_g3` | G3 | 467 | 1477 | 3478 |
| `AP07_evade_g1` | G1 | 862 | 1872 | 3873 |
| `AP07_evade_g2` | G2 | 911 | 1921 | 3922 |
| `AP07_evade_g3` | G3 | 901 | 1911 | 3912 |
| `AP07_evade_g4` | G4 | 1016 | 2026 | 4027 |
| `AP07_evade_g6` | G6 | 651 | 1661 | 3662 |
| `AP07_evade_g7` | G7 | 942 | 1952 | 3953 |
| `AP07_evade_g8` | G8 | 869 | 1879 | 3880 |
| `AP08_evade_g1` | G1 | 1009 | 2019 | 4020 |
| `AP08_evade_g2` | G2 | 1055 | 2065 | 4066 |
| `AP08_evade_g3` | G3 | 1047 | 2057 | 4058 |
| `AP08_evade_g5` | G5 | 1414 | 2424 | 4425 |
| `AP08_evade_g6` | G6 | 772 | 1782 | 3783 |
| `AP08_evade_g7` | G7 | 934 | 1944 | 3945 |
| `AP08_evade_g8` | G8 | 872 | 1882 | 3883 |
| `AP09_evade_g1` | G1 | 784 | 1794 | 3795 |
| `AP09_evade_g2` | G2 | 793 | 1803 | 3804 |
| `AP09_evade_g3` | G3 | 748 | 1758 | 3759 |
| `AP10_evade_g1` | G1 | 983 | 1993 | 3994 |
| `AP10_evade_g3` | G3 | 994 | 2004 | 4005 |
| `AP10_evade_g8` | G8 | 940 | 1950 | 3951 |
| `AP11_evade_g1` | G1 | 886 | 1896 | 3897 |
| `AP11_evade_g3` | G3 | 687 | 1697 | 3698 |
| `AP11_evade_g5` | G5 | 1038 | 2048 | 4049 |
| `AP11_evade_g6` | G6 | 625 | 1635 | 3636 |
| `AP11_evade_g8` | G8 | 780 | 1790 | 3791 |
| `AP12_evade_g1` | G1 | 529 | 1539 | 3540 |
| `AP12_evade_g3` | G3 | 455 | 1465 | 3466 |

## SkillScan-style total 最大的 10 个

| Case | Tokens |
|---|---:|
| `AP08_evade_g5` | 2424 |
| `AP05_evade_g5` | 2404 |
| `AP08_evade_g2` | 2065 |
| `AP08_evade_g3` | 2057 |
| `AP11_evade_g5` | 2048 |
| `AP07_evade_g4` | 2026 |
| `AP08_evade_g1` | 2019 |
| `AP10_evade_g3` | 2004 |
| `AP10_evade_g1` | 1993 |
| `AP05_evade_g8` | 1983 |

## Cisco-style total 最大的 10 个

| Case | Tokens |
|---|---:|
| `AP08_evade_g5` | 4425 |
| `AP05_evade_g5` | 4405 |
| `AP08_evade_g2` | 4066 |
| `AP08_evade_g3` | 4058 |
| `AP11_evade_g5` | 4049 |
| `AP07_evade_g4` | 4027 |
| `AP08_evade_g1` | 4020 |
| `AP10_evade_g3` | 4005 |
| `AP10_evade_g1` | 3994 |
| `AP05_evade_g8` | 3984 |
