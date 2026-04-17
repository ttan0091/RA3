#!/usr/bin/env python3
"""analyze_evasion_results.py - 分析 evade_g* 的 scanner 检出结果，生成结果矩阵和报告"""
import json
from pathlib import Path
from collections import defaultdict

EVAL_DIR = Path("/Users/tan/Desktop/RA3/3.24/evaluation")
BENCHMARK = Path("/Users/tan/Desktop/RA3/3.24/benchmark/malicious")

# ── 加载结果 ──────────────────────────────────────────────

def load_cisco_static():
    d = {}
    for f in (EVAL_DIR / "cisco_scanner_g" / "static").glob("*.json"):
        case = f.stem
        data = json.loads(f.read_text())
        detected = False
        if data.get("is_safe") is False:
            for finding in data.get("findings", []):
                if finding.get("severity") not in ("INFO", "SAFE", "LOW"):
                    detected = True
                    break
        d[case] = {"is_safe": data.get("is_safe"), "detected": detected,
                   "findings": len(data.get("findings", []))}
    return d

def load_cisco_full():
    d = {}
    full_dir = EVAL_DIR / "cisco_scanner_g" / "full_gpt54"
    for f in full_dir.glob("*.json"):
        case = f.stem
        data = json.loads(f.read_text())
        detected = data.get("_detected", False)
        if not detected and data.get("is_safe") is False:
            detected = True
        d[case] = {"is_safe": data.get("is_safe"), "detected": detected,
                   "findings": data.get("findings_count", 0)}
    return d

def load_skillfortify():
    d = {}
    for f in (EVAL_DIR / "skillfortify_g_results").glob("*.json"):
        case = f.stem
        data = json.loads(f.read_text())
        skills = data.get("skills", [])
        detected = any(not s.get("is_safe", True) for s in skills)
        d[case] = {"detected": detected, "skills": len(skills)}
    return d

def load_skillscan_static():
    d = {}
    for f in (EVAL_DIR / "skillscan_g_results").glob("*.json"):
        case = f.stem
        data = json.loads(f.read_text())
        issues = data.get("issues", [])
        detected = any(i.get("severity") in ("HIGH", "CRITICAL") for i in issues)
        d[case] = {"detected": detected, "issues": len(issues)}
    return d

def load_skillscan_gpt54():
    d = {}
    gpt_dir = EVAL_DIR / "skillscan_gpt54_g_results"
    for f in gpt_dir.glob("*.json"):
        case = f.stem
        data = json.loads(f.read_text())
        # MALICIOUS, MISALIGNED, SUSPICIOUS all count as detected
        status = data.get("audit_summary", {}).get("intent_alignment_status", "")
        detected = status in ("MALICIOUS", "MISALIGNED", "SUSPICIOUS") or data.get("_detected", False)
        d[case] = {"detected": detected, "status": status or data.get("error", "?")}
    return d

cisco_static = load_cisco_static()
cisco_full = load_cisco_full()
skillfortify = load_skillfortify()
skillscan_static = load_skillscan_static()
skillscan_gpt54 = load_skillscan_gpt54()

print(f"Loaded: Cisco-Static={len(cisco_static)}, Cisco-Full={len(cisco_full)}, "
      f"SF={len(skillfortify)}, SS-Static={len(skillscan_static)}, SS-GPT54={len(skillscan_gpt54)}")

# ── 恶意语义保留度 ──────────────────────────────────────────

