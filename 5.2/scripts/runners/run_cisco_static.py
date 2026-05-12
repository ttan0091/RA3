#!/usr/bin/env python3
"""Run Cisco skill-scanner (static-only, no LLM) over a benchmark directory.

Usage:
    python run_cisco_static.py BENCH_DIR OUT_DIR
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT_5_2 = Path(__file__).resolve().parents[2]
CISCO_DIR = ROOT_5_2 / "scanners" / "cisco"


def is_detected(result: dict) -> bool:
    if result.get("is_safe") is False:
        return True
    return any(
        f.get("severity") in {"CRITICAL", "HIGH"}
        for f in result.get("findings", [])
    )


def scan_one(skill_dir: Path) -> dict:
    proc = subprocess.run(
        ["uv", "run", "skill-scanner", "scan", str(skill_dir.resolve()),
         "--format", "json"],
        cwd=CISCO_DIR,
        capture_output=True,
        text=True,
        timeout=120,
    )
    out = proc.stdout.strip()
    # cisco prints a header line then JSON; find first '{'
    idx = out.find("{")
    if idx == -1:
        return {"error": "no_json", "stdout": out[:300], "stderr": proc.stderr[:300]}
    try:
        return json.loads(out[idx:])
    except json.JSONDecodeError as e:
        return {"error": "parse_failed", "msg": str(e), "stdout": out[:300]}


def main(bench_dir: str, out_dir: str) -> None:
    bench = Path(bench_dir)
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    cases = sorted(d for d in bench.iterdir() if d.is_dir())
    print(f"[cisco-static] scanning {len(cases)} cases from {bench} -> {out}")
    for case in cases:
        target = out / f"{case.name}.json"
        if target.exists():
            print(f"  skip {case.name}")
            continue
        result = scan_one(case)
        result["_case"] = case.name
        result["_detected"] = is_detected(result)
        target.write_text(json.dumps(result, indent=2, ensure_ascii=False))
        n = len(result.get("findings", []))
        print(f"  [{case.name}] findings={n} detected={result['_detected']}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
