#!/usr/bin/env python3
"""Run Cisco-Full scanner = static + DeepSeek LLM judge.

Static findings come from scanners/cisco; LLM findings come from DeepSeek
(deepseek-v4-pro by default) using the Cisco threat-analysis prompt.

Usage:
    python run_cisco_full.py BENCH_DIR OUT_DIR [STATIC_DIR]
"""
from __future__ import annotations

import json
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT_5_2 = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT_5_2 / "scripts"))
from common import deepseek, skill_io  # noqa: E402

PROMPT_THREAT = ROOT_5_2 / "scripts" / "common" / "cisco_threat_prompt.md"
PROMPT_RULES = ROOT_5_2 / "scripts" / "common" / "cisco_protection_prompt.md"

CONCURRENCY = 4
MAX_TOKENS = 4000


def llm_findings(skill_dir: Path, prompt: str, api_key: str) -> tuple[list[dict], dict]:
    user_msg = skill_io.read_skill(skill_dir)
    raw = deepseek.judge(prompt, user_msg, api_key=api_key, max_tokens=MAX_TOKENS)
    text = deepseek.extract_text(raw)
    parsed = deepseek.parse_json(text)
    findings = parsed.get("findings", []) if isinstance(parsed, dict) else []
    if not isinstance(findings, list):
        findings = []
    return findings, {"_raw_model": raw.get("model"), "_usage": raw.get("usage")}


def llm_only_detected(findings: list[dict]) -> bool:
    return any(f.get("severity") in {"CRITICAL", "HIGH"} for f in findings)


def combined_detected(findings: list[dict]) -> bool:
    return any(f.get("severity") in {"CRITICAL", "HIGH"} for f in findings)


def scan_one(case: Path, static_dir: Path | None, prompt: str, api_key: str) -> dict:
    static_findings: list[dict] = []
    if static_dir is not None:
        sf = static_dir / f"{case.name}.json"
        if sf.exists():
            sd = json.loads(sf.read_text())
            static_findings = sd.get("findings", [])
    try:
        llm, meta = llm_findings(case, prompt, api_key)
    except Exception as e:
        llm = []
        meta = {"_llm_error": f"{type(e).__name__}: {e}"}
    all_findings = static_findings + llm
    return {
        "skill_name": case.name,
        "is_safe": not combined_detected(all_findings),
        "findings": all_findings,
        "findings_count": len(all_findings),
        "static_findings_count": len(static_findings),
        "llm_findings_count": len(llm),
        "_case": case.name,
        "_analyzer": "cisco_full_deepseek",
        "_llm_only_detected": llm_only_detected(llm),
        "_detected": combined_detected(all_findings),
        **meta,
    }


def main(bench_dir: str, out_dir: str, static_dir: str | None = None) -> None:
    bench = Path(bench_dir)
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    sd = Path(static_dir) if static_dir else None

    prompt = PROMPT_THREAT.read_text()
    if PROMPT_RULES.exists():
        prompt = PROMPT_RULES.read_text().strip() + "\n\n" + prompt.strip()

    api_key = deepseek.get_api_key()
    cases = sorted(d for d in bench.iterdir() if d.is_dir())
    print(f"[cisco-full DS={deepseek.JUDGE_MODEL}] scanning {len(cases)} cases")

    todo = []
    for case in cases:
        target = out / f"{case.name}.json"
        if target.exists():
            print(f"  skip {case.name}")
            continue
        todo.append(case)

    with ThreadPoolExecutor(max_workers=CONCURRENCY) as ex:
        futs = {ex.submit(scan_one, case, sd, prompt, api_key): case for case in todo}
        for fut in as_completed(futs):
            case = futs[fut]
            try:
                result = fut.result()
                target = out / f"{case.name}.json"
                target.write_text(json.dumps(result, indent=2, ensure_ascii=False))
                print(f"  [{case.name}] llm_findings={result['llm_findings_count']} "
                      f"detected={result['_detected']} llm_only={result['_llm_only_detected']}")
            except Exception as e:
                print(f"  [{case.name}] ERROR {type(e).__name__}: {e}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    static = sys.argv[3] if len(sys.argv) > 3 else None
    main(sys.argv[1], sys.argv[2], static)
