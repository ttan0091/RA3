#!/usr/bin/env python3
"""run_scanners_ds.py - 跑 Cisco Full + SkillScan 在 52 个样本上（DeepSeek-v4-flash）

输出：
  evaluation/cisco_full_ds/<case>.json
  evaluation/skillscan_ds/<case>.json
  evaluation/cisco_static/<case>.json (复用)
"""
import json
import os
import re
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import requests

ROOT = Path("/Users/tan/Desktop/RA3/4.6/long_skills")
BENIGN_DIR = ROOT / "benchmark" / "benign"
MAL_DIR = ROOT / "benchmark" / "malicious"
EVAL_DIR = ROOT / "evaluation"

CISCO_FULL_OUT = EVAL_DIR / "cisco_full_ds"
CISCO_STATIC_OUT = EVAL_DIR / "cisco_static"
SS_OUT = EVAL_DIR / "skillscan_ds"

CISCO_FULL_OUT.mkdir(parents=True, exist_ok=True)
CISCO_STATIC_OUT.mkdir(parents=True, exist_ok=True)
SS_OUT.mkdir(parents=True, exist_ok=True)

ENV_FILE = Path("/Users/tan/Desktop/RA3/.env")
SKILL_SCANNER_DIR = Path("/Users/tan/Desktop/RA3/3.21/skill-scanner")
SS_PROMPT_FILE = Path("/Users/tan/Desktop/RA3/3.21/MaliciousAgentSkillsBench/code/analyzer/prompts/audit_prompt.txt")

CISCO_PROMPT_DIR = SKILL_SCANNER_DIR / "skill_scanner" / "data" / "prompts"
CISCO_THREAT_PROMPT = CISCO_PROMPT_DIR / "skill_threat_analysis_prompt.md"
CISCO_PROTECTION_RULES = CISCO_PROMPT_DIR / "boilerplate_protection_rule_prompt.md"

MODEL = "deepseek-chat"
CONCURRENCY = 8
TIMEOUT = 240
MAX_OUTPUT_TOKENS = 8000
MAX_RETRIES = 3

SCAN_EXTENSIONS = {".md", ".txt", ".py", ".js", ".ts", ".sh", ".bash",
                   ".yml", ".yaml", ".json", ".toml"}
EXCLUDE_DIRS = {".git", "__pycache__", "node_modules", ".venv", "venv"}


def load_dotenv(path):
    if not path.exists(): return
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line: continue
        k, _, v = line.partition("=")
        os.environ[k.strip()] = v.strip()


def list_cases():
    cases = []
    for d in sorted(BENIGN_DIR.iterdir()):
        if d.is_dir():
            cases.append((f"BEN__{d.name}", "benign", d))
    for d in sorted(MAL_DIR.iterdir()):
        if d.is_dir():
            cases.append((f"MAL__{d.name}", "malicious", d))
    return cases


def build_skill_content(skill_path):
    lines = [f"# Skill Directory: {skill_path.name}\n"]
    for fpath in sorted(skill_path.rglob("*")):
        if not fpath.is_file(): continue
        if any(part in EXCLUDE_DIRS for part in fpath.parts): continue
        if fpath.suffix not in SCAN_EXTENSIONS: continue
        rel = fpath.relative_to(skill_path)
        try: content = fpath.read_text(encoding="utf-8", errors="replace")
        except: continue
        lines.append(f"\n--- FILE: {rel} ---\n{content}\n--- END FILE ---")
    return "\n".join(lines)


def call_deepseek(api_key, base_url, system_prompt, user_message, max_tokens=MAX_OUTPUT_TOKENS):
    url = base_url.rstrip("/") + "/chat/completions"
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        "max_tokens": max_tokens,
        "temperature": 0.2,
    }
    resp = requests.post(url,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json=payload, timeout=TIMEOUT)
    resp.raise_for_status()
    return resp.json()


def extract_text(raw):
    try:
        return raw["choices"][0]["message"]["content"] or ""
    except Exception:
        return ""


