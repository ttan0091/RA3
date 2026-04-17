#!/usr/bin/env python3
"""Run SkillFortify on all evade_g* cases"""
import json, shutil, subprocess
from pathlib import Path

BENCHMARK = Path("/Users/tan/Desktop/RA3/3.24/benchmark/malicious")
SF_DIR = Path("/Users/tan/Desktop/RA3/3.21/skillfortify")
OUT_DIR = Path("/Users/tan/Desktop/RA3/3.24/evaluation/skillfortify_g_results")
STAGING = Path("/Users/tan/Desktop/RA3/3.24/evaluation/skillfortify_g_staging")

OUT_DIR.mkdir(parents=True, exist_ok=True)
STAGING.mkdir(parents=True, exist_ok=True)

CASES = sorted([d.name for d in BENCHMARK.iterdir() if d.is_dir() and "_evade_g" in d.name])
print(f"Running SkillFortify on {len(CASES)} cases...")

def is_detected(skills):
    """Any skill with is_safe=False is detected"""
    return any(not s.get("is_safe", True) for s in skills)

for case in CASES:
    out = OUT_DIR / f"{case}.json"
    if out.exists():
        print(f"  [skip] {case}")
        continue

    src = BENCHMARK / case / "SKILL.md"
    if not src.exists():
        print(f"  [warn] no SKILL.md for {case}")
        continue

    # Set up staging directory
    staging = STAGING / case
    skills_dir = staging / ".claude" / "skills"
    skills_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, skills_dir / f"{case}.md")

    proc = subprocess.run(
        ["uv", "run", "skillfortify", "scan", str(staging), "--format", "json"],
        cwd=SF_DIR, capture_output=True, text=True,
    )
    try:
        raw = json.loads(proc.stdout)
    except Exception:
        raw = {"error": "parse_failed", "stdout": proc.stdout[:300], "stderr": proc.stderr[:200]}

    # raw may be {"skills": [...], "summary": "..."} or a list
    if isinstance(raw, list):
        result = {"skills": raw, "_case": case}
    elif isinstance(raw, dict):
        result = raw
        result["_case"] = case
    else:
        result = {"error": "unexpected_type", "_case": case}

    skills = result.get("skills", [])
    detected = is_detected(skills)
    result["_detected"] = detected

    out.write_text(json.dumps(result, indent=2))
    print(f"  [skillfortify] {case}: skills={len(skills)} detected={detected}")

print(f"\n✓ SkillFortify done: {len(list(OUT_DIR.glob('*.json')))} results")
