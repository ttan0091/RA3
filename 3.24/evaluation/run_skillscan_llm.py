#!/usr/bin/env python3
"""Run SkillScan LLM analyzer (cc_analyzer) against SkillSecBench."""
import json
import os
import subprocess
import sys
from pathlib import Path

PROMPT_FILE = Path("/Users/tan/Desktop/RA3/3.21/MaliciousAgentSkillsBench/code/analyzer/prompts/audit_prompt.txt")
RESULTS_DIR = Path("/Users/tan/Desktop/RA3/3.24/evaluation/skillscan_llm_results")
BENCHMARK_MALICIOUS = Path("/Users/tan/Desktop/RA3/3.24/benchmark/malicious")
BENCHMARK_BENIGN = Path("/Users/tan/Desktop/RA3/3.24/benchmark/benign")

CASES = (
    [f"AP{i:02d}_{v}" for i in range(1, 13) for v in ("orig", "evade")] +
    [f"BEN{i:02d}" for i in range(1, 11)]
)

def get_case_path(name):
    p = BENCHMARK_MALICIOUS / name
    if p.exists(): return p
    p = BENCHMARK_BENIGN / name
    if p.exists(): return p
    return None

def parse_result(raw_output: str) -> dict:
    """Extract JSON from claude -p output."""
    try:
        wrapper = json.loads(raw_output)
        content = wrapper.get("result", raw_output)
    except Exception:
        content = raw_output

    # Try to extract JSON from markdown code blocks
    import re
    match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', content, re.DOTALL | re.IGNORECASE)
    if match:
        try:
            return json.loads(match.group(1))
        except Exception:
            pass

    # Try direct JSON extraction
    s = content.find('{')
    e = content.rfind('}')
    if s != -1 and e != -1:
        try:
            return json.loads(content[s:e+1])
        except Exception:
            pass

    return {"error": "parse_failed", "raw": content[:500]}

def build_user_message(skill_path: Path) -> str:
    """Embed all scannable file contents into the prompt."""
    scan_extensions = {'.md', '.txt', '.py', '.js', '.ts', '.sh', '.bash',
                       '.yml', '.yaml', '.json', '.toml'}
    exclude_dirs = {'.git', '__pycache__', 'node_modules', '.venv', 'venv'}

    lines = [f"Analyze Skill Directory: {skill_path}\n"]
    for fpath in sorted(skill_path.rglob("*")):
        if not fpath.is_file():
            continue
        if any(part in exclude_dirs for part in fpath.parts):
            continue
        if fpath.suffix not in scan_extensions:
            continue
        rel = fpath.relative_to(skill_path)
        try:
            content = fpath.read_text(encoding='utf-8', errors='replace')
        except Exception:
            continue
        lines.append(f"\n--- FILE: {rel} ---\n{content}\n--- END FILE ---")
    return "\n".join(lines)

def analyze_case(name: str, skill_path: Path, prompt: str) -> dict:
    result_file = RESULTS_DIR / f"{name}.json"
    if result_file.exists():
        print(f"  [skip] {name} (already done)")
        return json.loads(result_file.read_text())

    print(f"  [run]  {name} ...", end="", flush=True)
    user_message = build_user_message(skill_path)
    try:
        proc = subprocess.run(
            ["claude", "-p",
             "--output-format", "json",
             "--append-system-prompt", prompt,
             user_message],
            capture_output=True,
            text=True,
            timeout=120
        )
        if proc.returncode != 0:
            result = {"error": "claude_failed", "stderr": proc.stderr[:300]}
        else:
            result = parse_result(proc.stdout)

    except subprocess.TimeoutExpired:
        result = {"error": "timeout"}
    except Exception as e:
        result = {"error": str(e)}

    # Add metadata
    result["_case"] = name
    result["_path"] = str(skill_path)
    result_file.write_text(json.dumps(result, indent=2, ensure_ascii=False))

    status = result.get("audit_summary", {}).get("intent_alignment_status", result.get("error", "?"))
    print(f" {status}")
    return result

def main():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    audit_prompt = PROMPT_FILE.read_text()

    print(f"SkillScan LLM Analyzer — {len(CASES)} cases")
    print("=" * 50)

    results = {}
    for name in CASES:
        path = get_case_path(name)
        if path is None:
            print(f"  [err]  {name}: path not found")
            continue
        results[name] = analyze_case(name, path, audit_prompt)

    # Summary
    print("\n=== Results ===")
    status_map = {}
    for name, r in results.items():
        status = r.get("audit_summary", {}).get("intent_alignment_status")
        if not status:
            status = f"ERROR({r.get('error', '?')})"
        status_map[name] = status

    for name in CASES:
        s = status_map.get(name, "?")
        print(f"  {name:15s}  {s}")

if __name__ == "__main__":
    main()
