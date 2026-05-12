#!/usr/bin/env python3
"""Analyze codex exec JSONL outputs and check correctness against expected.json."""

import json
import os
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
SANDBOX_ROOT = SCRIPT_DIR / "sandboxes"
RESULTS_DIR = SCRIPT_DIR / "results" / "agent"

TASKS = [
    "T01_bonus_calc", "T02_order_classify", "T03_leave_approval",
    "T04_tax_calc", "T05_inventory_reorder", "T06_student_grade",
    "T07_shipping_cost", "T08_credit_score", "T09_room_booking",
    "T10_expense_review",
]
STYLES = ["S0", "S1", "S2", "S3", "S4", "S5", "S6"]


def load_expected(task: str) -> list[dict]:
    with open(SCRIPT_DIR / task / "expected.json") as f:
        return json.load(f)


def parse_jsonl(path: Path) -> dict:
    """Extract token usage and item count from codex JSONL output."""
    total_input = 0
    total_output = 0
    total_cached = 0
    total_reasoning = 0
    num_turns = 0
    num_commands = 0
    messages = []

    if not path.exists():
        return {}

    for line in path.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            evt = json.loads(line)
        except json.JSONDecodeError:
            continue

        if evt.get("type") == "turn.completed":
            usage = evt.get("usage", {})
            total_input += usage.get("input_tokens", 0)
            total_output += usage.get("output_tokens", 0)
            total_cached += usage.get("cached_input_tokens", 0)
            total_reasoning += usage.get("reasoning_output_tokens", 0)
            num_turns += 1

        if evt.get("type") == "item.completed":
            item = evt.get("item", {})
            if item.get("type") == "command_execution":
                num_commands += 1
            if item.get("type") == "agent_message":
                messages.append(item.get("text", ""))

    return {
        "input_tokens": total_input,
        "output_tokens": total_output,
        "cached_tokens": total_cached,
        "reasoning_tokens": total_reasoning,
        "total_tokens": total_input + total_output,
        "num_turns": num_turns,
        "num_commands": num_commands,
        "messages": messages,
    }


