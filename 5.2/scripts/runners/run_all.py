#!/usr/bin/env python3
"""Run all 5 scanners against a benchmark directory.

Output goes to <eval_root>/<scanner>/<case>.json

Usage:
    python run_all.py BENCH_DIR EVAL_ROOT
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT_5_2 = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT_5_2 / "scripts"))

from runners import (  # noqa: E402
    run_cisco_static, run_cisco_full,
    run_skillfortify,
    run_skillscan_static, run_skillscan_llm,
)


def main(bench_dir: str, eval_root: str) -> None:
    bench = Path(bench_dir)
    root = Path(eval_root)
    root.mkdir(parents=True, exist_ok=True)

    static_cisco = root / "cisco_static"
    full_cisco = root / "cisco_full"
    sf = root / "skillfortify"
    ss_static = root / "skillscan_static"
    ss_llm = root / "skillscan_llm"

    print("\n=== 1/5 Cisco Static ===")
    run_cisco_static.main(str(bench), str(static_cisco))

    print("\n=== 2/5 SkillFortify ===")
    run_skillfortify.main(str(bench), str(sf))

    print("\n=== 3/5 SkillScan Static ===")
    run_skillscan_static.main(str(bench), str(ss_static))

    print("\n=== 4/5 Cisco Full (DeepSeek) ===")
    run_cisco_full.main(str(bench), str(full_cisco), str(static_cisco))

    print("\n=== 5/5 SkillScan LLM (DeepSeek) ===")
    run_skillscan_llm.main(str(bench), str(ss_llm))

    print(f"\nDone. Results under {root}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
