#!/usr/bin/env python3
"""Count LLM input tokens for the 53 evade_g* skill cases."""
import csv
from pathlib import Path

import tiktoken

ROOT = Path("/Users/tan/Desktop/RA3")
BENCHMARK = ROOT / "3.24/benchmark/malicious"
OUT_CSV = ROOT / "3.24/evaluation/llm_input_token_counts_53.csv"
OUT_MD = ROOT / "4.6/llm_input_token_counts_53.md"

PROMPT_SKILLSCAN = ROOT / "3.21/MaliciousAgentSkillsBench/code/analyzer/prompts/audit_prompt.txt"
PROMPT_CISCO = ROOT / "3.21/skill-scanner/skill_scanner/data/prompts/skill_threat_analysis_prompt.md"
PROMPT_CISCO_RULES = ROOT / "3.21/skill-scanner/skill_scanner/data/prompts/boilerplate_protection_rule_prompt.md"

SCAN_EXTENSIONS = {".md", ".txt", ".py", ".js", ".ts", ".sh", ".bash", ".yml", ".yaml", ".json", ".toml"}
EXCLUDE_DIRS = {".git", "__pycache__", "node_modules", ".venv", "venv"}


def read_skill_files(skill_path: Path, header: str) -> str:
    lines = [header]
    for fpath in sorted(skill_path.rglob("*")):
        if not fpath.is_file():
            continue
        if any(part in EXCLUDE_DIRS for part in fpath.parts):
            continue
        if fpath.suffix not in SCAN_EXTENSIONS:
            continue
        rel = fpath.relative_to(skill_path)
        try:
            content = fpath.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        lines.append(f"\n--- FILE: {rel} ---\n{content}\n--- END FILE ---")
    return "\n".join(lines)


def count_tokens(enc, text: str) -> int:
    return len(enc.encode(text))


def summarize(values: list[int]) -> dict[str, float]:
    values = sorted(values)
    n = len(values)
    return {
        "min": values[0],
        "max": values[-1],
        "mean": sum(values) / n,
        "median": values[n // 2] if n % 2 else (values[n // 2 - 1] + values[n // 2]) / 2,
        "p90": values[int(n * 0.9) - 1],
    }


def main() -> None:
    enc = tiktoken.get_encoding("cl100k_base")
    cases = sorted(d.name for d in BENCHMARK.iterdir() if d.is_dir() and "_evade_g" in d.name)

    skillscan_system = PROMPT_SKILLSCAN.read_text()
    cisco_system = PROMPT_CISCO.read_text()
    if PROMPT_CISCO_RULES.exists():
        cisco_system = PROMPT_CISCO_RULES.read_text().strip() + "\n\n" + cisco_system.strip()

    skillscan_system_tokens = count_tokens(enc, skillscan_system)
    cisco_system_tokens = count_tokens(enc, cisco_system)

    rows = []
    for case in cases:
        skill_path = BENCHMARK / case
        skillscan_user = read_skill_files(skill_path, f"Analyze Skill Directory: {skill_path}\n")
        cisco_user = read_skill_files(skill_path, f"# Skill Directory: {case}\n")
        skillscan_user_tokens = count_tokens(enc, skillscan_user)
        cisco_user_tokens = count_tokens(enc, cisco_user)
        rows.append({
            "case": case,
            "group": "G" + case.split("_evade_g", 1)[1],
            "skillscan_user_tokens": skillscan_user_tokens,
            "skillscan_system_tokens": skillscan_system_tokens,
            "skillscan_total_input_tokens": skillscan_user_tokens + skillscan_system_tokens,
            "cisco_user_tokens": cisco_user_tokens,
            "cisco_system_tokens": cisco_system_tokens,
            "cisco_total_input_tokens": cisco_user_tokens + cisco_system_tokens,
        })

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    skillscan_summary = summarize([r["skillscan_total_input_tokens"] for r in rows])
    cisco_summary = summarize([r["cisco_total_input_tokens"] for r in rows])
    user_summary = summarize([r["skillscan_user_tokens"] for r in rows])

    top_skillscan = sorted(rows, key=lambda r: r["skillscan_total_input_tokens"], reverse=True)[:10]
    top_cisco = sorted(rows, key=lambda r: r["cisco_total_input_tokens"], reverse=True)[:10]

    lines = [
        "# 53 个 evade_g skill 的 LLM 输入 token 统计",
        "",
        "Token 统计使用 `tiktoken` 的 `cl100k_base` 编码，作为 OpenAI-compatible chat 输入长度的近似值。",
        "",
        "## 固定 system prompt token",
        "",
        f"- SkillScan-style system prompt: `{skillscan_system_tokens}` tokens",
        f"- Cisco-style system prompt: `{cisco_system_tokens}` tokens",
        "",
        "## 总输入 token 汇总",
        "",
        "| 配置 | Min | Median | Mean | P90 | Max |",
        "|---|---:|---:|---:|---:|---:|",
        f"| SkillScan-style total | {skillscan_summary['min']:.0f} | {skillscan_summary['median']:.0f} | {skillscan_summary['mean']:.1f} | {skillscan_summary['p90']:.0f} | {skillscan_summary['max']:.0f} |",
        f"| Cisco-style total | {cisco_summary['min']:.0f} | {cisco_summary['median']:.0f} | {cisco_summary['mean']:.1f} | {cisco_summary['p90']:.0f} | {cisco_summary['max']:.0f} |",
        f"| Skill files only | {user_summary['min']:.0f} | {user_summary['median']:.0f} | {user_summary['mean']:.1f} | {user_summary['p90']:.0f} | {user_summary['max']:.0f} |",
        "",
        "## 每个 case",
        "",
        "| Case | Group | Skill files | SkillScan total | Cisco total |",
        "|---|---:|---:|---:|---:|",
    ]
    for r in rows:
        lines.append(
            f"| `{r['case']}` | {r['group']} | {r['skillscan_user_tokens']} | "
            f"{r['skillscan_total_input_tokens']} | {r['cisco_total_input_tokens']} |"
        )
    lines.extend([
        "",
        "## SkillScan-style total 最大的 10 个",
        "",
        "| Case | Tokens |",
        "|---|---:|",
    ])
    for r in top_skillscan:
        lines.append(f"| `{r['case']}` | {r['skillscan_total_input_tokens']} |")
    lines.extend([
        "",
        "## Cisco-style total 最大的 10 个",
        "",
        "| Case | Tokens |",
        "|---|---:|",
    ])
    for r in top_cisco:
        lines.append(f"| `{r['case']}` | {r['cisco_total_input_tokens']} |")

    OUT_MD.write_text("\n".join(lines) + "\n")
    print(f"Wrote {OUT_CSV}")
    print(f"Wrote {OUT_MD}")
    print(f"SkillScan total median={skillscan_summary['median']:.0f}, max={skillscan_summary['max']:.0f}")
    print(f"Cisco total median={cisco_summary['median']:.0f}, max={cisco_summary['max']:.0f}")


if __name__ == "__main__":
    main()
