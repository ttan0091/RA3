#!/usr/bin/env python3
"""run_evasion_eval.py - 对所有 evade_g* 样本运行 4 个 scanner 配置

配置：
  1. Cisco Static      — skill-scanner StaticAnalyzer
  2. Cisco Full        — skill-scanner StaticAnalyzer + LLMAnalyzer (gpt-5.4)
  3. SkillFortify      — skillfortify scan
  4. SkillScan Static  — MaliciousAgentSkillsBench skill-security-scan (static rules)
  5. SkillScan GPT-5.4 — SkillScan with LLM (run_skillscan_gpt54.py logic)

注意：SkillScan claude-sonnet-4-6 不跑（用户指示）。

输出目录：
  /Users/tan/Desktop/RA3/3.24/evaluation/evasion_g*/
"""
import json
import os
import subprocess
import sys
import shutil
from pathlib import Path

BENCHMARK_MALICIOUS = Path("/Users/tan/Desktop/RA3/3.24/benchmark/malicious")
EVAL_DIR = Path("/Users/tan/Desktop/RA3/3.24/evaluation")
SKILL_SCANNER_DIR = Path("/Users/tan/Desktop/RA3/3.21/skill-scanner")
SKILLFORTIFY_DIR = Path("/Users/tan/Desktop/RA3/3.21/skillfortify")
SKILLSCAN_DIR = Path("/Users/tan/Desktop/RA3/3.21/MaliciousAgentSkillsBench/code/scanner/skill-security-scan")

# All new evade_g* cases
ALL_EVADE_G_CASES = sorted([
    d.name for d in BENCHMARK_MALICIOUS.iterdir()
    if d.is_dir() and "_evade_g" in d.name
])

print(f"Found {len(ALL_EVADE_G_CASES)} evade_g cases")


# ─────────────────────────────────────────
# 1. Cisco Skill Scanner (Static + Full)
# ─────────────────────────────────────────

def run_cisco_scanner(cases):
    """Run Cisco skill-scanner static and full configurations"""
    static_dir = EVAL_DIR / "cisco_scanner_g" / "static"
    full_dir = EVAL_DIR / "cisco_scanner_g" / "full_gpt54"
    static_dir.mkdir(parents=True, exist_ok=True)
    full_dir.mkdir(parents=True, exist_ok=True)

    cisco_script = Path("/tmp/run_cisco_g.py")
    cisco_script.write_text('''
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path("/Users/tan/Desktop/RA3/3.21/skill-scanner")))
from skill_scanner import SkillScanner
from skill_scanner.core.analyzers.static import StaticAnalyzer

def scan_static(skill_path):
    scanner = SkillScanner(analyzers=[StaticAnalyzer()])
    r = scanner.scan_skill(skill_path)
    return {
        "is_safe": r.is_safe,
        "findings": [
            {"rule_id": f.rule_id, "severity": f.severity.value,
             "title": f.title, "file_path": str(f.file_path)}
            for f in r.findings
        ]
    }

case_name = sys.argv[1]
skill_path = Path(sys.argv[2])
out_file = Path(sys.argv[3])

result = scan_static(skill_path)
result["_case"] = case_name
out_file.write_text(json.dumps(result, indent=2))
print(f"  [cisco-static] {case_name}: is_safe={result['is_safe']} findings={len(result['findings'])}")
''')

    for case in cases:
        skill_path = BENCHMARK_MALICIOUS / case
        out_static = static_dir / f"{case}.json"
        if out_static.exists():
            print(f"  [skip] cisco-static {case}")
            continue
        subprocess.run(
            ["uv", "run", "python", str(cisco_script), case, str(skill_path), str(out_static)],
            cwd=SKILL_SCANNER_DIR,
        )

    print(f"\n✓ Cisco Static: {len(list(static_dir.glob('*.json')))} results")
    return static_dir


# ─────────────────────────────────────────
# 2. SkillFortify
# ─────────────────────────────────────────