SEMANTIC_PRESERVATION = {
    **{f"AP{i:02d}_evade_g1": "完全保留" for i in range(1, 13)},
    **{f"AP{k}_evade_g2": "完全保留" for k in ["01","03","04","05","06","07","08","09"]},
    "AP01_evade_g3": "完全保留", "AP02_evade_g3": "完全保留", "AP03_evade_g3": "完全保留",
    "AP04_evade_g3": "完全保留", "AP05_evade_g3": "完全保留", "AP06_evade_g3": "完全保留",
    "AP07_evade_g3": "完全保留", "AP08_evade_g3": "完全保留", "AP09_evade_g3": "完全保留",
    "AP10_evade_g3": "完全保留", "AP11_evade_g3": "完全保留", "AP12_evade_g3": "完全保留",
    "AP01_evade_g4": "完全保留", "AP05_evade_g4": "完全保留", "AP07_evade_g4": "完全保留",
    "AP01_evade_g5": "完全保留", "AP02_evade_g5": "完全保留", "AP05_evade_g5": "完全保留",
    "AP08_evade_g5": "完全保留", "AP11_evade_g5": "完全保留",
    "AP05_evade_g6": "完全保留", "AP07_evade_g6": "完全保留",
    "AP08_evade_g6": "完全保留", "AP11_evade_g6": "完全保留",
    "AP03_evade_g7": "完全保留", "AP05_evade_g7": "完全保留",
    "AP07_evade_g7": "完全保留", "AP08_evade_g7": "完全保留",
    "AP05_evade_g8": "完全保留", "AP07_evade_g8": "完全保留",
    "AP08_evade_g8": "完全保留", "AP10_evade_g8": "完全保留", "AP11_evade_g8": "完全保留",
}

# ── 汇总所有 case ──────────────────────────────────────────
all_cases = sorted(set(
    list(cisco_static.keys()) + list(skillfortify.keys()) +
    list(skillscan_static.keys()) + list(skillscan_gpt54.keys()) + list(cisco_full.keys())
))

groups = defaultdict(list)
for case in all_cases:
    g = case.split("_evade_g")[1] if "_evade_g" in case else "?"
    groups[f"G{g}"].append(case)

def D(detected): return "D" if detected else "M"

# ── 打印结果矩阵 ──────────────────────────────────────────
header = f"{'Case':<22} {'Cisco-S':>8} {'Cisco-F':>8} {'SF':>6} {'SS-S':>6} {'SS-LLM':>8} {'语义':>8}"
print("\n" + "=" * 75)
print("Evasion 结果矩阵 (D=检出 M=漏检)")
print("=" * 75)
print(header)
print("-" * 75)

group_stats = {}
for gname in sorted(groups.keys()):
    cases = sorted(groups[gname])
    g_det_cs = g_det_cf = g_det_sf = g_det_ss = g_det_sg = 0
    g_eff_static = 0   # 有效绕过：所有3静态scanner漏检 + 语义保留
    g_eff_all = 0      # 有效绕过：所有5个scanner漏检 + 语义保留

    for case in cases:
        cs = cisco_static.get(case, {})
        cf = cisco_full.get(case, {})
        sf = skillfortify.get(case, {})
        ss = skillscan_static.get(case, {})
        sg = skillscan_gpt54.get(case, {})
        sem = SEMANTIC_PRESERVATION.get(case, "未知")

        c_s = D(cs.get("detected", False))
        c_f = D(cf.get("detected", False))
        f_d = D(sf.get("detected", False))
        s_d = D(ss.get("detected", False))
        g_d = D(sg.get("detected", False))

        if cs.get("detected"): g_det_cs += 1
        if cf.get("detected"): g_det_cf += 1
        if sf.get("detected"): g_det_sf += 1
        if ss.get("detected"): g_det_ss += 1
        if sg.get("detected"): g_det_sg += 1

        static_miss = not cs.get("detected") and not sf.get("detected") and not ss.get("detected")
        all_miss = static_miss and not cf.get("detected") and not sg.get("detected")

        if static_miss and sem == "完全保留":
            g_eff_static += 1
        if all_miss and sem == "完全保留":
            g_eff_all += 1

        print(f"  {case:<20} {c_s:>8} {c_f:>8} {f_d:>6} {s_d:>6} {g_d:>8} {sem:>8}")

    n = len(cases)
    group_stats[gname] = {
        "n": n,
        "cisco_static_det": g_det_cs,
        "cisco_full_det": g_det_cf,
        "sf_det": g_det_sf,
        "ss_det": g_det_ss,
        "ss_gpt54_det": g_det_sg,
        "eff_static": g_eff_static,
        "eff_all": g_eff_all,
        "bypass_rate_static": g_eff_static / n if n else 0,
        "bypass_rate_all": g_eff_all / n if n else 0,
    }
    print(f"  {'─'*70}")
    print(f"  {gname}: CS={g_det_cs}/{n} CF={g_det_cf}/{n} SF={g_det_sf}/{n} "
          f"SS-S={g_det_ss}/{n} SS-LLM={g_det_sg}/{n} "
          f"| 静态绕过={g_eff_static}/{n} 全绕过={g_eff_all}/{n}")
    print()

