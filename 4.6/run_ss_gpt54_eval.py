#!/usr/bin/env python3
"""Run SkillScan GPT-5.4 on all evade_g* cases (adapts existing run_skillscan_gpt54.py logic)"""
import json, os, re, sys, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import requests

PROMPT_FILE = Path("/Users/tan/Desktop/RA3/3.21/MaliciousAgentSkillsBench/code/analyzer/prompts/audit_prompt.txt")
ENV_FILE = Path("/Users/tan/Desktop/RA3/.env")
RESULTS_DIR = Path("/Users/tan/Desktop/RA3/3.24/evaluation/skillscan_gpt54_g_results")
BENCHMARK_MALICIOUS = Path("/Users/tan/Desktop/RA3/3.24/benchmark/malicious")

RESULTS_DIR.mkdir(parents=True, exist_ok=True)

CASES = sorted([d.name for d in BENCHMARK_MALICIOUS.iterdir() if d.is_dir() and "_evade_g" in d.name])
MODEL = "gpt-5.4"
CONCURRENCY = 8
TIMEOUT = 180
MAX_OUTPUT_TOKENS = 4000
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


def build_user_message(skill_path: Path) -> str:
    lines = [f"Analyze Skill Directory: {skill_path}\n"]
    for fpath in sorted(skill_path.rglob("*")):
        if not fpath.is_file(): continue
        if any(part in EXCLUDE_DIRS for part in fpath.parts): continue
        if fpath.suffix not in SCAN_EXTENSIONS: continue
        rel = fpath.relative_to(skill_path)
        try: content = fpath.read_text(encoding="utf-8", errors="replace")
        except: continue
        lines.append(f"\n--- FILE: {rel} ---\n{content}\n--- END FILE ---")
    return "\n".join(lines)


def call_openai(api_key: str, system_prompt: str, user_message: str) -> dict:
    payload = {
        "model": MODEL,
        "input": [
            {"role": "system", "content": [{"type": "input_text", "text": system_prompt}]},
            {"role": "user", "content": [{"type": "input_text", "text": user_message}]},
        ],
        "max_output_tokens": MAX_OUTPUT_TOKENS,
        "reasoning": {"effort": "medium"},
        "text": {"verbosity": "medium"},
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


def parse_result(text: str) -> dict:
    m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL | re.IGNORECASE)
    if m:
        try: return json.loads(m.group(1))
        except: pass
    s, e = text.find("{"), text.rfind("}")
    if s != -1 and e != -1:
        try: return json.loads(text[s:e+1])
        except: pass
    return {"error": "parse_failed", "raw": text[:500]}


def is_detected(result: dict) -> bool:
    status = result.get("audit_summary", {}).get("intent_alignment_status", "")
    return status in ("MISALIGNED", "SUSPICIOUS")


def analyze_case(name: str, api_key: str, prompt: str) -> tuple:
    out = RESULTS_DIR / f"{name}.json"
    if out.exists():
        r = json.loads(out.read_text())
        print(f"  [skip] {name}: {r.get('audit_summary', {}).get('intent_alignment_status', '?')}")
        return name, r

    skill_path = BENCHMARK_MALICIOUS / name
    user_msg = build_user_message(skill_path)
    result = None

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            raw = call_openai(api_key, prompt, user_msg)
            result = parse_result(extract_output_text(raw))
            result["_raw_response_id"] = raw.get("id")
            break
        except requests.HTTPError as e:
            status = getattr(e.response, "status_code", None)
            result = {"error": "http_error", "status_code": status}
            if status in {429, 500, 502, 503, 504} and attempt < MAX_RETRIES:
                time.sleep(min(2**attempt, 8)); continue
            break
        except Exception as e:
            result = {"error": type(e).__name__, "message": str(e)[:400]}
            if attempt < MAX_RETRIES:
                time.sleep(min(2**attempt, 8)); continue
            break

    result["_case"] = name
    result["_detected"] = is_detected(result)
    out.write_text(json.dumps(result, indent=2, ensure_ascii=False))

    status = result.get("audit_summary", {}).get("intent_alignment_status", result.get("error", "?"))
    print(f"  [skillscan-gpt54] {name}: {status} detected={result['_detected']}")
    return name, result


def main():
    load_dotenv(ENV_FILE)
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        print("[error] OPENAI_API_KEY not set"); sys.exit(1)

    prompt = PROMPT_FILE.read_text()
    print(f"Running SkillScan GPT-5.4 on {len(CASES)} cases (concurrency={CONCURRENCY})...")

    with ThreadPoolExecutor(max_workers=CONCURRENCY) as ex:
        futures = {ex.submit(analyze_case, case, api_key, prompt): case for case in CASES}
        for f in as_completed(futures):
            try: f.result()
            except Exception as e: print(f"  [err] {futures[f]}: {e}")

    print(f"\n✓ SkillScan GPT-5.4 done: {len(list(RESULTS_DIR.glob('*.json')))} results")


if __name__ == "__main__":
    main()
