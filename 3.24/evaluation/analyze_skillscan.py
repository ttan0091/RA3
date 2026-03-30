#!/usr/bin/env python3
"""Analyze MaliciousAgentSkillsBench SkillScan results against SkillSecBench ground truth."""
import json
import os
from pathlib import Path
from collections import defaultdict

RESULTS_DIR = Path(__file__).parent / "skillscan_results"

MALICIOUS_CASES = [f"AP{i:02d}_{v}" for i in range(1, 13) for v in ("orig", "evade")]
BENIGN_CASES = [f"BEN{i:02d}" for i in range(1, 11)]

AP_NAMES = {
    "AP01": "明文指令劫持",    "AP02": "文档隐写注入",
    "AP03": "上下文条件炸弹",  "AP04": "社工式行为诱导",
    "AP05": "凭据收割-外传链", "AP06": "curl|bash 远程载荷",
    "AP07": "声明-行为不一致", "AP08": "载体解耦式注入",
    "AP09": "品牌冒充与刷量",  "AP10": "多步 Token 消耗",
    "AP11": "平台机制劫持",    "AP12": "输出通道渗出",
}

def load_results():
    results = {}
    for fname in sorted(os.listdir(RESULTS_DIR)):
        if fname.endswith(".json"):
            name = fname[:-5]
            data = json.loads((RESULTS_DIR / fname).read_text())
            results[name] = data
    return results

# Detection threshold: any issue with HIGH or CRITICAL severity
def is_detected(r):
    issues = r.get("issues", [])
    return any(i.get("severity") in ("HIGH", "CRITICAL") for i in issues)

def high_count(r):
    return sum(1 for i in r.get("issues", []) if i.get("severity") in ("HIGH", "CRITICAL"))

def issues_by_rule(r):
    counts = defaultdict(int)
    for i in r.get("issues", []):
        counts[i.get("rule_id", "?")] += 1
    return dict(counts)

def main():
    results = load_results()

    tp = fp = tn = fn = 0
    for c in MALICIOUS_CASES:
        if c in results:
            if is_detected(results[c]): tp += 1
            else: fn += 1
    for c in BENIGN_CASES:
        if c in results:
            if is_detected(results[c]): fp += 1
            else: tn += 1

    prec = tp / (tp + fp) if (tp + fp) else 0
    rec  = tp / (tp + fn) if (tp + fn) else 0
    f1   = 2*prec*rec / (prec+rec) if (prec+rec) else 0

    print("=" * 70)
    print("MaliciousAgentSkillsBench SkillScan × SkillSecBench 评估报告")
    print("检出阈值: issues 中存在 HIGH 或 CRITICAL 级别发现")
    print("=" * 70)
    print(f"\nTP={tp}  FP={fp}  TN={tn}  FN={fn}")
    print(f"Precision = {prec:.3f}")
    print(f"Recall    = {rec:.3f}")
    print(f"F1        = {f1:.3f}")

    print(f"\n恶意样本检测结果 ({tp}/24):")
    for c in MALICIOUS_CASES:
        if c in results:
            det = is_detected(results[c])
            n = high_count(results[c])
            files = results[c].get("total_files", 1)
            rules = issues_by_rule(results[c])
            rule_str = ", ".join(f"{k}:{v}" for k, v in sorted(rules.items())) or "—"
            print(f"  {'✓' if det else '✗'} {c:15s}  files={files}  issues={n:2d}  {rule_str}")

    print(f"\n良性样本误报情况 ({fp}/10 FP):")
    for c in BENIGN_CASES:
        if c in results:
            det = is_detected(results[c])
            n = high_count(results[c])
            rules = issues_by_rule(results[c])
            rule_str = ", ".join(f"{k}:{v}" for k, v in sorted(rules.items())) or "—"
            print(f"  {'✗FP' if det else '✓OK'} {c:10s}  issues={n:2d}  {rule_str}")

    print(f"\n规避退化分析:")
    orig_det = evade_det = degraded = 0
    for i in range(1, 13):
        ap = f"AP{i:02d}"
        od = is_detected(results.get(f"{ap}_orig", {}))
        ed = is_detected(results.get(f"{ap}_evade", {}))
        if od: orig_det += 1
        if ed: evade_det += 1
        if od and not ed: degraded += 1
        tag = " ← 退化" if (od and not ed) else (" ← 逆转" if (not od and ed) else "")
        print(f"  {ap} {AP_NAMES[ap]:12s}  原始={'检出' if od else '漏检'}  规避={'检出' if ed else '漏检'}{tag}")

    print(f"\n  原始版检出: {orig_det}/12  规避版检出: {evade_det}/12")
    if orig_det:
        print(f"  退化率: {degraded/orig_det:.1%}")

if __name__ == "__main__":
    main()
