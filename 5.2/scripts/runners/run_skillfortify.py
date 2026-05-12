#!/usr/bin/env python3
"""Run SkillFortify over a benchmark directory.

Usage:
    python run_skillfortify.py BENCH_DIR OUT_DIR
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT_5_2 = Path(__file__).resolve().parents[2]
SF_DIR = ROOT_5_2 / "scanners" / "skillfortify"


def is_detected(skills: list[dict]) -> bool:
    return any(not s.get("is_safe", True) for s in skills)


def scan_one(skill_dir: Path) -> dict:
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return {"error": "no_skill_md"}
    with tempfile.TemporaryDirectory() as tmp:
        staging = Path(tmp) / "stage"
        skills_dir = staging / ".claude" / "skills"
        skills_dir.mkdir(parents=True, exist_ok=True)
        # SkillFortify expects flat .md files in .claude/skills/
        shutil.copy2(skill_md, skills_dir / f"{skill_dir.name}.md")
        proc = subprocess.run(
            ["uv", "run", "skillfortify", "scan", str(staging), "--format", "json"],
            cwd=SF_DIR,
            capture_output=True,
            text=True,
            timeout=120,
        )
        out = proc.stdout.strip()
        try:
            raw = json.loads(out)
        except Exception:
            return {"error": "parse_failed", "stdout": out[:300], "stderr": proc.stderr[:300]}
        if isinstance(raw, list):
            return {"skills": raw}
        return raw


def main(bench_dir: str, out_dir: str) -> None:
    bench = Path(bench_dir)
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    cases = sorted(d for d in bench.iterdir() if d.is_dir())
    print(f"[skillfortify] scanning {len(cases)} cases from {bench} -> {out}")
    for case in cases:
        target = out / f"{case.name}.json"
        if target.exists():
            print(f"  skip {case.name}")
            continue
        result = scan_one(case)
        result["_case"] = case.name
        skills = result.get("skills", [])
        result["_detected"] = is_detected(skills)
        target.write_text(json.dumps(result, indent=2, ensure_ascii=False))
        print(f"  [{case.name}] skills={len(skills)} detected={result['_detected']}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