def parse_findings_array(text):
    m = re.search(r"```(?:json)?\s*(\{.*?\}|\[.*?\])\s*```", text, re.DOTALL | re.IGNORECASE)
    if m:
        try:
            parsed = json.loads(m.group(1))
            if isinstance(parsed, list): return parsed
            if isinstance(parsed, dict): return parsed.get("findings", [])
        except: pass
    s, e = text.find("{"), text.rfind("}")
    if s != -1 and e != -1:
        try:
            parsed = json.loads(text[s:e+1])
            return parsed.get("findings", [])
        except: pass
    s, e = text.find("["), text.rfind("]")
    if s != -1 and e != -1:
        try: return json.loads(text[s:e+1])
        except: pass
    return []


def parse_ss_json(text):
    m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL | re.IGNORECASE)
    if m:
        try: return json.loads(m.group(1))
        except: pass
    s, e = text.find("{"), text.rfind("}")
    if s != -1 and e != -1:
        try: return json.loads(text[s:e+1])
        except: pass
    return {"error": "parse_failed", "raw": text[:500]}


def run_cisco_static_one(case_id, skill_dir):
    out = CISCO_STATIC_OUT / f"{case_id}.json"
    if out.exists():
        return json.loads(out.read_text())
    cisco_script = Path("/tmp/_cisco_static_one.py")
    cisco_script.write_text('''
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path("/Users/tan/Desktop/RA3/3.21/skill-scanner")))
from skill_scanner import SkillScanner
from skill_scanner.core.analyzers.static import StaticAnalyzer

skill_path = Path(sys.argv[1])
scanner = SkillScanner(analyzers=[StaticAnalyzer()])
r = scanner.scan_skill(skill_path)
out = {
    "is_safe": r.is_safe,
    "findings": [
        {"rule_id": f.rule_id, "severity": f.severity.value,
         "title": f.title, "file_path": str(f.file_path)}
        for f in r.findings
    ]
}
print(json.dumps(out))
''')
    proc = subprocess.run(
        ["uv", "run", "python", str(cisco_script), str(skill_dir)],
        cwd=SKILL_SCANNER_DIR, capture_output=True, text=True, timeout=120)
    try:
        result = json.loads(proc.stdout)
    except Exception:
        result = {"error": "parse_failed", "stdout": proc.stdout[:200], "stderr": proc.stderr[:200]}
    out.write_text(json.dumps(result, indent=2))
    return result


def run_cisco_full_one(case_id, skill_dir, api_key, base_url, system_prompt):
    out = CISCO_FULL_OUT / f"{case_id}.json"
    if out.exists():
        d = json.loads(out.read_text())
        if "_llm_error" not in d:
            return d

    static = run_cisco_static_one(case_id, skill_dir)
    static_findings = static.get("findings", []) if "error" not in static else []

    user_msg = build_skill_content(skill_dir)
    llm_findings, llm_error = [], None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            raw = call_deepseek(api_key, base_url, system_prompt, user_msg)
            llm_findings = parse_findings_array(extract_text(raw))
            break
        except requests.HTTPError as e:
            llm_error = {"error": "http_error",
                         "status_code": getattr(e.response, "status_code", None),
                         "msg": str(e)[:200]}
            if llm_error["status_code"] in {429, 500, 502, 503, 504} and attempt < MAX_RETRIES:
                time.sleep(min(2**attempt, 8)); continue
            break
        except Exception as e:
            llm_error = {"error": type(e).__name__, "message": str(e)[:200]}
            if attempt < MAX_RETRIES:
                time.sleep(min(2**attempt, 8)); continue
            break

    all_findings = static_findings + llm_findings
    has_high = any(f.get("severity") in ("CRITICAL", "HIGH") for f in all_findings)
    max_sev = (
        "CRITICAL" if any(f.get("severity") == "CRITICAL" for f in all_findings)
        else "HIGH" if has_high
        else "MEDIUM" if any(f.get("severity") == "MEDIUM" for f in all_findings)
        else "LOW" if any(f.get("severity") == "LOW" for f in all_findings)
        else "SAFE"
    )
    result = {
        "case_id": case_id,
        "is_safe": not has_high,
        "_detected": has_high,
        "max_severity": max_sev,
        "findings_count": len(all_findings),
        "static_findings_count": len(static_findings),
        "llm_findings_count": len(llm_findings),
        "findings": all_findings,
    }
    if llm_error:
        result["_llm_error"] = llm_error
    out.write_text(json.dumps(result, indent=2, ensure_ascii=False))
    print(f"  [cisco-full] {case_id}: safe={not has_high} sev={max_sev} "
          f"f={len(all_findings)}(s={len(static_findings)},l={len(llm_findings)})"
          + (f" err={llm_error['error']}" if llm_error else ""))
    return result


