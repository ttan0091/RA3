#!/usr/bin/env python3
"""
Analyze sampled skills (popular vs random) and generate comparison artifacts.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import statistics
from collections import Counter
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


SCRIPT_EXTENSIONS = {
    ".py",
    ".sh",
    ".bash",
    ".zsh",
    ".ps1",
    ".js",
    ".ts",
    ".mjs",
    ".cjs",
    ".rb",
    ".go",
    ".java",
    ".rs",
    ".php",
    ".bat",
    ".cmd",
}

CONFIG_EXTENSIONS = {
    ".json",
    ".yaml",
    ".yml",
    ".toml",
    ".ini",
    ".cfg",
    ".conf",
    ".env",
    ".xml",
}

DOC_FOLDERS = {"docs", "doc", "reference", "references"}
TEMPLATE_HINTS = {"template", "templates", "boilerplate", "scaffold"}

TAXONOMY_RULES: dict[str, list[str]] = {
    "coding_dev": [
        "code",
        "coding",
        "debug",
        "bug",
        "refactor",
        "implementation",
        "function",
        "class",
        "api",
        "programming",
    ],
    "devops_infra": [
        "deploy",
        "deployment",
        "docker",
        "kubernetes",
        "k8s",
        "terraform",
        "infra",
        "ci/cd",
        "pipeline",
        "cloud",
    ],
    "data_ml_ai": [
        "machine learning",
        "deep learning",
        "llm",
        "model",
        "training",
        "inference",
        "rag",
        "embedding",
        "pytorch",
        "tensorflow",
    ],
    "security": [
        "security",
        "secure",
        "vulnerability",
        "oauth",
        "jwt",
        "permission",
        "encryption",
        "secret",
        "threat",
    ],
    "documentation_writing": [
        "documentation",
        "document",
        "readme",
        "release note",
        "changelog",
        "writing",
        "summary",
        "report",
    ],
    "research_analysis": [
        "research",
        "analysis",
        "benchmark",
        "evaluate",
        "experiment",
        "study",
        "paper",
    ],
    "workflow_automation": [
        "workflow",
        "automation",
        "orchestrate",
        "process",
        "agent",
        "task",
        "operation",
    ],
    "product_design": [
        "ux",
        "ui",
        "figma",
        "penpot",
        "wireframe",
        "design system",
        "user interface",
        "landing page",
        "prototype",
    ],
    "integration_tools": [
        "integration",
        "plugin",
        "mcp",
        "github",
        "slack",
        "discord",
        "notion",
        "stripe",
        "webhook",
    ],
}

SECURITY_POSITIVE_PATTERNS = [
    "least privilege",
    "never",
    "avoid",
    "do not",
    "must not",
    "confirm",
    "approval",
    "validate",
    "sanitize",
    "security",
]

SECURITY_RISK_PATTERNS = [
    "rm -rf",
    "curl | sh",
    "chmod 777",
    "sudo ",
    "api key",
    "secret",
    "password",
    "token",
    "private key",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyze sampled skills in popular/random cohorts.")
    parser.add_argument(
        "--run-dir",
        default="skills_data/sampled_skills_1000",
        help="Path to sampled skills run directory.",
    )
    parser.add_argument(
        "--output-dir",
        default="",
        help="Output directory. Defaults to <run-dir>/analysis",
    )
    return parser.parse_args()


def safe_read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="ignore")


def find_skill_md(content_dir: Path) -> Path | None:
    if not content_dir.exists():
        return None
    candidates = [p for p in content_dir.rglob("*") if p.is_file() and p.name.lower() == "skill.md"]
    if not candidates:
        return None
    candidates.sort(key=lambda p: (len(p.relative_to(content_dir).parts), str(p).lower()))
    return candidates[0]


def count_occurrences(text: str, patterns: list[str]) -> int:
    low = text.lower()
    return sum(low.count(p.lower()) for p in patterns)


def median(values: list[float]) -> float:
    if not values:
        return 0.0
    return float(statistics.median(values))


def mean(values: list[float]) -> float:
    if not values:
        return 0.0
    return float(statistics.fmean(values))


def q90(values: list[float]) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    idx = int(round((len(ordered) - 1) * 0.9))
    return float(ordered[idx])


def ratio(features: list[dict[str, Any]], key: str) -> float:
    if not features:
        return 0.0
    return sum(1 for f in features if f.get(key)) / len(features)


def extract_taxonomy_labels(text: str) -> list[str]:
    low = text.lower()
    labels: list[str] = []
    for label, keywords in TAXONOMY_RULES.items():
        if any(keyword_match(low, k) for k in keywords):
            labels.append(label)
    if not labels:
        labels.append("domain_specific")
    return labels


def keyword_match(text: str, keyword: str) -> bool:
    escaped = re.escape(keyword.lower())
    if re.match(r"^[a-z0-9_ ]+$", keyword.lower()):
        pattern = rf"\b{escaped}\b"
    else:
        pattern = escaped
    return re.search(pattern, text) is not None


def analyze_skill(skill_dir: Path, cohort: str) -> dict[str, Any]:
    metadata_path = skill_dir / "metadata.json"
    if not metadata_path.exists():
        raise FileNotFoundError(f"missing metadata.json: {skill_dir}")
    metadata = json.loads(safe_read_text(metadata_path))
    skill = metadata.get("skill", {})

    content_dir = skill_dir / "content"
    files = [p for p in content_dir.rglob("*") if p.is_file()] if content_dir.exists() else []
    dirs = [p for p in content_dir.rglob("*") if p.is_dir()] if content_dir.exists() else []

    file_count = len(files)
    dir_count = len(dirs)
    total_bytes = sum(p.stat().st_size for p in files) if files else 0

    if files:
        max_depth = max(len(p.relative_to(content_dir).parts) for p in files)
    else:
        max_depth = 0

    has_scripts = any(p.suffix.lower() in SCRIPT_EXTENSIONS for p in files)
    has_templates = any(any(h in part.lower() for h in TEMPLATE_HINTS) for p in files for part in p.parts)
    has_docs = any(part.lower() in DOC_FOLDERS for p in dirs for part in p.parts)
    has_config = any(p.suffix.lower() in CONFIG_EXTENSIONS for p in files)
    has_license = any(p.name.lower().startswith("license") for p in files)

    skill_md_path = find_skill_md(content_dir)
    skill_md_text = safe_read_text(skill_md_path) if skill_md_path else ""
    skill_md_lines = len(skill_md_text.splitlines()) if skill_md_text else 0
    skill_md_words = len(re.findall(r"\b\w+\b", skill_md_text)) if skill_md_text else 0
    heading_count = len(re.findall(r"^\s*#{1,6}\s+", skill_md_text, flags=re.MULTILINE))
    code_fence_count = skill_md_text.count("```")
    ordered_list_count = len(re.findall(r"^\s*\d+\.\s+", skill_md_text, flags=re.MULTILINE))
    bullet_list_count = len(re.findall(r"^\s*[-*]\s+", skill_md_text, flags=re.MULTILINE))
    step_signal_count = len(
        re.findall(
            r"\b(step|steps|first|second|then|next|finally)\b",
            skill_md_text.lower(),
        )
    )
    example_signal_count = len(re.findall(r"\b(example|examples|for example|e\.g\.)\b", skill_md_text.lower()))
    boundary_signal_count = len(
        re.findall(
            r"\b(avoid|do not|don't|must not|never|only if|unless|edge case|limit)\b",
            skill_md_text.lower(),
        )
    )
    placeholder_count = (
        len(re.findall(r"\$[A-Z_][A-Z0-9_]*", skill_md_text))
        + len(re.findall(r"\{[a-zA-Z_][a-zA-Z0-9_.-]*\}", skill_md_text))
    )
    version_mention_count = len(re.findall(r"\bv?\d+\.\d+(?:\.\d+)?\b", skill_md_text.lower()))
    license_mention_count = len(re.findall(r"\blicense\b", skill_md_text.lower()))

    full_text = " ".join(
        [
            str(skill.get("name", "")),
            str(skill.get("description", "")),
            skill_md_text[:6000],
        ]
    ).lower()
    taxonomy_labels = extract_taxonomy_labels(full_text)

    security_positive_score = count_occurrences(full_text, SECURITY_POSITIVE_PATTERNS)
    security_risk_score = count_occurrences(full_text, SECURITY_RISK_PATTERNS)

    return {
        "cohort": cohort,
        "skill_id": skill.get("id", skill_dir.name),
        "skill_dirname": skill_dir.name,
        "skill_name": skill.get("name", ""),
        "author": skill.get("author", ""),
        "stars": int(skill.get("stars") or 0),
        "updated_at": int(skill.get("updatedAt") or 0),
        "github_url": skill.get("githubUrl", ""),
        "skill_url": skill.get("skillUrl", ""),
        "file_count": file_count,
        "dir_count": dir_count,
        "max_depth": max_depth,
        "total_bytes": total_bytes,
        "local_content_path": str(content_dir),
        "has_skill_md": bool(skill_md_path),
        "skill_md_relpath": str(skill_md_path.relative_to(content_dir)) if skill_md_path else "",
        "skill_md_lines": skill_md_lines,
        "skill_md_words": skill_md_words,
        "heading_count": heading_count,
        "code_fence_count": code_fence_count,
        "ordered_list_count": ordered_list_count,
        "bullet_list_count": bullet_list_count,
        "step_signal_count": step_signal_count,
        "example_signal_count": example_signal_count,
        "boundary_signal_count": boundary_signal_count,
        "placeholder_count": placeholder_count,
        "version_mention_count": version_mention_count,
        "license_mention_count": license_mention_count,
        "has_scripts": has_scripts,
        "has_templates": has_templates,
        "has_docs": has_docs,
        "has_config": has_config,
        "has_license_file": has_license,
        "taxonomy_labels": ";".join(taxonomy_labels),
        "security_positive_score": security_positive_score,
        "security_risk_score": security_risk_score,
        "has_security_risk_signal": security_risk_score > 0,
    }


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fieldnames = list(rows[0].keys())
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def summarize_group(features: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "n": len(features),
        "avg_file_count": mean([f["file_count"] for f in features]),
        "median_file_count": median([f["file_count"] for f in features]),
        "q90_file_count": q90([f["file_count"] for f in features]),
        "avg_total_bytes": mean([f["total_bytes"] for f in features]),
        "median_total_bytes": median([f["total_bytes"] for f in features]),
        "avg_skill_md_words": mean([f["skill_md_words"] for f in features]),
        "median_skill_md_words": median([f["skill_md_words"] for f in features]),
        "q90_skill_md_words": q90([f["skill_md_words"] for f in features]),
        "rate_has_scripts": ratio(features, "has_scripts"),
        "rate_has_templates": ratio(features, "has_templates"),
        "rate_has_docs": ratio(features, "has_docs"),
        "rate_has_config": ratio(features, "has_config"),
        "rate_has_license_file": ratio(features, "has_license_file"),
        "rate_has_security_risk_signal": ratio(features, "has_security_risk_signal"),
        "avg_security_positive_score": mean([f["security_positive_score"] for f in features]),
        "avg_security_risk_score": mean([f["security_risk_score"] for f in features]),
        "avg_heading_count": mean([f["heading_count"] for f in features]),
        "avg_code_fence_count": mean([f["code_fence_count"] for f in features]),
        "avg_example_signal_count": mean([f["example_signal_count"] for f in features]),
        "avg_boundary_signal_count": mean([f["boundary_signal_count"] for f in features]),
    }


def collect_taxonomy_counter(features: list[dict[str, Any]]) -> Counter[str]:
    counter: Counter[str] = Counter()
    for row in features:
        labels = [x for x in row["taxonomy_labels"].split(";") if x]
        counter.update(labels)
    return counter


def extract_repo_slug(github_url: str) -> str:
    parsed = urlparse(github_url)
    parts = [x for x in parsed.path.split("/") if x]
    if len(parts) >= 2:
        return f"{parts[0]}/{parts[1]}"
    return "unknown/unknown"


def concentration_summary(features: list[dict[str, Any]]) -> dict[str, Any]:
    author_counter = Counter(str(f.get("author", "")) for f in features)
    repo_counter = Counter(extract_repo_slug(str(f.get("github_url", ""))) for f in features)
    n = len(features) if features else 1
    author_top = author_counter.most_common(1)[0] if author_counter else ("", 0)
    repo_top = repo_counter.most_common(1)[0] if repo_counter else ("", 0)
    return {
        "unique_authors": len(author_counter),
        "unique_repos": len(repo_counter),
        "top_author": author_top[0],
        "top_author_count": author_top[1],
        "top_author_share": author_top[1] / n,
        "top_repo": repo_top[0],
        "top_repo_count": repo_top[1],
        "top_repo_share": repo_top[1] / n,
    }


def markdown_table(headers: list[str], rows: list[list[str]]) -> str:
    out = []
    out.append("| " + " | ".join(headers) + " |")
    out.append("| " + " | ".join(["---"] * len(headers)) + " |")
    for row in rows:
        out.append("| " + " | ".join(row) + " |")
    return "\n".join(out)


def pct(x: float) -> str:
    return f"{x * 100:.1f}%"


def main() -> int:
    args = parse_args()
    run_dir = Path(args.run_dir)
    output_dir = Path(args.output_dir) if args.output_dir else run_dir / "analysis_baseline"
    output_dir.mkdir(parents=True, exist_ok=True)

    all_features: list[dict[str, Any]] = []
    skipped: list[dict[str, str]] = []
    for cohort in ["popular", "random"]:
        cohort_dir = run_dir / cohort
        if not cohort_dir.exists():
            raise FileNotFoundError(f"missing cohort directory: {cohort_dir}")
        for skill_dir in sorted([p for p in cohort_dir.iterdir() if p.is_dir()]):
            try:
                all_features.append(analyze_skill(skill_dir, cohort))
            except Exception as e:  # noqa: BLE001
                skipped.append({"cohort": cohort, "skill_dir": str(skill_dir), "error": str(e)})

    top_features = [x for x in all_features if x["cohort"] == "popular"]
    random_features = [x for x in all_features if x["cohort"] == "random"]

    write_csv(output_dir / "features_top.csv", top_features)
    write_csv(output_dir / "features_random.csv", random_features)
    write_csv(output_dir / "features_all.csv", all_features)

    taxonomy_rows = []
    for row in all_features:
        taxonomy_rows.append(
            {
                "cohort": row["cohort"],
                "skill_id": row["skill_id"],
                "skill_name": row["skill_name"],
                "author": row["author"],
                "taxonomy_labels": row["taxonomy_labels"],
            }
        )
    write_csv(output_dir / "taxonomy_v1.csv", taxonomy_rows)

    top_summary = summarize_group(top_features)
    random_summary = summarize_group(random_features)
    top_concentration = concentration_summary(top_features)
    random_concentration = concentration_summary(random_features)
    summary_payload = {
        "top": top_summary,
        "random": random_summary,
        "top_concentration": top_concentration,
        "random_concentration": random_concentration,
        "delta_top_minus_random": {
            k: (top_summary[k] - random_summary[k])
            for k in top_summary.keys()
            if k != "n"
        },
        "skipped_count": len(skipped),
        "skipped": skipped,
    }
    (output_dir / "summary_metrics.json").write_text(
        json.dumps(summary_payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    top_tax = collect_taxonomy_counter(top_features)
    rnd_tax = collect_taxonomy_counter(random_features)
    labels = sorted(set(top_tax) | set(rnd_tax))
    tax_rows = []
    for label in labels:
        t = top_tax[label]
        r = rnd_tax[label]
        tax_rows.append(
            {
                "label": label,
                "top_count": t,
                "top_rate": round(t / max(1, len(top_features)), 4),
                "random_count": r,
                "random_rate": round(r / max(1, len(random_features)), 4),
                "delta_rate_top_minus_random": round((t / max(1, len(top_features))) - (r / max(1, len(random_features))), 4),
            }
        )
    write_csv(output_dir / "taxonomy_distribution.csv", tax_rows)

    risk_rows = sorted(all_features, key=lambda x: (x["security_risk_score"], x["security_positive_score"]), reverse=True)
    write_csv(output_dir / "security_scores.csv", risk_rows)

    top_risky = [r for r in risk_rows if r["security_risk_score"] > 0][:20]
    sec_lines = [
        "# Security Findings",
        "",
        f"- Total skills analyzed: {len(all_features)}",
        f"- Skills with risk signals: {sum(1 for r in all_features if r['has_security_risk_signal'])}",
        f"- Top risk signal rate (popular): {pct(top_summary['rate_has_security_risk_signal'])}",
        f"- Top risk signal rate (random): {pct(random_summary['rate_has_security_risk_signal'])}",
        "",
        "## Top Risk-Signal Skills",
        "",
    ]
    if top_risky:
        sec_lines.append(markdown_table(
            ["cohort", "skill_id", "risk_score", "positive_score", "github_url"],
            [
                [
                    r["cohort"],
                    r["skill_id"],
                    str(r["security_risk_score"]),
                    str(r["security_positive_score"]),
                    r["github_url"],
                ]
                for r in top_risky
            ],
        ))
    else:
        sec_lines.append("No risk-signal skill found by rule-based scan.")
    (output_dir / "security_findings.md").write_text("\n".join(sec_lines), encoding="utf-8")

    key_rows = [
        ["Sample size", str(top_summary["n"]), str(random_summary["n"]), "-"],
        ["Avg file count", f"{top_summary['avg_file_count']:.2f}", f"{random_summary['avg_file_count']:.2f}", f"{top_summary['avg_file_count'] - random_summary['avg_file_count']:.2f}"],
        ["Median file count", f"{top_summary['median_file_count']:.1f}", f"{random_summary['median_file_count']:.1f}", f"{top_summary['median_file_count'] - random_summary['median_file_count']:.1f}"],
        ["Avg SKILL.md words", f"{top_summary['avg_skill_md_words']:.1f}", f"{random_summary['avg_skill_md_words']:.1f}", f"{top_summary['avg_skill_md_words'] - random_summary['avg_skill_md_words']:.1f}"],
        ["Has scripts", pct(top_summary["rate_has_scripts"]), pct(random_summary["rate_has_scripts"]), pct(top_summary["rate_has_scripts"] - random_summary["rate_has_scripts"])],
        ["Has templates", pct(top_summary["rate_has_templates"]), pct(random_summary["rate_has_templates"]), pct(top_summary["rate_has_templates"] - random_summary["rate_has_templates"])],
        ["Has docs folders", pct(top_summary["rate_has_docs"]), pct(random_summary["rate_has_docs"]), pct(top_summary["rate_has_docs"] - random_summary["rate_has_docs"])],
        ["Has config files", pct(top_summary["rate_has_config"]), pct(random_summary["rate_has_config"]), pct(top_summary["rate_has_config"] - random_summary["rate_has_config"])],
        ["Has license file", pct(top_summary["rate_has_license_file"]), pct(random_summary["rate_has_license_file"]), pct(top_summary["rate_has_license_file"] - random_summary["rate_has_license_file"])],
        ["Risk-signal rate", pct(top_summary["rate_has_security_risk_signal"]), pct(random_summary["rate_has_security_risk_signal"]), pct(top_summary["rate_has_security_risk_signal"] - random_summary["rate_has_security_risk_signal"])],
    ]

    top_tax_lines = [f"- {k}: {v} ({pct(v / max(1, len(top_features)))})" for k, v in top_tax.most_common(10)]
    rnd_tax_lines = [f"- {k}: {v} ({pct(v / max(1, len(random_features)))})" for k, v in rnd_tax.most_common(10)]

    report_lines = [
        "# Popular vs Random Skills Comparison",
        "",
        "## Cohort Status",
        "",
        f"- Popular skills: {len(top_features)}",
        f"- Random skills: {len(random_features)}",
        f"- Skipped during analysis: {len(skipped)}",
        "",
        "## Key Metrics",
        "",
        markdown_table(["Metric", "Popular", "Random", "Delta (Popular-Random)"], key_rows),
        "",
        "## Cohort Concentration",
        "",
        markdown_table(
            ["Metric", "Popular", "Random"],
            [
                ["Unique authors", str(top_concentration["unique_authors"]), str(random_concentration["unique_authors"])],
                ["Unique repos", str(top_concentration["unique_repos"]), str(random_concentration["unique_repos"])],
                [
                    "Top author share",
                    f"{top_concentration['top_author']} ({pct(top_concentration['top_author_share'])})",
                    f"{random_concentration['top_author']} ({pct(random_concentration['top_author_share'])})",
                ],
                [
                    "Top repo share",
                    f"{top_concentration['top_repo']} ({pct(top_concentration['top_repo_share'])})",
                    f"{random_concentration['top_repo']} ({pct(random_concentration['top_repo_share'])})",
                ],
            ],
        ),
        "",
        "## Taxonomy Distribution (Top 10 in Each Cohort)",
        "",
        "### Popular",
        "",
        *top_tax_lines,
        "",
        "### Random",
        "",
        *rnd_tax_lines,
        "",
        "## Notes",
        "",
        "- Taxonomy and security are keyword/rule-based and should be followed by manual validation on selected samples.",
        "- These stats are cohort-level descriptive comparisons, not causal findings.",
    ]
    (output_dir / "comparison_summary.md").write_text("\n".join(report_lines), encoding="utf-8")

    print(f"[INFO] Analysis complete. Output dir: {output_dir}")
    print(f"[INFO] popular={len(top_features)} random={len(random_features)} skipped={len(skipped)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
