#!/usr/bin/env python3
"""
Run Cisco skill-scanner Full (LLM gpt-5.4) on all evade_g* cases.
Uses /v1/responses endpoint directly (bypasses litellm) to match API key quota.
Combines static analysis results with LLM semantic analysis.
"""
import json, os, re, sys, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import requests

SKILL_SCANNER_DIR = Path("/Users/tan/Desktop/RA3/3.21/skill-scanner")
BENCHMARK = Path("/Users/tan/Desktop/RA3/3.24/benchmark/malicious")
OUT_DIR = Path("/Users/tan/Desktop/RA3/3.24/evaluation/cisco_scanner_g/full_gpt54")
STATIC_DIR = Path("/Users/tan/Desktop/RA3/3.24/evaluation/cisco_scanner_g/static")
ENV_FILE = Path("/Users/tan/Desktop/RA3/.env")

PROMPTS_DIR = SKILL_SCANNER_DIR / "skill_scanner" / "data" / "prompts"
THREAT_PROMPT_FILE = PROMPTS_DIR / "skill_threat_analysis_prompt.md"
PROTECTION_RULES_FILE = PROMPTS_DIR / "boilerplate_protection_rule_prompt.md"

OUT_DIR.mkdir(parents=True, exist_ok=True)

MODEL = "gpt-5.4"
CONCURRENCY = 4
TIMEOUT = 180
MAX_OUTPUT_TOKENS = 8000
MAX_RETRIES = 3

SCAN_EXTENSIONS = {".md", ".txt", ".py", ".js", ".ts", ".sh", ".bash", ".yml", ".yaml", ".json", ".toml"}
EXCLUDE_DIRS = {".git", "__pycache__", "node_modules", ".venv", "venv"}


def load_dotenv(path: Path):
    if not path.exists(): return
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line: continue
        k, _, v = line.partition("=")
        os.environ.setdefault(k.strip(), v.strip())


def build_skill_content(skill_path: Path) -> str:
    """Build concatenated skill file content for analysis."""
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


def call_openai_responses(api_key: str, system_prompt: str, user_message: str) -> dict:
    payload = {
        "model": MODEL,
        "input": [
            {"role": "system", "content": [{"type": "input_text", "text": system_prompt}]},
            {"role": "user", "content": [{"type": "input_text", "text": user_message}]},
        ],
        "max_output_tokens": MAX_OUTPUT_TOKENS,
        "reasoning": {"effort": "medium"},
    }
    resp = requests.post(
        "https://api.openai.com/v1/responses",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json=payload,
        timeout=TIMEOUT,
    )
    resp.raise_for_status()
    return resp.json()


def extract_output_text(raw: dict) -> str:
    try:
        for item in raw.get("output", []):
            if item.get("type") == "message":
                for c in item.get("content", []):
                    if c.get("type") == "output_text":
                        return c.get("text", "")
        return ""
    except: return ""


def parse_llm_findings(text: str) -> list:
    """Extract findings list from LLM response."""
    # Try to find JSON block
    m = re.search(r"```(?:json)?\s*(\{.*?\}|\[.*?\])\s*```", text, re.DOTALL | re.IGNORECASE)
    if m:
        try:
            parsed = json.loads(m.group(1))
            if isinstance(parsed, list): return parsed
            if isinstance(parsed, dict): return parsed.get("findings", [])
        except: pass
    # Try raw JSON
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


def is_detected(result: dict) -> bool:
    """Detected if any finding is HIGH or CRITICAL severity."""
    for f in result.get("findings", []):
        if f.get("severity") in ("CRITICAL", "HIGH"):
            return True
    # Also check is_safe flag
    if result.get("is_safe") is False:
        return True
    return False