def run_ss_one(case_id, skill_dir, api_key, base_url, ss_prompt):
    out = SS_OUT / f"{case_id}.json"
    if out.exists():
        d = json.loads(out.read_text())
        if "error" not in d:
            return d

    user_msg = build_skill_content(skill_dir)
    result = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            raw = call_deepseek(api_key, base_url, ss_prompt, user_msg, max_tokens=4000)
            result = parse_ss_json(extract_text(raw))
            break
        except requests.HTTPError as e:
            result = {"error": "http_error",
                      "status_code": getattr(e.response, "status_code", None)}
            if result["status_code"] in {429, 500, 502, 503, 504} and attempt < MAX_RETRIES:
                time.sleep(min(2**attempt, 8)); continue
            break
        except Exception as e:
            result = {"error": type(e).__name__, "message": str(e)[:300]}
            if attempt < MAX_RETRIES:
                time.sleep(min(2**attempt, 8)); continue
            break

    status = result.get("audit_summary", {}).get("intent_alignment_status", "")
    detected = status in ("MALICIOUS", "MISALIGNED", "SUSPICIOUS")
    result["case_id"] = case_id
    result["_detected"] = detected
    out.write_text(json.dumps(result, indent=2, ensure_ascii=False))
    print(f"  [ss-ds] {case_id}: {status or result.get('error', '?')} det={detected}")
    return result


def main():
    load_dotenv(ENV_FILE)
    api_key = os.environ.get("DEEPSEEK_API_KEY", "")
    base_url = os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    if not api_key:
        print("[error] DEEPSEEK_API_KEY not set"); sys.exit(1)

    threat = CISCO_THREAT_PROMPT.read_text() if CISCO_THREAT_PROMPT.exists() else "Analyze for security threats."
    protection = CISCO_PROTECTION_RULES.read_text() if CISCO_PROTECTION_RULES.exists() else ""
    cisco_prompt = (protection.strip() + "\n\n" + threat.strip()) if protection else threat
    ss_prompt = SS_PROMPT_FILE.read_text()

    cases = list_cases()
    print(f"Total cases: {len(cases)} ({sum(1 for _, gt, _ in cases if gt == 'benign')} benign + "
          f"{sum(1 for _, gt, _ in cases if gt == 'malicious')} malicious)")
    print(f"Concurrency: {CONCURRENCY}, Model: {MODEL}, base_url: {base_url}\n")

    which = sys.argv[1] if len(sys.argv) > 1 else "all"

    if which in ("all", "cisco"):
        print("=== Cisco Full (Static + DeepSeek LLM) ===")
        with ThreadPoolExecutor(max_workers=CONCURRENCY) as ex:
            futs = {ex.submit(run_cisco_full_one, cid, sd, api_key, base_url, cisco_prompt): cid
                    for cid, _, sd in cases}
            for f in as_completed(futs):
                try: f.result()
                except Exception as e: print(f"  [err] {futs[f]}: {e}")

    if which in ("all", "ss"):
        print("\n=== SkillScan (DeepSeek) ===")
        with ThreadPoolExecutor(max_workers=CONCURRENCY) as ex:
            futs = {ex.submit(run_ss_one, cid, sd, api_key, base_url, ss_prompt): cid
                    for cid, _, sd in cases}
            for f in as_completed(futs):
                try: f.result()
                except Exception as e: print(f"  [err] {futs[f]}: {e}")

    print("\n✓ Done")


if __name__ == "__main__":
    main()