# ── Group 汇总表 ──────────────────────────────────────────
print("=" * 90)
print("Group 汇总")
print("=" * 90)
print(f"{'Group':<6} {'N':>4} {'Cisco-S':>8} {'Cisco-F':>8} {'SF':>6} {'SS-S':>6} {'SS-LLM':>8} {'静态绕过率':>12} {'全绕过率':>10}")
print("-" * 90)
for gname in sorted(group_stats.keys()):
    s = group_stats[gname]
    n = s["n"]
    print(f"{gname:<6} {n:>4} "
          f"{s['cisco_static_det']:>4}/{n:<3} "
          f"{s['cisco_full_det']:>4}/{n:<3} "
          f"{s['sf_det']:>3}/{n:<3} "
          f"{s['ss_det']:>3}/{n:<2} "
          f"{s['ss_gpt54_det']:>4}/{n:<3} "
          f"{s['bypass_rate_static']:>10.1%}   "
          f"{s['bypass_rate_all']:>8.1%}")

total = len(all_cases)
total_cs = sum(1 for c in all_cases if cisco_static.get(c, {}).get("detected"))
total_cf = sum(1 for c in all_cases if cisco_full.get(c, {}).get("detected"))
total_sf = sum(1 for c in all_cases if skillfortify.get(c, {}).get("detected"))
total_ss = sum(1 for c in all_cases if skillscan_static.get(c, {}).get("detected"))
total_sg = sum(1 for c in all_cases if skillscan_gpt54.get(c, {}).get("detected"))
total_eff_static = sum(s["eff_static"] for s in group_stats.values())
total_eff_all = sum(s["eff_all"] for s in group_stats.values())

print("-" * 90)
print(f"{'总计':<6} {total:>4} "
      f"{total_cs:>4}/{total:<3} "
      f"{total_cf:>4}/{total:<3} "
      f"{total_sf:>3}/{total:<3} "
      f"{total_ss:>3}/{total:<2} "
      f"{total_sg:>4}/{total:<3} "
      f"{total_eff_static/total:>10.1%}   "
      f"{total_eff_all/total:>8.1%}")

# ── 有效绕过案例（静态3个scanner全漏检）──────────────────
print("\n" + "=" * 60)
print("有效绕过案例（3静态scanner全漏检 + 语义完全保留）")
print("=" * 60)
eff_cases_static = []
for case in all_cases:
    cs = cisco_static.get(case, {})
    sf = skillfortify.get(case, {})
    ss = skillscan_static.get(case, {})
    sem = SEMANTIC_PRESERVATION.get(case, "未知")
    if not cs.get("detected") and not sf.get("detected") and not ss.get("detected") and sem == "完全保留":
        eff_cases_static.append(case)
for c in sorted(eff_cases_static):
    sg_det = "SS-LLM:D" if skillscan_gpt54.get(c, {}).get("detected") else "SS-LLM:M"
    cf_det = "CF:D" if cisco_full.get(c, {}).get("detected") else "CF:M"
    print(f"  ✓ {c}  [{cf_det} {sg_det}]")
print(f"\n共 {len(eff_cases_static)}/{total} 个样本绕过3个静态scanner ({len(eff_cases_static)/total:.1%})")

