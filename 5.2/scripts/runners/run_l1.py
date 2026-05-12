#!/usr/bin/env python3
"""Run all 5 scanners on every L1 attack-generated sample.

Output goes under evaluation/L1_single/<scanner>/<case>.json
Same I/O layout as run_all.py — but reads directly from benchmark/L1_single/.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT_5_2 = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT_5_2 / "scripts"))

from runners import run_all  # noqa: E402


def main() -> None:
    bench = ROOT_5_2 / "benchmark" / "L1_single"
    out = ROOT_5_2 / "evaluation" / "L1_single"
    if not bench.exists():
        print(f"no L1 samples at {bench}")
        return
    n = sum(1 for d in bench.iterdir() if d.is_dir())
    print(f"L1 sample count: {n}")
    run_all.main(str(bench), str(out))


if __name__ == "__main__":
    main()
