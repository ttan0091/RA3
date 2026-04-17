#!/usr/bin/env python3
"""Run SkillScan (MaliciousAgentSkillsBench) static scanner on all evade_g* cases"""
import json, subprocess, sys
from pathlib import Path

BENCHMARK = Path("/Users/tan/Desktop/RA3/3.24/benchmark/malicious")
SS_CLI = Path("/Users/tan/Desktop/RA3/3.21/MaliciousAgentSkillsBench/code/scanner/skill-security-scan/src/cli.py")
OUT_DIR = Path("/Users/tan/Desktop/RA3/3.24/evaluation/skillscan_g_results")

OUT_DIR.mkdir(parents=True, exist_ok=True)

CASES = sorted([d.name for d in BENCHMARK.iterdir() if d.is_dir() and "_evade_g" in d.name])
print(f"Running SkillScan Static on {len(CASES)} cases...")

def is_detected(result):
    issues = result.get("issues", [])
    return any(i.get("severity") in ("HIGH", "CRITICAL") for i in issues)

for case in CASES:
    out = OUT_DIR / f"{case}.json"
    if out.exists():
        print(f"  [skip] {case}")
        continue

    skill_path = BENCHMARK / case
    proc = subprocess.run(
        ["python3", str(SS_CLI), str(skill_path), "--format", "json"],
        capture_output=True, text=True,
    )
    try:
        result = json.loads(proc.stdout)
    except Exception:
        result = {"error": "parse_failed", "stdout": proc.stdout[:200], "stderr": proc.stderr[:200]}

    result["_case"] = case
    result["_detected"] = is_detected(result)
    out.write_text(json.dumps(result, indent=2))

    issues_count = len(result.get("issues", []))
    print(f"  [skillscan-static] {case}: issues={issues_count} detected={result['_detected']}")

print(f"\n✓ SkillScan Static done: {len(list(OUT_DIR.glob('*.json')))} results")