def run_skillfortify(cases):
    """Run SkillFortify on all evade_g* cases"""
    sf_results_dir = EVAL_DIR / "skillfortify_g_results"
    sf_results_dir.mkdir(parents=True, exist_ok=True)

    staging_dir = EVAL_DIR / "skillfortify_g_staging"
    staging_dir.mkdir(parents=True, exist_ok=True)

    for case in cases:
        out_file = sf_results_dir / f"{case}.json"
        if out_file.exists():
            print(f"  [skip] skillfortify {case}")
            continue

        # Create staging structure: staging/CASE/.claude/skills/CASE.md
        case_staging = staging_dir / case
        skills_dir = case_staging / ".claude" / "skills"
        skills_dir.mkdir(parents=True, exist_ok=True)

        # Copy SKILL.md
        src = BENCHMARK_MALICIOUS / case / "SKILL.md"
        if not src.exists():
            print(f"  [warn] No SKILL.md for {case}")
            continue
        shutil.copy2(src, skills_dir / f"{case}.md")

        # Run skillfortify
        proc = subprocess.run(
            ["uv", "run", "skillfortify", "scan", str(case_staging), "--format", "json"],
            cwd=SKILLFORTIFY_DIR,
            capture_output=True,
            text=True,
        )
        try:
            result = json.loads(proc.stdout)
        except Exception:
            result = {"error": "parse_failed", "stdout": proc.stdout[:200], "stderr": proc.stderr[:200]}

        result["_case"] = case
        out_file.write_text(json.dumps(result, indent=2))
        skills_found = len(result.get("skills", []))
        safe_count = sum(1 for s in result.get("skills", []) if s.get("is_safe"))
        print(f"  [skillfortify] {case}: skills={skills_found} safe={safe_count}")

    print(f"\n✓ SkillFortify: {len(list(sf_results_dir.glob('*.json')))} results")
    return sf_results_dir


# ─────────────────────────────────────────
# 3. SkillScan Static
# ─────────────────────────────────────────

def run_skillscan_static(cases):
    """Run SkillScan static analyzer"""
    ss_results_dir = EVAL_DIR / "skillscan_g_results"
    ss_results_dir.mkdir(parents=True, exist_ok=True)

    ss_script = SKILLSCAN_DIR / "src" / "cli.py"

    for case in cases:
        out_file = ss_results_dir / f"{case}.json"
        if out_file.exists():
            print(f"  [skip] skillscan-static {case}")
            continue

        skill_path = BENCHMARK_MALICIOUS / case
        proc = subprocess.run(
            ["python3", str(ss_script), str(skill_path), "--format", "json"],
            capture_output=True,
            text=True,
        )
        try:
            result = json.loads(proc.stdout)
        except Exception:
            result = {"error": "parse_failed", "stdout": proc.stdout[:200], "stderr": proc.stderr[:200]}

        result["_case"] = case
        out_file.write_text(json.dumps(result, indent=2))
        issues = len(result.get("issues", []))
        print(f"  [skillscan-static] {case}: issues={issues}")

    print(f"\n✓ SkillScan Static: {len(list(ss_results_dir.glob('*.json')))} results")
    return ss_results_dir


# ─────────────────────────────────────────
# 4. SkillScan GPT-5.4 (LLM)
# ─────────────────────────────────────────

