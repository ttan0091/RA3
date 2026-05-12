#!/usr/bin/env python3
"""A7 — Complexity-reducing transforms (counter-intuitive evasion).

Strip comments, collapse blank lines, single-letter variable names. Single
deterministic pass per script file (no LLM queries needed for the transform
itself; one final detector query for measurement).
"""
from __future__ import annotations

import argparse
import ast
import io
import re
import sys
import tokenize
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from attacks._helpers import (  # noqa: E402
    DEFAULT_APS, attack_dir, copy_skill, src_skill_dir,
    write_attack_log, benign_score, judge_semantic_preservation,
)

SCRIPT_EXTS = {".py"}


def strip_python_comments(src: str) -> str:
    """Remove # comments and docstrings; keep newlines so line numbers loosely align."""
    out = io.StringIO()
    try:
        tokens = list(tokenize.generate_tokens(io.StringIO(src).readline))
    except tokenize.TokenizeError:
        return src
    prev = None
    for tok in tokens:
        if tok.type == tokenize.COMMENT:
            continue
        if tok.type == tokenize.STRING and prev is not None and prev.type in (
            tokenize.INDENT, tokenize.NEWLINE, tokenize.NL, tokenize.ENCODING
        ):
            # likely docstring — keep simple heuristic: drop if triple-quoted at start of block
            if tok.string.startswith(('"""', "'''")):
                continue
        prev = tok
    try:
        return tokenize.untokenize(t for t in tokens if t.type != tokenize.COMMENT)
    except Exception:
        # Fallback: regex strip of # comments
        lines = []
        for line in src.splitlines():
            stripped = re.sub(r"(?<!['\"])#.*$", "", line).rstrip()
            if stripped or not line.strip():
                lines.append(stripped)
        return "\n".join(lines)


def collapse_blank_lines(src: str) -> str:
    return re.sub(r"\n\s*\n+", "\n", src)


def shorten_var_names(src: str) -> str:
    """Rename common 'malicious' identifiers to neutral one/two-char names.

    Conservative: only renames known sensitive names so we don't break code.
    """
    renames = {
        r"\bcredentials\b": "_d",
        r"\bcreds\b": "_d",
        r"\bexfiltrate\b": "_sync",
        r"\bexfil\b": "_sync",
        r"\bendpoint\b": "_url",
        r"\bsteal\b": "_load",
        r"\bsecret\b": "_t",
        r"\bpayload\b": "_p",
    }
    for pat, repl in renames.items():
        src = re.sub(pat, repl, src, flags=re.IGNORECASE)
    return src


def simplify_python(src: str) -> str:
    src = strip_python_comments(src)
    src = collapse_blank_lines(src)
    src = shorten_var_names(src)
    return src


def attack_one(ap: str) -> dict:
    src = src_skill_dir(ap)
    dst = attack_dir("a7", ap)
    copy_skill(src, dst)

    base_score, base_res = benign_score(dst)

    n_changed = 0
    for script in dst.rglob("*"):
        if not script.is_file() or script.suffix not in SCRIPT_EXTS:
            continue
        try:
            new_text = simplify_python(script.read_text())
            if new_text != script.read_text():
                script.write_text(new_text)
                n_changed += 1
        except Exception:
            continue

    final_score, final_res = benign_score(dst)
    sem = judge_semantic_preservation(src, dst)
    log = {
        "baseline_score": base_score,
        "baseline_n_findings": base_res["n_findings"],
        "best_score": final_score,
        "best_n_findings": final_res["n_findings"],
        "files_simplified": n_changed,
        "semantic_preservation": sem,
    }
    write_attack_log(dst, "a7", ap, log)
    return log


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--aps", nargs="+", default=DEFAULT_APS)
    args = parser.parse_args()
    for ap in args.aps:
        print(f"\n== A7 on {ap} ==")
        log = attack_one(ap)
        print(f"  base={log['baseline_score']:.3f} -> best={log['best_score']:.3f}  "
              f"files={log['files_simplified']} "
              f"semantic={log['semantic_preservation'].get('preserved', '?')}")


if __name__ == "__main__":
    main()
