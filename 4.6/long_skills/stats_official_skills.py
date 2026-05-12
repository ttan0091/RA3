#!/usr/bin/env python3
"""统计 26 个官方 skill 的 token / 行数 / 文件数 / 字节数"""
import json
from pathlib import Path
from statistics import mean, median, stdev

import tiktoken

ROOT = Path("/Users/tan/Desktop/RA3/4.6/long_skills")
BENIGN = ROOT / "benchmark" / "benign"
ENC = tiktoken.get_encoding("cl100k_base")

SCAN_EXTENSIONS = {".md", ".txt", ".py", ".js", ".ts", ".sh", ".bash",
                   ".yml", ".yaml", ".json", ".toml"}
EXCLUDE_DIRS = {".git", "__pycache__", "node_modules", ".venv", "venv"}


def collect_files(skill_dir):
    out = []
    for fpath in sorted(skill_dir.rglob("*")):
        if not fpath.is_file(): continue
        if any(part in EXCLUDE_DIRS for part in fpath.parts): continue
        if fpath.suffix not in SCAN_EXTENSIONS: continue
        try:
            content = fpath.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        out.append((str(fpath.relative_to(skill_dir)), content))
    return out


def stats_for(skill_dir):
    skill_md = skill_dir / "SKILL.md"
    md_text = skill_md.read_text() if skill_md.exists() else ""
    md_lines = md_text.count("\n") + 1 if md_text else 0
    md_chars = len(md_text)
    md_tokens = len(ENC.encode(md_text))

    files = collect_files(skill_dir)
    total_chars = sum(len(c) for _, c in files)
    total_lines = sum(c.count("\n") + 1 for _, c in files)
    total_tokens = sum(len(ENC.encode(c)) for _, c in files)

    return {
        "skill": skill_dir.name,
        "n_files": len(files),
        "skill_md_lines": md_lines,
        "skill_md_chars": md_chars,
        "skill_md_tokens": md_tokens,
        "total_lines": total_lines,
        "total_chars": total_chars,
        "total_tokens": total_tokens,
    }


def fmt_summary(values, label):
    return (f"{label:<25} min={min(values):>6}  median={int(median(values)):>6}  "
            f"mean={int(mean(values)):>6}  max={max(values):>6}  "
            f"stdev={int(stdev(values)) if len(values) > 1 else 0:>6}")


def main():
    rows = []
    for d in sorted(BENIGN.iterdir()):
        if d.is_dir():
            rows.append(stats_for(d))

    print(f"# 26 官方 skill 输入规模统计 (tiktoken cl100k_base)\n")
    print(f"## Per-skill 明细\n")
    print(f"{'#':>2} {'skill':<55} {'files':>5} | {'SKILL.md':>20} | {'all-files':>22}")
    print(f"{'':>2} {'':<55} {'':>5} | {'lines':>5} {'chars':>6} {'tok':>6} | "
          f"{'lines':>5} {'chars':>6} {'tok':>7}")
    print("-" * 120)
    rows_sorted = sorted(rows, key=lambda r: r["total_tokens"])
    for i, r in enumerate(rows_sorted, 1):
        print(f"{i:>2} {r['skill']:<55} {r['n_files']:>5} | "
              f"{r['skill_md_lines']:>5} {r['skill_md_chars']:>6} {r['skill_md_tokens']:>6} | "
              f"{r['total_lines']:>5} {r['total_chars']:>6} {r['total_tokens']:>7}")

    print(f"\n## 汇总 (n=26)\n")
    print("**SKILL.md 单文件：**")
    print(fmt_summary([r["skill_md_lines"]   for r in rows], "  lines"))
    print(fmt_summary([r["skill_md_chars"]   for r in rows], "  chars"))
    print(fmt_summary([r["skill_md_tokens"]  for r in rows], "  tokens"))

    print("\n**整个 skill 目录（全部可扫描文件）：**")
    print(fmt_summary([r["n_files"]          for r in rows], "  files (count)"))
    print(fmt_summary([r["total_lines"]      for r in rows], "  total lines"))
    print(fmt_summary([r["total_chars"]      for r in rows], "  total chars"))
    print(fmt_summary([r["total_tokens"]     for r in rows], "  total tokens"))

    print(f"\n**总计（26 个 skill 加起来）：**")
    print(f"  files       : {sum(r['n_files'] for r in rows)}")
    print(f"  SKILL.md tokens : {sum(r['skill_md_tokens'] for r in rows):,}")
    print(f"  total tokens    : {sum(r['total_tokens'] for r in rows):,}")

    out_json = ROOT / "official_skills_stats.json"
    out_json.write_text(json.dumps(rows, indent=2))
    print(f"\n→ 明细写入 {out_json}")


if __name__ == "__main__":
    main()
