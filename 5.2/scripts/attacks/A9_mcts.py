#!/usr/bin/env python3
"""A9 — MCTS-style search over A8's transforms (AdVulCode).

Treats each subset / order of A8 transforms as an action sequence; uses a small
random search with detector queries instead of a full MCTS for cost reasons.
This still gets the spirit of AdVulCode (search-based combination) while
keeping queries within budget.
"""
from __future__ import annotations

import argparse
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from attacks._helpers import (  # noqa: E402
    DEFAULT_APS, attack_dir, copy_skill, src_skill_dir,
    write_attack_log, benign_score, judge_semantic_preservation,
)
from attacks.A8_transforms import (  # noqa: E402
    L1_rename, L2_decoy, D1_split_strings, D2_b64_endpoint,
    D3_config_dict, C1_try_finally, SCRIPT_EXTS,
)

ACTIONS = [L1_rename, L2_decoy, D1_split_strings, D2_b64_endpoint, D3_config_dict, C1_try_finally]
N_TRIALS = 6
SEED = 42


def apply_seq(src: str, seq: list) -> str:
    out = src
    for fn in seq:
        try:
            out = fn(out)
        except Exception:
            continue
    return out


def attack_one(ap: str) -> dict:
    src = src_skill_dir(ap)
    dst = attack_dir("a9", ap)
    copy_skill(src, dst)

    rng = random.Random(SEED + hash(ap) % 1000)
    base_score, base_res = benign_score(dst)

    scripts = [p for p in dst.rglob("*") if p.is_file() and p.suffix in SCRIPT_EXTS]
    if not scripts:
        log = {"error": "no_python_scripts", "baseline_score": base_score}
        write_attack_log(dst, "a9", ap, log)
        return log

    originals = {p: p.read_text() for p in scripts}
    best_score = base_score
    best_seq: list = []
    iters = []

    for trial in range(N_TRIALS):
        k = rng.randint(2, len(ACTIONS))
        seq = rng.sample(ACTIONS, k)
        for p, orig in originals.items():
            p.write_text(apply_seq(orig, seq))
        score, res = benign_score(dst)
        print(f"    [a9/{ap}] trial {trial+1}/{N_TRIALS}: "
              f"score={score:.3f} n_findings={res['n_findings']}", flush=True)
        iters.append({"trial": trial, "seq": [f.__name__ for f in seq],
                      "score": score, "n_findings": res["n_findings"]})
        if score > best_score:
            best_score = score
            best_seq = seq

    # Apply best
    for p, orig in originals.items():
        if best_seq:
            p.write_text(apply_seq(orig, best_seq))
        else:
            p.write_text(orig)
    final_score, final_res = benign_score(dst)
    sem = judge_semantic_preservation(src, dst)

    log = {
        "baseline_score": base_score,
        "baseline_n_findings": base_res["n_findings"],
        "best_score": final_score,
        "best_n_findings": final_res["n_findings"],
        "best_seq": [f.__name__ for f in best_seq],
        "trials": iters,
        "semantic_preservation": sem,
    }
    write_attack_log(dst, "a9", ap, log)
    return log


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--aps", nargs="+", default=DEFAULT_APS)
    args = parser.parse_args()
    for ap in args.aps:
        print(f"\n== A9 on {ap} ==")
        log = attack_one(ap)
        if "best_score" not in log:
            print(f"  skipped: {log.get('error', 'unknown')} (baseline {log.get('baseline_score', 'NA')})")
            continue
        print(f"  base={log['baseline_score']:.3f} -> best={log['best_score']:.3f}  "
              f"semantic={log['semantic_preservation'].get('preserved', '?')}")


if __name__ == "__main__":
    main()