def extract_json_from_messages(messages: list[str]) -> list[dict] | None:
    """Fallback: extract JSON array from agent message text (when file write failed)."""
    for msg in reversed(messages):
        match = re.search(r"```json\s*\n(\[.*?\])\s*\n```", msg, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                continue
        match = re.search(r"(\[\s*\{.*?\}\s*\])", msg, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                continue
    return None


def load_output(task: str, style: str, messages: list[str]) -> list[dict] | None:
    """Load output.json from sandbox, or extract from agent messages as fallback."""
    output_path = SANDBOX_ROOT / f"{task}_{style}" / "output.json"
    if output_path.exists():
        try:
            with open(output_path) as f:
                return json.load(f)
        except (json.JSONDecodeError, ValueError):
            pass
    return extract_json_from_messages(messages)


def check_t01(output: list[dict], expected: list[dict]) -> tuple[int, int]:
    exp_map = {e["id"]: e["bonus"] for e in expected}
    correct = 0
    for item in output:
        eid = item.get("id", "")
        bonus = item.get("bonus")
        if isinstance(bonus, (int, float)) and eid in exp_map:
            if round(bonus) == exp_map[eid]:
                correct += 1
    return correct, len(expected)


def check_t02(output: list[dict], expected: list[dict]) -> tuple[int, int]:
    exp_map = {e["id"]: e["classification"] for e in expected}
    correct = 0
    for item in output:
        oid = item.get("id", "")
        cls = item.get("classification", "").upper().replace(" ", "_")
        if oid in exp_map and cls == exp_map[oid]:
            correct += 1
    return correct, len(expected)


def check_t03(output: list[dict], expected: list[dict]) -> tuple[int, int]:
    exp_map = {e["id"]: e["decision"] for e in expected}
    correct = 0
    for item in output:
        lid = item.get("id", "")
        dec = item.get("decision", "").upper()
        if lid in exp_map and dec == exp_map[lid]:
            correct += 1
    return correct, len(expected)


def check_numeric(output: list[dict], expected: list[dict], key: str, tolerance=0.5) -> tuple[int, int]:
    exp_map = {e["id"]: e[key] for e in expected}
    correct = 0
    for item in output:
        eid = item.get("id", "")
        val = item.get(key)
        if eid in exp_map and val is not None:
            if isinstance(val, (int, float)) and abs(val - exp_map[eid]) <= tolerance:
                correct += 1
    return correct, len(expected)


def check_enum(output: list[dict], expected: list[dict], key: str) -> tuple[int, int]:
    exp_map = {e["id"]: str(e[key]).upper().strip() for e in expected}
    correct = 0
    for item in output:
        eid = item.get("id", "")
        val = str(item.get(key, "")).upper().strip()
        if eid in exp_map and val == exp_map[eid]:
            correct += 1
    return correct, len(expected)


def check_t04(output, expected):
    return check_numeric(output, expected, "tax")

def check_t05(output, expected):
    return check_enum(output, expected, "decision")

def check_t06(output, expected):
    return check_enum(output, expected, "grade")

def check_t07(output, expected):
    return check_numeric(output, expected, "cost", tolerance=0.15)

def check_t08(output, expected):
    return check_numeric(output, expected, "score", tolerance=0.5)

def check_t09(output, expected):
    return check_enum(output, expected, "result")

def check_t10(output, expected):
    return check_enum(output, expected, "result")


CHECKERS = {
    "T01_bonus_calc": check_t01,
    "T02_order_classify": check_t02,
    "T03_leave_approval": check_t03,
    "T04_tax_calc": check_t04,
    "T05_inventory_reorder": check_t05,
    "T06_student_grade": check_t06,
    "T07_shipping_cost": check_t07,
    "T08_credit_score": check_t08,
    "T09_room_booking": check_t09,
    "T10_expense_review": check_t10,
}


def main():
    results = []

    for task in TASKS:
        expected = load_expected(task)
        checker = CHECKERS[task]
        print(f"=== {task} ===")

        for style in STYLES:
            jsonl_path = RESULTS_DIR / f"{task}_{style}.jsonl"
            done_flag = RESULTS_DIR / f"{task}_{style}_done"

            if not done_flag.exists():
                print(f"  {task}/{style} ... NOT RUN")
                continue

            stats = parse_jsonl(jsonl_path)
            if not stats:
                print(f"  {task}/{style} ... NO DATA")
                continue

            output = load_output(task, style, stats.get("messages", []))
            if output is None:
                score_str = "NO OUTPUT"
                correct, total = 0, len(expected)
            else:
                correct, total = checker(output, expected)
                score_str = f"{correct}/{total} ({100*correct//total}%)"

            print(
                f"  {task}/{style} ... "
                f"tokens={stats['total_tokens']} "
                f"(in={stats['input_tokens']}, out={stats['output_tokens']}, "
                f"cached={stats['cached_tokens']}, reason={stats['reasoning_tokens']}) "
                f"turns={stats['num_turns']} cmds={stats['num_commands']} "
                f"score={score_str}"
            )

            results.append({
                "task": task,
                "style": style,
                "input_tokens": stats["input_tokens"],
                "output_tokens": stats["output_tokens"],
                "cached_tokens": stats["cached_tokens"],
                "reasoning_tokens": stats["reasoning_tokens"],
                "total_tokens": stats["total_tokens"],
                "num_turns": stats["num_turns"],
                "num_commands": stats["num_commands"],
                "correct": correct,
                "total": total,
                "score": correct / total if total > 0 else 0,
            })

    # Summary table
    print("\n=== Summary ===")
    print(f"{'Task':<22} {'Style':<8} {'Score':>8} {'Tokens':>10} "
          f"{'In':>8} {'Out':>8} {'Cached':>8} {'Turns':>6} {'Cmds':>6}")
    print("-" * 90)

    for r in results:
        print(
            f"{r['task']:<22} {r['style']:<8} "
            f"{r['score']:>7.0%} {r['total_tokens']:>10} "
            f"{r['input_tokens']:>8} {r['output_tokens']:>8} "
            f"{r['cached_tokens']:>8} {r['num_turns']:>6} {r['num_commands']:>6}"
        )

    # Save JSON
    summary_path = RESULTS_DIR / "agent_summary.json"
    with open(summary_path, "w") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\nSummary saved to {summary_path}")


if __name__ == "__main__":
    main()