def analyze_case(name: str, api_key: str, system_prompt: str) -> tuple:
    out = OUT_DIR / f"{name}.json"
    if out.exists():
        data = json.loads(out.read_text())
        if "error" not in data:
            det = data.get("_detected", False)
            print(f"  [skip] {name}: is_safe={data.get('is_safe')} detected={det}")
            return name, data

    skill_path = BENCHMARK / name

    # Load static results if available
    static_data = {}
    static_file = STATIC_DIR / f"{name}.json"
    if static_file.exists():
        static_data = json.loads(static_file.read_text())

    user_msg = build_skill_content(skill_path)
    llm_findings = []
    llm_error = None

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            raw = call_openai_responses(api_key, system_prompt, user_msg)
            text = extract_output_text(raw)
            llm_findings = parse_llm_findings(text)
            break
        except requests.HTTPError as e:
            status = getattr(e.response, "status_code", None)
            llm_error = {"error": "http_error", "status_code": status, "msg": str(e)[:200]}
            if status in {429, 500, 502, 503, 504} and attempt < MAX_RETRIES:
                time.sleep(min(2**attempt, 8)); continue
            break
        except Exception as e:
            llm_error = {"error": type(e).__name__, "message": str(e)[:200]}
            if attempt < MAX_RETRIES:
                time.sleep(min(2**attempt, 8)); continue
            break

    # Merge static + LLM findings
    static_findings = static_data.get("findings", [])
    all_findings = static_findings + llm_findings

    # Determine is_safe: safe only if no HIGH/CRITICAL findings from either
    has_high_critical = any(
        f.get("severity") in ("CRITICAL", "HIGH") for f in all_findings
    )
    is_safe = not has_high_critical

    result = {
        "skill_name": name,
        "is_safe": is_safe,
        "max_severity": (
            "CRITICAL" if any(f.get("severity") == "CRITICAL" for f in all_findings)
            else "HIGH" if any(f.get("severity") == "HIGH" for f in all_findings)
            else "MEDIUM" if any(f.get("severity") == "MEDIUM" for f in all_findings)
            else "LOW" if any(f.get("severity") == "LOW" for f in all_findings)
            else "SAFE"
        ),
        "findings_count": len(all_findings),
        "findings": all_findings,
        "static_findings_count": len(static_findings),
        "llm_findings_count": len(llm_findings),
        "analyzers_used": ["static_analyzer", "llm_analyzer_gpt54"],
        "_case": name,
        "_detected": not is_safe,
    }
    if llm_error:
        result["_llm_error"] = llm_error

    out.write_text(json.dumps(result, indent=2, ensure_ascii=False))
    print(f"  [cisco-full] {name}: is_safe={is_safe} max_sev={result['max_severity']} "
          f"findings={len(all_findings)} (static={len(static_findings)}, llm={len(llm_findings)})"
          + (f" llm_err={llm_error['error']}" if llm_error else ""))
    return name, result


def main():
    load_dotenv(ENV_FILE)
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        print("[error] OPENAI_API_KEY not set"); sys.exit(1)

    # Build system prompt from Cisco scanner prompts
    threat_prompt = THREAT_PROMPT_FILE.read_text() if THREAT_PROMPT_FILE.exists() else "Analyze for security threats."
    protection_rules = PROTECTION_RULES_FILE.read_text() if PROTECTION_RULES_FILE.exists() else ""
    system_prompt = protection_rules.strip() + "\n\n" + threat_prompt.strip() if protection_rules else threat_prompt

    cases = sorted([d.name for d in BENCHMARK.iterdir() if d.is_dir() and "_evade_g" in d.name])
    print(f"Running Cisco Full (gpt-5.4) on {len(cases)} cases (concurrency={CONCURRENCY})...")

    with ThreadPoolExecutor(max_workers=CONCURRENCY) as ex:
        futures = {ex.submit(analyze_case, case, api_key, system_prompt): case for case in cases}
        for f in as_completed(futures):
            try: f.result()
            except Exception as e: print(f"  [err] {futures[f]}: {e}")

    total = len(list(OUT_DIR.glob("*.json")))
    detected = sum(1 for f in OUT_DIR.glob("*.json")
                   if json.loads(f.read_text()).get("_detected"))
    print(f"\n✓ Cisco Full done: {total} results, {detected}/{total} detected")


if __name__ == "__main__":
    main()