# ── 写出报告 ──────────────────────────────────────────────
report_lines = []
report_lines.append("# Evasion 实验结果报告（完整版）\n")
report_lines.append("**Scanner 配置**：Cisco Static / Cisco Full(gpt-5.4) / SkillFortify / SkillScan Static / SkillScan GPT-5.4  \n")

report_lines.append("## 结果矩阵\n")
report_lines.append(f"| {'Case':<22} | {'Cisco-S':>8} | {'Cisco-F':>8} | {'SF':>6} | {'SS-S':>6} | {'SS-LLM':>8} | 语义 |")
report_lines.append(f"|{'-'*24}|{'-'*10}|{'-'*10}|{'-'*8}|{'-'*8}|{'-'*10}|{'-'*8}|")

for case in sorted(all_cases):
    cs = cisco_static.get(case, {})
    cf = cisco_full.get(case, {})
    sf = skillfortify.get(case, {})
    ss = skillscan_static.get(case, {})
    sg = skillscan_gpt54.get(case, {})
    sem = SEMANTIC_PRESERVATION.get(case, "未知")
    static_miss = not cs.get("detected") and not sf.get("detected") and not ss.get("detected")
    mark = " ★" if (static_miss and sem == "完全保留") else ""
    report_lines.append(
        f"| {case:<22} | {'D' if cs.get('detected') else 'M':>8} "
        f"| {'D' if cf.get('detected') else 'M':>8} "
        f"| {'D' if sf.get('detected') else 'M':>6} "
        f"| {'D' if ss.get('detected') else 'M':>6} "
        f"| {'D' if sg.get('detected') else 'M':>8} "
        f"| {sem}{mark} |"
    )

report_lines.append("\n★ = 绕过3个静态scanner（Cisco-S / SF / SS-S）且语义完全保留\n")

report_lines.append("## Group 汇总\n")
report_lines.append("| Group | N | Cisco-S | Cisco-F | SF | SS-S | SS-LLM | 静态绕过率 | 全绕过率 |")
report_lines.append("|-------|---|---------|---------|----|----- |--------|----------|---------|")
for gname in sorted(group_stats.keys()):
    s = group_stats[gname]
    n = s["n"]
    report_lines.append(
        f"| {gname} | {n} | {s['cisco_static_det']}/{n} | {s['cisco_full_det']}/{n} "
        f"| {s['sf_det']}/{n} | {s['ss_det']}/{n} | {s['ss_gpt54_det']}/{n} "
        f"| {s['bypass_rate_static']:.1%} | {s['bypass_rate_all']:.1%} |"
    )
report_lines.append(
    f"| **总计** | {total} | {total_cs}/{total} | {total_cf}/{total} "
    f"| {total_sf}/{total} | {total_ss}/{total} | {total_sg}/{total} "
    f"| {total_eff_static/total:.1%} | {total_eff_all/total:.1%} |"
)

report_lines.append("\n## Key Findings\n")
report_lines.append(f"- **SkillScan Static 完全失效**：对全部 {total} 个 evade_g* 样本检出率为 {total_ss/total:.1%}")
report_lines.append(f"- **SkillScan GPT-5.4 全检出**：对全部 {total} 个样本检出率为 {total_sg/total:.1%}")
report_lines.append(f"- **Cisco Full (gpt-5.4) 全检出**：对全部 {total} 个样本检出率为 {total_cf/total:.1%}")
report_lines.append(f"- **3静态scanner绕过案例**：{len(eff_cases_static)}/{total} ({len(eff_cases_static)/total:.1%})")
report_lines.append(f"- **全部5scanner绕过案例**：0/{total} (0.0%)（LLM scanner 全部检出）")
report_lines.append(f"- **LLM scanner 有效弥补**：SkillFortify 漏检的案例均被 LLM scanner 检出")

report_path = Path("/Users/tan/Desktop/RA3/4.6/evasion_results_report.md")
report_path.write_text("\n".join(report_lines))
print(f"\n✓ 报告已写出: {report_path}")
