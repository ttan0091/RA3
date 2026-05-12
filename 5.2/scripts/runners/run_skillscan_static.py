#!/usr/bin/env python3
"""Run SkillScan (MaliciousAgentSkillsBench) static over a benchmark directory.

Usage:
    python run_skillscan_static.py BENCH_DIR OUT_DIR
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT_5_2 = Path(__file__).resolve().parents[2]
SS_PROJECT = ROOT_5_2 / "scanners" / "skillscan" / "code" / "scanner" / "skill-security-scan"


def is_detected(result: dict) -> bool:
    issues = result.get("issues", [])
    return any(i.get("severity") in {"CRITICAL", "HIGH"} for i in issues)


def scan_one(skill_dir: Path) -> dict:
    abs_path = str(skill_dir.resolve())
    code = (
        f"import sys, json\n"
        f"sys.path.insert(0, {str(SS_PROJECT)!r})\n"
        f"from src.cli import cli\n"
        f"try:\n"
        f"    cli(['scan', {abs_path!r}, '--format', 'json'], standalone_mode=False)\n"
        f"except SystemExit:\n"
        f"    pass\n"
    )
    proc = subprocess.run(
        ["python3", "-c", code],
        capture_output=True, text=True, timeout=120,
    )
    out = proc.stdout.strip()
    idx = out.find("{")
    if idx == -1:
        return {"error": "no_json", "stdout": out[:300], "stderr": proc.stderr[:300]}
    try:
        return json.loads(out[idx:])
    except json.JSONDecodeError:
        return {"error": "parse_failed", "stdout": out[:300]}


def main(bench_dir: str, out_dir: str) -> None:
    bench = Path(bench_dir)
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    cases = sorted(d for d in bench.iterdir() if d.is_dir())
    print(f"[skillscan-static] scanning {len(cases)} cases from {bench} -> {out}")
    for case in cases:
        target = out / f"{case.name}.json"
        if target.exists():
            print(f"  skip {case.name}")
            continue
        result = scan_one(case)
        result["_case"] = case.name
        result["_detected"] = is_detected(result)
        target.write_text(json.dumps(result, indent=2, ensure_ascii=False))
        n = len(result.get("issues", []))
        print(f"  [{case.name}] issues={n} detected={result['_detected']}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
