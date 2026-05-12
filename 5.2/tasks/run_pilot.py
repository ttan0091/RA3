#!/usr/bin/env python3
"""Pilot experiment: 3 tasks × 7 conditions (S0–S6) × 3 reps.

Measures task success, token consumption, and latency for each condition.
Uses DeepSeek v4-flash via the shared client in scripts/common/deepseek.py.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

ROOT_5_2 = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_5_2 / "scripts"))

from common.deepseek import call, extract_text, get_api_key, ATTACKER_MODEL  # noqa: E402

TASKS_DIR = Path(__file__).resolve().parent
RESULTS_DIR = TASKS_DIR / "results" / "raw"
STYLES = ["S0", "S1", "S2", "S3", "S4", "S5", "S6"]
REPS = 3
MODEL = ATTACKER_MODEL


def load_task(task_dir: Path) -> dict:
    instruction = (task_dir / "task_instruction.txt").read_text()
    input_data = (task_dir / "input.json").read_text()
    expected = json.loads((task_dir / "expected.json").read_text())
    return {
        "instruction": instruction,
        "input_data": input_data,
        "expected": expected,
    }


def load_skill(task_dir: Path, style: str) -> str | None:
    if style == "S0":
        return None
    fname = {
        "S1": "S1_minimal.md",
        "S2": "S2_checklist.md",
        "S3": "S3_narrative.md",
        "S4": "S4_example.md",
        "S5": "S5_code.md",
        "S6": "S6_hybrid.md",
    }[style]
    path = task_dir / fname
    return path.read_text() if path.exists() else None


def build_prompt(task: dict, skill_content: str | None) -> tuple[str, str]:
    user_msg = task["instruction"].replace("{input_data}", task["input_data"])
    if skill_content is None:
        system_msg = "You are a helpful assistant."
    else:
        system_msg = (
            "You are an AI agent. You have the following skill loaded:\n\n"
            + skill_content
        )
    return system_msg, user_msg


def run_one(task_dir: Path, task: dict, style: str, rep: int, api_key: str) -> dict:
    skill = load_skill(task_dir, style)
    system_msg, user_msg = build_prompt(task, skill)

    t_start = time.time()
    raw = call(
        system_msg,
        user_msg,
        model=MODEL,
        temperature=0.0,
        max_tokens=4096,
        api_key=api_key,
    )
    t_end = time.time()

    usage = raw.get("usage", {})
    output = extract_text(raw)

    return {
        "task": task_dir.name,
        "style": style,
        "rep": rep,
        "model": MODEL,
        "prompt_tokens": usage.get("prompt_tokens", 0),
        "completion_tokens": usage.get("completion_tokens", 0),
        "total_tokens": usage.get("total_tokens", 0),
        "latency_ms": round((t_end - t_start) * 1000),
        "output": output,
        "skill_tokens": len(skill.split()) if skill else 0,
    }


def check_t01(output: str, expected: list[dict]) -> dict:
    """Check bonus calculation: extract numbers and compare."""
    results = {}
    for exp in expected:
        eid = exp["id"]
        target = exp["bonus"]
        found = None
        for line in output.split("\n"):
            if eid in line:
                import re
                nums = re.findall(r'"bonus"\s*:\s*(\d+)', line)
                if nums:
                    found = int(nums[0])
                    break
        if found is None:
            import re
            pattern = rf'"{eid}".*?"bonus"\s*:\s*(\d+)'
            m = re.search(pattern, output, re.DOTALL)
            if m:
                found = int(m.group(1))
        results[eid] = {"expected": target, "got": found, "correct": found == target}
    n_correct = sum(1 for v in results.values() if v["correct"])
    return {"score": n_correct / len(expected), "n_correct": n_correct, "n_total": len(expected), "details": results}


def check_t02(output: str, expected: list[dict]) -> dict:
    """Check order classification: exact string match."""
    results = {}
    for exp in expected:
        oid = exp["id"]
        target = exp["classification"]
        found = None
        import re
        pattern = rf'"{oid}".*?"classification"\s*:\s*"([A-Z_]+)"'
        m = re.search(pattern, output, re.DOTALL)
        if m:
            found = m.group(1)
        results[oid] = {"expected": target, "got": found, "correct": found == target}
    n_correct = sum(1 for v in results.values() if v["correct"])
    return {"score": n_correct / len(expected), "n_correct": n_correct, "n_total": len(expected), "details": results}


def check_t03(output: str, expected: list[dict]) -> dict:
    """Check leave approval: decision match."""
    results = {}
    for exp in expected:
        lid = exp["id"]
        target = exp["decision"]
        found = None
        import re
        pattern = rf'"{lid}".*?"decision"\s*:\s*"([A-Z]+)"'
        m = re.search(pattern, output, re.DOTALL)
        if m:
            found = m.group(1)
        results[lid] = {"expected": target, "got": found, "correct": found == target}
    n_correct = sum(1 for v in results.values() if v["correct"])
    return {"score": n_correct / len(expected), "n_correct": n_correct, "n_total": len(expected), "details": results}


CHECKERS = {
    "T01_bonus_calc": check_t01,
    "T02_order_classify": check_t02,
    "T03_leave_approval": check_t03,
}


def main() -> None:
    api_key = get_api_key()
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    task_dirs = sorted(d for d in TASKS_DIR.iterdir()
                       if d.is_dir() and d.name.startswith("T0"))

    print(f"Tasks: {[d.name for d in task_dirs]}")
    print(f"Styles: {STYLES}")
    print(f"Reps: {REPS}")
    print(f"Model: {MODEL}")
    print(f"Total calls: {len(task_dirs) * len(STYLES) * REPS}")
    print()

    all_results = []

    for task_dir in task_dirs:
        task = load_task(task_dir)
        checker = CHECKERS.get(task_dir.name)
        print(f"=== {task_dir.name} ===")

        for style in STYLES:
            for rep in range(REPS):
                result_file = RESULTS_DIR / f"{task_dir.name}_{style}_r{rep}.json"
                if result_file.exists():
                    print(f"  skip {task_dir.name}/{style}/r{rep}")
                    result = json.loads(result_file.read_text())
                    all_results.append(result)
                    continue

                print(f"  {task_dir.name}/{style}/r{rep} ... ", end="", flush=True)
                result = run_one(task_dir, task, style, rep, api_key)

                if checker:
                    check = checker(result["output"], task["expected"])
                    result["check"] = check
                    print(f"tokens={result['total_tokens']} "
                          f"latency={result['latency_ms']}ms "
                          f"score={check['score']:.0%} "
                          f"({check['n_correct']}/{check['n_total']})")
                else:
                    print(f"tokens={result['total_tokens']} latency={result['latency_ms']}ms")

                result_file.write_text(json.dumps(result, indent=2, ensure_ascii=False))
                all_results.append(result)

    print("\n=== Summary ===")
    summary = {}
    for r in all_results:
        key = (r["task"], r["style"])
        if key not in summary:
            summary[key] = {"scores": [], "tokens": [], "latencies": []}
        if "check" in r:
            summary[key]["scores"].append(r["check"]["score"])
        summary[key]["tokens"].append(r["total_tokens"])
        summary[key]["latencies"].append(r["latency_ms"])

    header = f"{'Task':<20} {'Style':<6} {'Success':>8} {'Avg Tokens':>11} {'Avg Latency':>12}"
    print(header)
    print("-" * len(header))
    for (task, style), v in sorted(summary.items()):
        avg_score = sum(v["scores"]) / len(v["scores"]) if v["scores"] else -1
        avg_tok = sum(v["tokens"]) / len(v["tokens"])
        avg_lat = sum(v["latencies"]) / len(v["latencies"])
        score_str = f"{avg_score:.0%}" if avg_score >= 0 else "N/A"
        print(f"{task:<20} {style:<6} {score_str:>8} {avg_tok:>11.0f} {avg_lat:>11.0f}ms")

    summary_file = TASKS_DIR / "results" / "pilot_summary.json"
    summary_out = []
    for (task, style), v in sorted(summary.items()):
        summary_out.append({
            "task": task, "style": style,
            "avg_score": sum(v["scores"]) / len(v["scores"]) if v["scores"] else None,
            "avg_tokens": sum(v["tokens"]) / len(v["tokens"]),
            "avg_latency_ms": sum(v["latencies"]) / len(v["latencies"]),
            "n_reps": len(v["tokens"]),
        })
    summary_file.write_text(json.dumps(summary_out, indent=2))
    print(f"\nSummary saved to {summary_file}")


if __name__ == "__main__":
    main()