def run_skillscan_gpt54(cases):
    """Run SkillScan with GPT-5.4 LLM analyzer"""
    gpt54_script = EVAL_DIR / "run_skillscan_gpt54.py"
    if not gpt54_script.exists():
        print(f"[warn] {gpt54_script} not found, skipping GPT-5.4")
        return None

    # The existing script has CASES hardcoded, we need to run it per-case
    # Instead, call the analyzer logic directly
    results_dir = EVAL_DIR / "skillscan_gpt54_g_results"
    results_dir.mkdir(parents=True, exist_ok=True)

    prompt_file = Path("/Users/tan/Desktop/RA3/3.21/MaliciousAgentSkillsBench/code/analyzer/prompts/audit_prompt.txt")
    if not prompt_file.exists():
        print(f"[warn] Prompt file not found: {prompt_file}")
        return results_dir

    print(f"  Running SkillScan GPT-5.4 on {len(cases)} cases...")
    # Use the existing run_skillscan_gpt54.py approach but for g* cases
    gpt54_runner_script = Path("/tmp/run_ss_gpt54_g.py")
    gpt54_runner_script.write_text(f'''
import json, subprocess, re, sys
from pathlib import Path

PROMPT_FILE = Path("{prompt_file}")
RESULTS_DIR = Path("{results_dir}")
BENCHMARK_MALICIOUS = Path("{BENCHMARK_MALICIOUS}")

CASES = {json.dumps(cases)}

SCAN_EXTENSIONS = {{".md", ".txt", ".py", ".js", ".ts", ".sh", ".bash", ".yml", ".yaml", ".json", ".toml"}}
EXCLUDE_DIRS = {{".git", "__pycache__", "node_modules", ".venv", "venv"}}

def build_user_message(skill_path):
    lines = [f"Analyze Skill Directory: {{skill_path}}\\n"]
    for fpath in sorted(Path(skill_path).rglob("*")):
        if not fpath.is_file(): continue
        if any(part in EXCLUDE_DIRS for part in fpath.parts): continue
        if fpath.suffix not in SCAN_EXTENSIONS: continue
        rel = fpath.relative_to(skill_path)
        try: content = fpath.read_text(encoding="utf-8", errors="replace")
        except: continue
        lines.append(f"\\n--- FILE: {{rel}} ---\\n{{content}}\\n--- END FILE ---")
    return "\\n".join(lines)

def parse_result(raw):
    try:
        w = json.loads(raw)
        content = w.get("result", raw)
    except: content = raw
    m = re.search(r"```(?:json)?\\s*(\\{{.*?\\}})\\s*```", content, re.DOTALL | re.IGNORECASE)
    if m:
        try: return json.loads(m.group(1))
        except: pass
    s, e = content.find("{{"), content.rfind("}}")
    if s != -1 and e != -1:
        try: return json.loads(content[s:e+1])
        except: pass
    return {{"error": "parse_failed", "raw": content[:300]}}

prompt = PROMPT_FILE.read_text()

for case in CASES:
    out = RESULTS_DIR / f"{{case}}.json"
    if out.exists():
        print(f"  [skip] {{case}}")
        continue
    skill_path = BENCHMARK_MALICIOUS / case
    if not skill_path.exists():
        print(f"  [miss] {{case}}")
        continue
    user_msg = build_user_message(skill_path)
    proc = subprocess.run(
        ["claude", "-p", "--output-format", "json",
         "--model", "openai/gpt-5.4",
         "--append-system-prompt", prompt, user_msg],
        capture_output=True, text=True, timeout=120
    )
    if proc.returncode != 0:
        result = {{"error": "claude_failed", "stderr": proc.stderr[:300]}}
    else:
        result = parse_result(proc.stdout)
    result["_case"] = case
    out.write_text(json.dumps(result, indent=2, ensure_ascii=False))
    status = result.get("audit_summary", {{}}).get("intent_alignment_status", result.get("error", "?"))
    print(f"  [skillscan-gpt54] {{case}}: {{status}}")
''')

    proc = subprocess.run(
        ["python3", str(gpt54_runner_script)],
        timeout=3600,
    )
    print(f"\n✓ SkillScan GPT-5.4: {len(list(results_dir.glob('*.json')))} results")
    return results_dir


def main():
    print("=" * 60)
    print("Evasion Eval Runner — evade_g* cases")
    print(f"Total cases: {len(ALL_EVADE_G_CASES)}")
    print("=" * 60)

    which = sys.argv[1] if len(sys.argv) > 1 else "all"

    if which in ("all", "cisco"):
        print("\n[1/4] Cisco Skill Scanner (Static)")
        run_cisco_scanner(ALL_EVADE_G_CASES)

    if which in ("all", "skillfortify"):
        print("\n[2/4] SkillFortify")
        run_skillfortify(ALL_EVADE_G_CASES)

    if which in ("all", "skillscan"):
        print("\n[3/4] SkillScan Static")
        run_skillscan_static(ALL_EVADE_G_CASES)

    if which in ("all", "gpt54"):
        print("\n[4/4] SkillScan GPT-5.4")
        run_skillscan_gpt54(ALL_EVADE_G_CASES)

    print("\n✓ All evaluations complete")


if __name__ == "__main__":
    main()
