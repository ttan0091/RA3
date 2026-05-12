#!/usr/bin/env python3
"""Aggregate scanner outputs into a single matrix CSV + Markdown report.

Usage:
    python aggregate.py EVAL_ROOT [--out reports/<name>.md]

Reads the 5 scanner subdirectories under EVAL_ROOT and produces:
- a per-case matrix (case × scanner -> D/M/E) CSV
- a per-scanner detection-rate summary
- (optional) per-attack rollup if case names follow `<AP>_<aid>` convention
"""
from __future__ import annotations

import argparse
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

ATTACK_RE = re.compile(r"^(AP\d+)_(.+)$")


def load_one(path: Path) -> dict | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text())
    except Exception:
        return None


def detected_label(d: dict | None) -> str:
    if d is None:
        return "?"
    if d.get("error"):
        return "E"
    return "D" if d.get("_detected") else "M"


def gather(eval_root: Path) -> tuple[list[str], dict[str, dict[str, str]]]:
    """Return (cases, matrix[case][scanner_short] -> label)."""
    case_set: set[str] = set()
    for short, _ in SCANNERS:
        d = eval_root / short
        if d.is_dir():
            for f in d.glob("*.json"):
                case_set.add(f.stem)
    cases = sorted(case_set)
    matrix: dict[str, dict[str, str]] = {}
    for case in cases:
        row = {}
        for key, label in SCANNERS:
            res = load_one(eval_root / key / f"{case}.json")
            row[label] = detected_label(res)
        matrix[case] = row
    return cases, matrix


def per_scanner_rates(cases: list[str], matrix: dict[str, dict[str, str]]) -> dict[str, dict]:
    out = {}
    for _, label in SCANNERS:
        d = sum(1 for c in cases if matrix[c][label] == "D")
        m = sum(1 for c in cases if matrix[c][label] == "M")
        e = sum(1 for c in cases if matrix[c][label] == "E")
        n = d + m + e
        out[label] = {
            "n": n,
            "detected": d,
            "missed": m,
            "errors": e,
            "detect_rate": (d / n) if n else 0.0,
            "miss_rate": (m / n) if n else 0.0,
        }
    return out


def per_attack_rollup(cases: list[str], matrix: dict[str, dict[str, str]]) -> dict[str, dict]:
    """Group cases like AP05_a3 -> attack id 'a3'."""
    by_attack: dict[str, list[str]] = defaultdict(list)
    for c in cases:
        m = ATTACK_RE.match(c)
        if not m:
            continue
        ap, aid = m.group(1), m.group(2)
        # baselines use _orig / _evade, real attacks use lowercase aN
        if aid in ("orig", "evade") or aid.startswith("evade_g"):
            continue
        by_attack[aid].append(c)
    rollup = {}
    for aid, group in by_attack.items():
        scanner_stats = {}
        for _, label in SCANNERS:
            d = sum(1 for c in group if matrix[c][label] == "D")
            m = sum(1 for c in group if matrix[c][label] == "M")
            scanner_stats[label] = {"detected": d, "missed": m, "n": len(group),
                                    "miss_rate": m / len(group)}
        all_llm_missed = sum(
            1 for c in group
            if matrix[c]["Cisco-F"] == "M" and matrix[c]["SS-LLM"] == "M"
        )
        all_5_missed = sum(
            1 for c in group
            if all(matrix[c][label] == "M" for _, label in SCANNERS)
        )
        rollup[aid] = {
            "n": len(group),
            "by_scanner": scanner_stats,
            "all_llm_missed": all_llm_missed,
            "all_5_missed": all_5_missed,
        }
    return rollup


def write_csv(out_path: Path, cases: list[str], matrix: dict[str, dict[str, str]]) -> None:
    with out_path.open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["case"] + [label for _, label in SCANNERS])
        for c in cases:
            w.writerow([c] + [matrix[c][label] for _, label in SCANNERS])


def write_markdown(out_path: Path, eval_root: Path, cases: list[str],
                   matrix: dict[str, dict[str, str]],
                   rates: dict[str, dict],
                   attack_rollup: dict[str, dict]) -> None:
    lines = [f"# Scanner matrix: `{eval_root}`", ""]

    lines += ["## Per-case matrix", "",
              "| case | " + " | ".join(label for _, label in SCANNERS) + " |",
              "|---" * (len(SCANNERS) + 1) + "|"]
    for c in cases:
        lines.append("| " + c + " | " +
                     " | ".join(matrix[c][label] for _, label in SCANNERS) + " |")

    lines += ["", "## Per-scanner detection rate", "",
              "| scanner | detected | missed | errors | detect rate | miss rate |",
              "|---|---:|---:|---:|---:|---:|"]
    for _, label in SCANNERS:
        r = rates[label]
        lines.append(f"| {label} | {r['detected']} | {r['missed']} | {r['errors']} | "
                     f"{100*r['detect_rate']:.1f}% | {100*r['miss_rate']:.1f}% |")

    if attack_rollup:
        lines += ["", "## Per-attack roll-up", "",
                  "| attack | N | Cisco-F miss | SS-LLM miss | both LLM miss | all 5 miss |",
                  "|---|---:|---:|---:|---:|---:|"]
        for aid, r in sorted(attack_rollup.items()):
            cf_miss = r["by_scanner"]["Cisco-F"]["missed"]
            ss_miss = r["by_scanner"]["SS-LLM"]["missed"]
            lines.append(f"| {aid} | {r['n']} | {cf_miss}/{r['n']} | "
                         f"{ss_miss}/{r['n']} | {r['all_llm_missed']}/{r['n']} | "
                         f"{r['all_5_missed']}/{r['n']} |")

    lines += ["",
              "**Legend**: `D` = detected (HIGH/CRITICAL finding or MALICIOUS verdict); "
              "`M` = missed; `E` = scanner error; `?` = no result.", ""]
    out_path.write_text("\n".join(lines))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("eval_root")
    parser.add_argument("--out", default=None)
    args = parser.parse_args()

    eval_root = Path(args.eval_root).resolve()
    out = Path(args.out) if args.out else (
        ROOT_5_2 / "reports" / f"{eval_root.name}.md"
    )
    csv_out = out.with_suffix(".csv")
    out.parent.mkdir(parents=True, exist_ok=True)

    cases, matrix = gather(eval_root)
    rates = per_scanner_rates(cases, matrix)
    rollup = per_attack_rollup(cases, matrix)

    write_csv(csv_out, cases, matrix)
    write_markdown(out, eval_root, cases, matrix, rates, rollup)
    print(f"  wrote {out}")
    print(f"  wrote {csv_out}")
    print(f"  cases={len(cases)}")
    for _, label in SCANNERS:
        r = rates[label]
        print(f"    {label}: detect {r['detected']}/{r['n']} ({100*r['detect_rate']:.1f}%) "
              f"miss {r['missed']}/{r['n']}")


if __name__ == "__main__":
    main()
