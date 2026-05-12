#!/usr/bin/env python3
"""Build the final L1 evasion report combining baseline + L1 attack matrix.

Reads:
  evaluation/L0_baseline_malicious/{cisco_static,cisco_full,skillfortify,skillscan_static,skillscan_llm}/*.json
  evaluation/L0_baseline_benign/{...}/*.json
  evaluation/L1_single/{...}/*.json
  benchmark/L1_single/<AP>_<aid>/attack.json

Writes:
  reports/L1_final.md         master matrix per attack
  reports/L1_final.csv        per-case D/M/E
  reports/L1_attacks_meta.csv attack_id, ap, baseline_score, best_score, semantic
"""
from __future__ import annotations

import csv
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT_5_2 = Path(__file__).resolve().parents[1]

SCANNERS = [
    ("cisco_static", "Cisco-S"),
    ("cisco_full", "Cisco-F"),
    ("skillfortify", "SF"),
    ("skillscan_static", "SS-S"),
    ("skillscan_llm", "SS-LLM"),
]

ATTACK_RE = re.compile(r"^(AP\d+)_(a\d+)$")


def load(path: Path) -> dict | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text())
    except Exception:
        return None


def label(d: dict | None) -> str:
    if d is None:
        return "?"
    if d.get("error"):
        return "E"
    return "D" if d.get("_detected") else "M"


def gather_matrix(eval_root: Path) -> dict[str, dict[str, str]]:
    """case -> {scanner_short: D/M/E/?}"""
    matrix: dict[str, dict[str, str]] = defaultdict(dict)
    for short, lab in SCANNERS:
        d = eval_root / short
        if not d.is_dir():
            continue
        for f in d.glob("*.json"):
            matrix[f.stem][lab] = label(load(f))
    return matrix


def detection_rate(matrix: dict[str, dict[str, str]]) -> dict[str, dict]:
    cases = list(matrix.keys())
    out = {}
    for _, lab in SCANNERS:
        d = sum(1 for c in cases if matrix[c].get(lab) == "D")
        m = sum(1 for c in cases if matrix[c].get(lab) == "M")
        e = sum(1 for c in cases if matrix[c].get(lab) == "E")
        n = d + m + e
        out[lab] = {"d": d, "m": m, "e": e, "n": n,
                    "rate": d / n if n else 0.0}
    return out


def attack_meta() -> dict[str, dict]:
    """attack_id -> {ap -> attack.json contents}"""
    out: dict[str, dict] = defaultdict(dict)
    for d in (ROOT_5_2 / "benchmark" / "L1_single").glob("AP*_a*"):
        m = ATTACK_RE.match(d.name)
        if not m:
            continue
        ap, aid = m.group(1), m.group(2)
        meta_file = d / "attack.json"
        if meta_file.exists():
            try:
                out[aid][ap] = json.loads(meta_file.read_text())
            except Exception:
                pass
    return out


