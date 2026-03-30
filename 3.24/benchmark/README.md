# SkillSecBench v1.0

**首个对抗性 AI Agent Skill 安全检测 Benchmark**

## 概述

SkillSecBench 用于评估 AI Agent Skill 安全扫描工具的检测能力和对抗鲁棒性。与已有 benchmark（如 AgentShield 537 cases）的关键差异：

1. **双版本设计**：每种攻击模式有 original（baseline）和 evasion（加固规避）两个版本，量化 scanner 面对规避技术时的检出率退化
2. **系统性规避技术**：evasion 版本使用文献中记录的真实规避手法（语态变换、载体解耦、编码混淆、条件门控等）
3. **良性对照组**：10 个故意设计成"容易被误判"的正常 skill，测试 scanner precision
4. **五维标注**：每个 case 标注攻击技术、生命周期阶段、载体层级、规避等级、检测需求

## 规模

| 类型 | 数量 | 说明 |
|------|------|------|
| 恶意-原始版本 | 12 | AP-01 到 AP-12，EL0-EL2 规避等级 |
| 恶意-规避版本 | 12 | 对应加固版本，EL2-EL4 规避等级 |
| 良性对照 | 10 | 容易误判的正常 skill |
| **合计** | **34** | |

## 目录结构

```
benchmark/
├── manifest.yaml           # 全部标注元数据
├── README.md               # 本文件
├── malicious/
│   ├── AP01_orig/          # 明文指令劫持 - 原始版
│   │   └── SKILL.md
│   ├── AP01_evade/         # 明文指令劫持 - 规避版
│   │   └── SKILL.md
│   ├── AP02_orig/          # 文档隐写注入 - 原始版
│   │   └── SKILL.md
│   ├── ...                 # AP03-AP12 同理
│   └── AP12_evade/
│       └── SKILL.md
└── benign/
    ├── BEN01/              # S3 备份工具（含 HTTP 传输 → 易误判）
    │   └── SKILL.md
    ├── ...
    └── BEN10/
        └── SKILL.md
```

## 攻击模式覆盖

| 模式 | 原始版 | 规避版 | 规避技术 |
|------|--------|--------|---------|
| AP-01 明文指令劫持 | code-guardian | code-standards | 语态变换+良性外壳稀释 |
| AP-02 文档隐写注入 | doc-formatter | md-linter | 零宽 Unicode+位置隐藏 |
| AP-03 上下文条件炸弹 | deploy-helper | env-doctor | 条件门控+语义伪装 |
| AP-04 社工式行为诱导 | project-bootstrap | workspace-init | 结构模仿+curl 弱化 |
| AP-05 凭据收割-外传链 | cloud-sync | config-migrator | 十六进制编码+载体解耦 |
| AP-06 curl\|bash 远程载荷 | depcheck | perf-profiler | URL 运行时拼接+Python 间接调用 |
| AP-07 声明-行为不一致 | text-transform | log-analyzer | 遥测伪装+载体解耦 |
| AP-08 载体解耦式注入 | code-review-assistant | test-helper | 全项目遍历+coverage 伪装 |
| AP-09 品牌冒充与刷量 | githubb | gh-actions-helper | 微妙命名+analytics 伪装 |
| AP-10 多步 Token 消耗 | thorough-validator | api-contract-tester | 收敛性修辞+无脚本纯指令 |
| AP-11 平台机制劫持 | mcp-toolkit | devcontainer-setup | 多配置文件分散+合法化 framing |
| AP-12 输出通道渗出 | link-generator | research-assistant | 学术服务伪装+机构访问 framing |

## 使用方法

### 1. 将 benchmark cases 作为 scanner 输入

每个子目录就是一个 skill 包。将其指向待评估的 scanner：

```bash
# Cisco Skill Scanner 示例
for case_dir in benchmark/malicious/*/; do
    skill-scanner scan "$case_dir" --output json >> results.jsonl
done
for case_dir in benchmark/benign/*/; do
    skill-scanner scan "$case_dir" --output json >> results.jsonl
done
```

### 2. 对比 scanner 输出与 ground truth

从 `manifest.yaml` 读取 `ground_truth` 标签，与 scanner 输出比对，计算：

- **Precision** = TP / (TP + FP)
- **Recall** = TP / (TP + FN)
- **F1** = 2 × Precision × Recall / (Precision + Recall)

### 3. 计算规避退化率

```
Degradation = 1 - (Recall_evasion / Recall_original)
```

对每种攻击模式分别计算退化率，找出各 scanner 的致命弱点。

### 4. 按维度分解分析

利用 manifest 中的五维标注，按以下维度分解检出率：
- 按攻击技术类别（A/B/C/D）
- 按载体层级（CL1-CL6）
- 按规避等级（EL0-EL4）
- 按检测需求（DR1-DR6）

## 标注 Schema

每个 case 在 manifest.yaml 中的标注字段：

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | string | 唯一标识，如 MAL-AP01-ORIG |
| `path` | string | 相对于 benchmark/ 的路径 |
| `attack_pattern` | string | AP-01 到 AP-12 |
| `variant` | string | original / evasion |
| `attack_techniques` | list | A1-A4, B1-B4, C1-C4, D1-D4 |
| `lifecycle_phases` | list | L1-L6 |
| `carrier_layers` | list | CL1-CL6 |
| `evasion_level` | string | EL0-EL4 |
| `evasion_techniques` | list | 具体规避手法（仅 evasion 版本） |
| `detection_requirement` | list | DR1-DR6 |
| `severity` | string | low / medium / high / critical |
| `ground_truth` | string | malicious / benign |
| `malicious_elements` | list | 具体恶意内容位置和描述 |
| `detection_hints` | list | 应该检出的线索 |
| `expected_detection` | dict | 对各 scanner 的预期检出结果 |

## 与分类手册的关系

本 benchmark 的标注体系来自 `Skill安全漏洞分类手册_v1.md` 中提出的五维分类框架。分类手册提供理论基础，benchmark 提供实验材料。

## 局限性

1. 34 个 case 的规模适合精细化分析，但不适合做大规模统计显著性检验
2. evasion 版本的有效性需要实际跑测验证（预期检出标注基于架构分析推断）
3. AP-10（token drain）和 AP-12（输出通道）需要运行时测试框架配合，纯静态 scanner 可能无法评估
4. 良性对照组覆盖了 8 种常见误判场景，但未穷举所有可能的 false positive 模式
