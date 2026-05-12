#!/usr/bin/env python3
"""Run SkillScan LLM judge using DeepSeek (deepseek-v4-pro by default).

Usage:
    python run_skillscan_llm.py BENCH_DIR OUT_DIR
"""
from __future__ import annotations

import json
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT_5_2 = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT_5_2 / "scripts"))
from common import deepseek, skill_io  # noqa: E402

PROMPT_FILE = ROOT_5_2 / "scripts" / "common" / "skillscan_audit_prompt.txt"

CONCURRENCY = 4
MAX_TOKENS = 4000


def is_detected(result: dict) -> bool:
    status = result.get("audit_summary", {}).get("intent_alignment_status", "")
    if status in {"MALICIOUS", "MISALIGNED", "SUSPICIOUS"}:
        return True
    for v in result.get("vulnerabilities", []):
        if v.get("risk_level") in {"CRITICAL", "HIGH", "MEDIUM"}:
            return True
    return False


def scan_one(case: Path, prompt: str, api_key: str) -> dict:
    user_msg = skill_io.read_skill(case, header=f"Analyze Skill Directory: {case}\n")
    try:
        raw = deepseek.judge(prompt, user_msg, api_key=api_key, max_tokens=MAX_TOKENS)
        text = deepseek.extract_text(raw)
        result = deepseek.parse_json(text)
        if not isinstance(result, dict):
            result = {"_parse_failed": True}
        result["_raw_model"] = raw.get("model")
        result["_usage"] = raw.get("usage")
    except Exception as e:
        result = {"error": type(e).__name__, "message": str(e)[:300]}
    result["_case"] = case.name
    result["_analyzer"] = "skillscan_deepseek"
    result["_detected"] = is_detected(result)
    return result


def main(bench_dir: str, out_dir: str) -> None:
    bench = Path(bench_dir)
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    prompt = PROMPT_FILE.read_text()
    api_key = deepseek.get_api_key()
    cases = sorted(d for d in bench.iterdir() if d.is_dir())
    print(f"[skillscan-llm DS={deepseek.JUDGE_MODEL}] scanning {len(cases)} cases")

    todo = [c for c in cases if not (out / f"{c.name}.json").exists()]
    for c in cases:
        if c not in todo:
            print(f"  skip {c.name}")

    with ThreadPoolExecutor(max_workers=CONCURRENCY) as ex:
        futs = {ex.submit(scan_one, case, prompt, api_key): case for case in todo}
        for fut in as_completed(futs):
            case = futs[fut]
            try:
                result = fut.result()
                target = out / f"{case.name}.json"
                target.write_text(json.dumps(result, indent=2, ensure_ascii=False))
                status = result.get("audit_summary", {}).get("intent_alignment_status", "?")
                print(f"  [{case.name}] status={status} detected={result['_detected']}")
            except Exception as e:
                print(f"  [{case.name}] ERROR {type(e).__name__}: {e}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