def build_report() -> None:
    out_dir = ROOT_5_2 / "reports"
    out_dir.mkdir(parents=True, exist_ok=True)

    L0_mal = gather_matrix(ROOT_5_2 / "evaluation" / "L0_baseline_malicious")
    L0_ben = gather_matrix(ROOT_5_2 / "evaluation" / "L0_baseline_benign")
    L1_mat = gather_matrix(ROOT_5_2 / "evaluation" / "L1_single")
    meta = attack_meta()

    L0_rates_mal = detection_rate(L0_mal)
    L0_rates_ben = detection_rate(L0_ben)

    # Per-attack summary
    attack_ids = sorted(meta.keys())
    per_attack: dict[str, dict] = {}
    for aid in attack_ids:
        cases = [f"{ap}_{aid}" for ap in meta[aid].keys()]
        cases = [c for c in cases if c in L1_mat]
        if not cases:
            continue
        scanner_miss: dict[str, int] = {lab: 0 for _, lab in SCANNERS}
        for c in cases:
            for _, lab in SCANNERS:
                if L1_mat[c].get(lab) == "M":
                    scanner_miss[lab] += 1
        all_llm_missed = sum(
            1 for c in cases
            if L1_mat[c].get("Cisco-F") == "M" and L1_mat[c].get("SS-LLM") == "M"
        )
        all5_missed = sum(
            1 for c in cases
            if all(L1_mat[c].get(lab) == "M" for _, lab in SCANNERS)
        )
        sem_full = sum(1 for ap in meta[aid] if
                       (meta[aid][ap].get("semantic_preservation", {}).get("preserved") == "full"))
        per_attack[aid] = {
            "n": len(cases),
            "scanner_miss": scanner_miss,
            "all_llm_missed": all_llm_missed,
            "all5_missed": all5_missed,
            "sem_full": sem_full,
        }

    # Markdown
    lines = []
    lines.append("# 5.2 Skill Detector Evasion — final report")
    lines.append("")
    lines.append("## L0 baseline detection rates")
    lines.append("")
    lines.append("| scanner | malicious detect | benign FPR |")
    lines.append("|---|---:|---:|")
    for _, lab in SCANNERS:
        rm = L0_rates_mal[lab]
        rb = L0_rates_ben[lab]
        lines.append(f"| {lab} | {rm['d']}/{rm['n']} ({100*rm['rate']:.1f}%) | "
                     f"{rb['d']}/{rb['n']} ({100*rb['rate']:.1f}%) |")
    lines.append("")
    lines.append("## L1 attack roll-up (miss = scanner classified as benign)")
    lines.append("")
    lines.append("| attack | N | sem=full | "
                 + " | ".join(f"{lab} miss" for _, lab in SCANNERS)
                 + " | both LLM miss | all 5 miss |")
    lines.append("|---|---:|---:|" + "---:|" * (len(SCANNERS) + 2))
    for aid in sorted(per_attack.keys()):
        r = per_attack[aid]
        miss_cells = " | ".join(
            f"{r['scanner_miss'][lab]}/{r['n']}" for _, lab in SCANNERS
        )
        lines.append(f"| {aid} | {r['n']} | {r['sem_full']}/{r['n']} | "
                     f"{miss_cells} | {r['all_llm_missed']}/{r['n']} | "
                     f"{r['all5_missed']}/{r['n']} |")
    lines.append("")
    lines.append("## L1 per-case matrix")
    lines.append("")
    lines.append("| case | " + " | ".join(lab for _, lab in SCANNERS) + " | semantic |")
    lines.append("|---" * (len(SCANNERS) + 2) + "|")
    for c in sorted(L1_mat.keys()):
        m = ATTACK_RE.match(c)
        sem = "?"
        if m:
            ap, aid = m.group(1), m.group(2)
            sem = (meta.get(aid, {}).get(ap, {})
                   .get("semantic_preservation", {})
                   .get("preserved", "?"))
        lines.append("| " + c + " | "
                     + " | ".join(L1_mat[c].get(lab, "?") for _, lab in SCANNERS)
                     + f" | {sem} |")
    lines.append("")
    lines.append("**Legend**: D = detected; M = missed; E = scanner error; ? = no result.")
    lines.append("")

    md_out = out_dir / "L1_final.md"
    md_out.write_text("\n".join(lines))

    # CSV per-case
    csv_out = out_dir / "L1_final.csv"
    with csv_out.open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["case"] + [lab for _, lab in SCANNERS] + ["semantic"])
        for c in sorted(L1_mat.keys()):
            m = ATTACK_RE.match(c)
            sem = "?"
            if m:
                ap, aid = m.group(1), m.group(2)
                sem = (meta.get(aid, {}).get(ap, {})
                       .get("semantic_preservation", {})
                       .get("preserved", "?"))
            w.writerow([c] + [L1_mat[c].get(lab, "?") for _, lab in SCANNERS] + [sem])

    # CSV per-attack-meta
    meta_csv = out_dir / "L1_attacks_meta.csv"
    with meta_csv.open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["attack_id", "ap", "baseline_score", "best_score",
                    "baseline_n_findings", "best_n_findings", "semantic"])
        for aid in sorted(meta.keys()):
            for ap in sorted(meta[aid].keys()):
                d = meta[aid][ap]
                sem = d.get("semantic_preservation", {}).get("preserved", "?")
                w.writerow([aid, ap,
                            d.get("baseline_score", ""),
                            d.get("best_score", ""),
                            d.get("baseline_n_findings", ""),
                            d.get("best_n_findings", ""),
                            sem])

    print(f"  wrote {md_out}")
    print(f"  wrote {csv_out}")
    print(f"  wrote {meta_csv}")


if __name__ == "__main__":
    build_report()
