#!/usr/bin/env python3
"""Run SkillScan-style LLM analyzer against SkillSecBench using OpenAI gpt-5.4."""
import json
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import requests

PROMPT_FILE = Path("/Users/tan/Desktop/RA3/3.21/MaliciousAgentSkillsBench/code/analyzer/prompts/audit_prompt.txt")
ENV_FILE = Path("/Users/tan/Desktop/RA3/.env")
RESULTS_DIR = Path("/Users/tan/Desktop/RA3/3.24/evaluation/skillscan_gpt54_results")
BENCHMARK_MALICIOUS = Path("/Users/tan/Desktop/RA3/3.24/benchmark/malicious")
BENCHMARK_BENIGN = Path("/Users/tan/Desktop/RA3/3.24/benchmark/benign")

CASES = (
    [f"AP{i:02d}_{v}" for i in range(1, 13) for v in ("orig", "evade")] +
    [f"BEN{i:02d}" for i in range(1, 11)]
)

MODEL = os.getenv("SKILLSCAN_OPENAI_MODEL", "gpt-5.4")
CONCURRENCY = int(os.getenv("SKILLSCAN_OPENAI_CONCURRENCY", str(len(CASES))))
TIMEOUT = int(os.getenv("SKILLSCAN_OPENAI_TIMEOUT_SEC", "180"))
MAX_OUTPUT_TOKENS = int(os.getenv("SKILLSCAN_OPENAI_MAX_OUTPUT_TOKENS", "4000"))
MAX_RETRIES = int(os.getenv("SKILLSCAN_OPENAI_MAX_RETRIES", "3"))


def load_dotenv(path: Path) -> None:
    if not path.exists():
        return
    for raw in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


def get_api_key() -> str:
    load_dotenv(ENV_FILE)
    key = os.getenv("OPENAI_API_KEY", "").strip()
    if not key:
        raise RuntimeError(f"OPENAI_API_KEY not found in env or {ENV_FILE}")
    return key


def get_case_path(name: str):
    p = BENCHMARK_MALICIOUS / name
    if p.exists():
        return p
    p = BENCHMARK_BENIGN / name
    if p.exists():
        return p
    return None


def build_user_message(skill_path: Path) -> str:
    scan_extensions = {
        ".md", ".txt", ".py", ".js", ".ts", ".sh", ".bash",
        ".yml", ".yaml", ".json", ".toml"
    }
    exclude_dirs = {".git", "__pycache__", "node_modules", ".venv", "venv"}

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
            content = fpath.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        lines.append(f"\n--- FILE: {rel} ---\n{content}\n--- END FILE ---")
    return "\n".join(lines)


def extract_output_text(data: dict) -> str:
    if isinstance(data.get("output_text"), str) and data["output_text"].strip():
        return data["output_text"]

    chunks = []
    for item in data.get("output", []):
        if item.get("type") != "message":
            continue
        for content in item.get("content", []):
            if content.get("type") == "output_text":
                text = content.get("text", "")
                if text:
                    chunks.append(text)
    return "\n".join(chunks)


def parse_result(text: str) -> dict:
    try:
        return json.loads(text)
    except Exception:
        pass

    import re
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL | re.IGNORECASE)
    if match:
        try:
            return json.loads(match.group(1))
        except Exception:
            pass

    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        try:
            return json.loads(text[start:end + 1])
        except Exception:
            pass

    return {"error": "parse_failed", "raw": text[:1200]}


def call_openai(api_key: str, system_prompt: str, user_message: str) -> dict:
    payload = {
        "model": MODEL,
        "input": [
            {
                "role": "system",
                "content": [{"type": "input_text", "text": system_prompt}],
            },
            {
                "role": "user",
                "content": [{"type": "input_text", "text": user_message}],
            },
        ],
        "max_output_tokens": MAX_OUTPUT_TOKENS,
        "reasoning": {"effort": "medium"},
        "text": {"verbosity": "medium"},
    }
    resp = requests.post(
        "https://api.openai.com/v1/responses",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=TIMEOUT,
    )
    resp.raise_for_status()
    return resp.json()


def analyze_case(name: str, skill_path: Path, prompt: str, api_key: str) -> tuple[str, dict]:
    result_file = RESULTS_DIR / f"{name}.json"
    if result_file.exists():
        return name, json.loads(result_file.read_text())

    user_message = build_user_message(skill_path)

    result = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            raw = call_openai(api_key, prompt, user_message)
            output_text = extract_output_text(raw)
            result = parse_result(output_text)
            result["_raw_response_id"] = raw.get("id")
            break
        except requests.HTTPError as e:
            status = getattr(e.response, "status_code", None)
            err_text = getattr(e.response, "text", "")[:800]
            result = {"error": "http_error", "status_code": status, "response": err_text}
            if status in {429, 500, 502, 503, 504} and attempt < MAX_RETRIES:
                time.sleep(min(2 ** attempt, 8))
                continue
            break
        except Exception as e:
            result = {"error": type(e).__name__, "message": str(e)[:800]}
            if attempt < MAX_RETRIES:
                time.sleep(min(2 ** attempt, 8))
                continue
            break

    result["_case"] = name
    result["_path"] = str(skill_path)
    result_file.write_text(json.dumps(result, indent=2, ensure_ascii=False))
    return name, result


def main() -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    prompt = PROMPT_FILE.read_text(encoding="utf-8")
    api_key = get_api_key()

    print(f"SkillScan LLM Analyzer via OpenAI — model={MODEL}")
    print(f"Cases={len(CASES)}  Concurrency={CONCURRENCY}")
    print("=" * 60)

    case_paths = []
    for name in CASES:
        path = get_case_path(name)
        if path is None:
            print(f"[err ] {name}: path not found")
            continue
        case_paths.append((name, path))

    results = {}
    with ThreadPoolExecutor(max_workers=CONCURRENCY) as pool:
        future_map = {
            pool.submit(analyze_case, name, path, prompt, api_key): name
            for name, path in case_paths
        }
        for future in as_completed(future_map):
            name = future_map[future]
            try:
                _, result = future.result()
                status = result.get("audit_summary", {}).get(
                    "intent_alignment_status",
                    result.get("error", "?"),
                )
                print(f"[done] {name:15s} {status}")
                results[name] = result
            except Exception as e:
                print(f"[fail] {name:15s} {type(e).__name__}: {e}")

    print("\n=== Summary ===")
    for name in CASES:
        result = results.get(name)
        if result is None:
            result_file = RESULTS_DIR / f"{name}.json"
            if result_file.exists():
                result = json.loads(result_file.read_text())
            else:
                print(f"{name:15s} ?")
                continue
        status = result.get("audit_summary", {}).get("intent_alignment_status")
        if not status:
            status = f"ERROR({result.get('error', '?')})"
        print(f"{name:15s} {status}")


if __name__ == "__main__":
    main()
