#!/usr/bin/env python3
"""Run agent-based skill style experiment using Codex CLI."""

import csv
import json
import os
import subprocess
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
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

TASK_PROMPTS = {
    "T01_bonus_calc": (
        "请读取当前目录下的 input.csv 文件，根据 AGENTS.md 中的奖金计算规则，"
        "计算每位员工的年终奖金。将结果以 JSON 数组格式写入 output.json，"
        "每个元素包含 id 和 bonus 两个字段，bonus 为整数（四舍五入）。"
    ),
    "T02_order_classify": (
        "请读取当前目录下的 input.csv 文件，根据 AGENTS.md 中的订单风控分类规则，"
        "对每笔订单进行风险分类。将结果以 JSON 数组格式写入 output.json，"
        "每个元素包含 id 和 classification 两个字段。"
    ),
    "T03_leave_approval": (
        "请读取当前目录下的 input.csv 文件，根据 AGENTS.md 中的请假审批规则，"
        "对每个请假申请做出审批决定。将结果以 JSON 数组格式写入 output.json，"
        "每个元素包含 id、decision 和 reason 三个字段。"
    ),
    "T04_tax_calc": (
        "请读取当前目录下的 input.csv 文件，根据 AGENTS.md 中的个人所得税计算规则，"
        "计算每位员工的应缴个人所得税。将结果以 JSON 数组格式写入 output.json，"
        "每个元素包含 id 和 tax 两个字段，tax 为整数（四舍五入）。"
    ),
    "T05_inventory_reorder": (
        "请读取当前目录下的 input.csv 文件，根据 AGENTS.md 中的库存补货规则，"
        "判断每个商品是否需要补货并计算补货数量。将结果以 JSON 数组格式写入 output.json，"
        "每个元素包含 id、decision 和 order_qty 三个字段。"
    ),
    "T06_student_grade": (
        "请读取当前目录下的 input.csv 文件，根据 AGENTS.md 中的成绩评定规则，"
        "计算每位学生的最终成绩等级。将结果以 JSON 数组格式写入 output.json，"
        "每个元素包含 id、grade、honor 和 warning 四个字段。"
    ),
    "T07_shipping_cost": (
        "请读取当前目录下的 input.csv 文件，根据 AGENTS.md 中的运费计算规则，"
        "计算每个包裹的运费。将结果以 JSON 数组格式写入 output.json，"
        "每个元素包含 id 和 cost 两个字段，cost 保留一位小数。"
    ),
    "T08_credit_score": (
        "请读取当前目录下的 input.csv 文件，根据 AGENTS.md 中的信用评分规则，"
        "计算每位客户的信用得分和评级。将结果以 JSON 数组格式写入 output.json，"
        "每个元素包含 id、score、tier、max_loan 和 rate 五个字段。"
    ),
    "T09_room_booking": (
        "请读取当前目录下的 input.csv 文件，根据 AGENTS.md 中的会议室预订规则，"
        "审批每个预订请求。将结果以 JSON 数组格式写入 output.json，"
        "每个元素包含 id、result 和 reason 三个字段。"
    ),
    "T10_expense_review": (
        "请读取当前目录下的 input.csv 文件，根据 AGENTS.md 中的报销审核规则，"
        "审核每笔报销申请。将结果以 JSON 数组格式写入 output.json，"
        "每个元素包含 id、result、approved_amount 和 approval_level 四个字段。"
    ),
}


def json_to_csv(json_path: Path, csv_path: Path):
    with open(json_path) as f:
        data = json.load(f)
    if not data:
        return
    keys = list(data[0].keys())
    with open(csv_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        w.writerows(data)


def build_agents_md(task: str, style: str, outfile: Path):
    if style == "S0":
        outfile.write_text(
            "# Instructions\n\nYou are a helpful assistant. Complete the task as requested.\n"
        )
        return

    pattern = list((SCRIPT_DIR / task).glob(f"{style}_*.md"))
    if not pattern:
        raise FileNotFoundError(f"Skill file not found: {SCRIPT_DIR / task / f'{style}_*.md'}")
    import shutil
    shutil.copy2(pattern[0], outfile)


def setup_sandbox(task: str, style: str) -> Path:
    d = SANDBOX_ROOT / f"{task}_{style}"
    d.mkdir(parents=True, exist_ok=True)
    json_to_csv(SCRIPT_DIR / task / "input.json", d / "input.csv")
    build_agents_md(task, style, d / "AGENTS.md")
    (d / "output.json").unlink(missing_ok=True)
    return d


def run_one(task: str, style: str) -> dict:
    done_flag = RESULTS_DIR / f"{task}_{style}_done"
    if done_flag.exists():
        return {"task": task, "style": style, "status": "skipped"}

    sandbox = setup_sandbox(task, style)
    jsonl_path = RESULTS_DIR / f"{task}_{style}.jsonl"
    reply_path = RESULTS_DIR / f"{task}_{style}_reply.txt"
    prompt = TASK_PROMPTS[task]

    ts = time.strftime("%H:%M:%S")
    print(f"[{ts}] START {task}/{style}", flush=True)
    start = time.time()

    try:
        result = subprocess.run(
            [
                "codex", "exec",
                "-C", str(sandbox),
                "-s", "workspace-write",
                "--skip-git-repo-check",
                "--json",
                "-o", str(reply_path),
                prompt,
            ],
            capture_output=True,
            text=True,
            timeout=300,
        )
        jsonl_path.write_text(result.stdout)
    except subprocess.TimeoutExpired:
        elapsed = time.time() - start
        print(f"[{time.strftime('%H:%M:%S')}] TIMEOUT {task}/{style} ({elapsed:.0f}s)", flush=True)
        return {"task": task, "style": style, "status": "timeout", "elapsed": elapsed}

    elapsed = time.time() - start

    timing_line = json.dumps({
        "task": task, "style": style,
        "start": start, "end": start + elapsed,
    })
    with open(RESULTS_DIR / "timing.jsonl", "a") as f:
        f.write(timing_line + "\n")

    done_flag.touch()
    print(f"[{time.strftime('%H:%M:%S')}] DONE  {task}/{style} ({elapsed:.1f}s)", flush=True)
    return {"task": task, "style": style, "status": "done", "elapsed": elapsed}


def main():
    parallel = "--parallel" in sys.argv
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    cases = [(t, s) for t in TASKS for s in STYLES]
    total = len(cases)

    # Check how many are already done
    done = sum(1 for t, s in cases if (RESULTS_DIR / f"{t}_{s}_done").exists())
    remaining = total - done
    print(f"Total cases: {total}, already done: {done}, remaining: {remaining}")
    print(f"Mode: {'parallel' if parallel else 'sequential'}")
    print()

    if parallel:
        with ProcessPoolExecutor(max_workers=7) as executor:
            futures = {executor.submit(run_one, t, s): (t, s) for t, s in cases}
            for future in as_completed(futures):
                r = future.result()
                if r["status"] == "timeout":
                    t, s = futures[future]
                    print(f"  WARNING: {t}/{s} timed out")
    else:
        for t, s in cases:
            run_one(t, s)

    print()
    print("=== All experiments complete ===")
    print()

    subprocess.run([sys.executable, str(SCRIPT_DIR / "analyze_agent_results.py")])


if __name__ == "__main__":
    main()
