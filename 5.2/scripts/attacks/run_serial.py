#!/usr/bin/env python3
"""Run a list of attack scripts strictly serially (one process at a time).

This avoids DeepSeek rate-limit cascades that happen when several attack
scripts run in parallel and each issues many concurrent queries.
"""
from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

ROOT_5_2 = Path(__file__).resolve().parents[2]
ATTACK_DIR = ROOT_5_2 / "scripts" / "attacks"

DEFAULT_ORDER = [
    "A2_advjudge.py",
    "A3_paraphrase.py",
    "A5_insec.py",
    "A6_svulattack.py",
    "A9_mcts.py",
]


def main() -> None:
    order = sys.argv[1:] or DEFAULT_ORDER
    for name in order:
        path = ATTACK_DIR / name
        if not path.exists():
            print(f"  skip missing {name}")
            continue
        log = Path("/tmp") / f"{name.replace('.py', '')}.log"
        print(f"\n>>> {name}  log -> {log}")
        t0 = time.time()
        with log.open("w") as fh:
            proc = subprocess.run(
                ["python3", "-u", str(path)],
                stdout=fh, stderr=subprocess.STDOUT,
            )
        dt = time.time() - t0
        print(f"<<< {name}  exit={proc.returncode}  took {dt:.0f}s")


if __name__ == "__main__":
    main()
