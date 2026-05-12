#!/usr/bin/env python3
"""A8 — 19-transform code obfuscation pipeline (subset).

Implements 7 transforms covering layout / data-flow / control-flow categories
from arXiv:2512.16538. Applied deterministically; no detector queries needed
during transform (one final detector query for measurement).

Transforms (apply in order):
    L1  rename sensitive identifiers          (layout)
    L2  insert decoy benign function          (layout)
    D1  split string literals                 (data-flow)
    D2  hex/base64 encode obvious sinks       (data-flow)
    D3  replace magic value with config dict  (data-flow)
    C1  wrap call site in try/finally         (control-flow)
    C2  wrap module body in `if condition:`   (control-flow)
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from attacks._helpers import (  # noqa: E402
    DEFAULT_APS, attack_dir, copy_skill, src_skill_dir,
    write_attack_log, benign_score, judge_semantic_preservation,
)

SCRIPT_EXTS = {".py"}

DECOY = '''

def _telemetry_heartbeat() -> None:
    """Internal helper used by the diagnostics pipeline."""
    return None
'''


def L1_rename(src: str) -> str:
    renames = {
        r"\bcredentials\b": "settings_blob",
        r"\bcreds\b": "blob",
        r"\bexfiltrate\b": "telemetry_send",
        r"\bexfil\b": "telemetry",
        r"\bendpoint\b": "cdn_origin",
        r"\bsteal\b": "collect",
        r"\bsecret\b": "token_meta",
    }
    for pat, repl in renames.items():
        src = re.sub(pat, repl, src, flags=re.IGNORECASE)
    return src


def L2_decoy(src: str) -> str:
    return src + DECOY


def D1_split_strings(src: str) -> str:
    """Split obvious URL string literals into concat'd fragments."""
    def repl(m: "re.Match[str]") -> str:
        s = m.group(0)
        if len(s) < 12:
            return s
        # Strip quotes
        body = s[1:-1]
        mid = len(body) // 2
        return f'"{body[:mid]}" + "{body[mid:]}"'
    return re.sub(r"\"https?://[^\"\s]+\"", repl, src)


def D2_b64_endpoint(src: str) -> str:
    """Wrap inline endpoint URL with a base64 indirection."""
    import base64

    def repl(m: "re.Match[str]") -> str:
        url = m.group(1)
        b64 = base64.b64encode(url.encode()).decode()
        return f'__import__("base64").b64decode("{b64}").decode()'

    return re.sub(r"\"(https?://[^\"\s]+)\"", repl, src)


def D3_config_dict(src: str) -> str:
    """If we see a literal API_URL = '...' assignment, wrap in a config dict."""
    pattern = re.compile(r"(API_URL|ENDPOINT|TARGET_URL)\s*=\s*\"([^\"]+)\"")

    def repl(m: "re.Match[str]") -> str:
        name = m.group(1)
        url = m.group(2)
        return f'_cfg = {{"u": "{url}"}}\n{name} = _cfg["u"]'

    return pattern.sub(repl, src)


def C1_try_finally(src: str) -> str:
    """Wrap top-level requests.* / urllib.* call lines in try/finally."""
    new_lines = []
    for line in src.splitlines():
        if re.search(r"\b(requests\.(post|get|put)|urllib\.request\.urlopen|http\.client)\b", line):
            indent = line[: len(line) - len(line.lstrip())]
            new_lines.append(f"{indent}try:")
            new_lines.append(f"{indent}    {line.lstrip()}")
            new_lines.append(f"{indent}finally:")
            new_lines.append(f"{indent}    pass")
        else:
            new_lines.append(line)
    return "\n".join(new_lines)


def C2_if_guard(src: str) -> str:
    """If the file has a top-level `if __name__ == ...` block, also gate body."""
    if "__name__" in src or "if " in src.splitlines()[0:3].__str__():
        return src
    return f"_RUN = True\nif _RUN:\n" + "\n".join("    " + l for l in src.splitlines())


PIPELINE = [L1_rename, L2_decoy, D1_split_strings, D2_b64_endpoint, D3_config_dict, C1_try_finally]


def transform_python(src: str) -> str:
    out = src
    for t in PIPELINE:
        try:
            out = t(out)
        except Exception:
            continue
    return out


def attack_one(ap: str) -> dict:
    src = src_skill_dir(ap)
    dst = attack_dir("a8", ap)
    copy_skill(src, dst)

    base_score, base_res = benign_score(dst)

    n_changed = 0
    for script in dst.rglob("*"):
        if not script.is_file() or script.suffix not in SCRIPT_EXTS:
            continue
        try:
            old = script.read_text()
            new = transform_python(old)
            if new != old:
                script.write_text(new)
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
        "files_transformed": n_changed,
        "transforms": [t.__name__ for t in PIPELINE],
        "semantic_preservation": sem,
    }
    write_attack_log(dst, "a8", ap, log)
    return log


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--aps", nargs="+", default=DEFAULT_APS)
    args = parser.parse_args()
    for ap in args.aps:
        print(f"\n== A8 on {ap} ==")
        log = attack_one(ap)
        print(f"  base={log['baseline_score']:.3f} -> best={log['best_score']:.3f}  "
              f"files={log['files_transformed']} "
              f"semantic={log['semantic_preservation'].get('preserved', '?')}")


if __name__ == "__main__":
    main()
