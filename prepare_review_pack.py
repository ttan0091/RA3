#!/usr/bin/env python3
"""
Prepare manual-review pack and meeting brief from analysis outputs.
"""

from __future__ import annotations

import argparse
import csv
import json
import random
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build manual review candidates and empirical brief.")
    parser.add_argument(
        "--run-dir",
        default="skills_data/sampled_skills_1000",
        help="Sampled skills run directory.",
    )
    parser.add_argument(
        "--analysis-dir",
        default="",
        help="Analysis directory. Defaults to <run-dir>/analysis",
    )
    parser.add_argument(
        "--review-size",
        type=int,
        default=30,
        help="Number of manual review candidates.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=20260226,
        help="Random seed for fill-up sampling.",
    )
    return parser.parse_args()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fieldnames = list(rows[0].keys())
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def to_int(row: dict[str, str], key: str) -> int:
    v = row.get(key, "")
    try:
        return int(float(v))
    except ValueError:
        return 0


def select_top(
    rows: list[dict[str, str]],
    by_key: str,
    k: int,
    selected: set[str],
    descending: bool = True,
) -> list[dict[str, str]]:
    ordered = sorted(rows, key=lambda r: to_int(r, by_key), reverse=descending)
    picked: list[dict[str, str]] = []
    for r in ordered:
        sid = r["skill_id"]
        if sid in selected:
            continue
        picked.append(r)
        selected.add(sid)
        if len(picked) >= k:
            break
    return picked


def bucket_pick(
    cohort_rows: list[dict[str, str]],
    selected: set[str],
) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []

    # 1) security-high samples
    risk_candidates = [r for r in cohort_rows if to_int(r, "security_risk_score") > 0]
    out.extend(select_top(risk_candidates, "security_risk_score", 5, selected))

    # 2) structurally heavy samples
    out.extend(select_top(cohort_rows, "file_count", 5, selected))

    # 3) long-instruction samples
    out.extend(select_top(cohort_rows, "skill_md_words", 5, selected))
    return out


def make_review_rows(
    rows: list[dict[str, str]],
    run_dir: Path,
    reason: str,
) -> list[dict[str, Any]]:
    out = []
    for r in rows:
        cohort = r["cohort"]
        sid = r["skill_id"]
        local_path = r.get("local_content_path") or str(run_dir / cohort / sid / "content")
        out.append(
            {
                "review_bucket": reason,
                "cohort": cohort,
                "skill_id": sid,
                "skill_name": r.get("skill_name", ""),
                "author": r.get("author", ""),
                "stars": to_int(r, "stars"),
                "file_count": to_int(r, "file_count"),
                "skill_md_words": to_int(r, "skill_md_words"),
                "taxonomy_labels": r.get("taxonomy_labels", ""),
                "security_risk_score": to_int(r, "security_risk_score"),
                "security_positive_score": to_int(r, "security_positive_score"),
                "github_url": r.get("github_url", ""),
                "local_content_path": str(local_path),
            }
        )
    return out


def enrich_template(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out = []
    for r in rows:
        x = dict(r)
        x.update(
            {
                "reviewer": "",
                "primary_taxonomy_manual": "",
                "taxonomy_match": "",
                "has_clear_steps_manual": "",
                "has_examples_manual": "",
                "boundary_condition_quality_0to2": "",
                "security_controls_level": "",
                "security_risk_level": "",
                "license_mention_manual": "",
                "overall_quality_1to5": "",
                "notes": "",
            }
        )
        out.append(x)
    return out


def load_summary(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def pct(v: float) -> str:
    return f"{v * 100:.1f}%"


def main() -> int:
    args = parse_args()
    run_dir = Path(args.run_dir)
    analysis_dir = Path(args.analysis_dir) if args.analysis_dir else run_dir / "analysis_baseline"
    analysis_dir.mkdir(parents=True, exist_ok=True)

    features_path = analysis_dir / "features_all.csv"
    summary_path = analysis_dir / "summary_metrics.json"
    taxonomy_dist_path = analysis_dir / "taxonomy_distribution.csv"

    rows = read_csv(features_path)
    summary = load_summary(summary_path)
    tax_rows = read_csv(taxonomy_dist_path)

    popular_rows = [r for r in rows if r["cohort"] == "popular"]
    random_rows = [r for r in rows if r["cohort"] == "random"]
    selected: set[str] = set()

    picked = []
    picked.extend(bucket_pick(popular_rows, selected))
    picked.extend(bucket_pick(random_rows, selected))

    # fill-up to target size with balanced cohorts
    rng = random.Random(args.seed)
    need = max(args.review_size - len(picked), 0)
    if need > 0:
        pool_pop = [r for r in popular_rows if r["skill_id"] not in selected]
        pool_rnd = [r for r in random_rows if r["skill_id"] not in selected]
        rng.shuffle(pool_pop)
        rng.shuffle(pool_rnd)
        while need > 0 and (pool_pop or pool_rnd):
            if pool_pop and need > 0:
                r = pool_pop.pop()
                picked.append(r)
                selected.add(r["skill_id"])
                need -= 1
            if pool_rnd and need > 0:
                r = pool_rnd.pop()
                picked.append(r)
                selected.add(r["skill_id"])
                need -= 1

    # trim if over target; keep deterministic order by cohort then risk/file/words
    if len(picked) > args.review_size:
        picked = sorted(
            picked,
            key=lambda r: (
                r["cohort"],
                -to_int(r, "security_risk_score"),
                -to_int(r, "file_count"),
                -to_int(r, "skill_md_words"),
                r["skill_id"],
            ),
        )[: args.review_size]

    # derive bucket labels
    review_rows: list[dict[str, Any]] = []
    for r in picked:
        risk = to_int(r, "security_risk_score")
        files = to_int(r, "file_count")
        words = to_int(r, "skill_md_words")
        if risk > 0:
            reason = "security_high"
        elif files >= 8:
            reason = "structure_heavy"
        elif words >= 1200:
            reason = "instruction_long"
        else:
            reason = "balanced_fill"
        review_rows.extend(make_review_rows([r], run_dir, reason))

    # stable sort for human scanning
    review_rows = sorted(
        review_rows,
        key=lambda r: (
            r["cohort"],
            {"security_high": 0, "structure_heavy": 1, "instruction_long": 2, "balanced_fill": 3}.get(
                r["review_bucket"], 9
            ),
            -int(r["security_risk_score"]),
            -int(r["file_count"]),
            r["skill_id"],
        ),
    )

    review_candidates_path = analysis_dir / "manual_review_candidates.csv"
    review_template_path = analysis_dir / "manual_review_template.csv"
    write_csv(review_candidates_path, review_rows)
    write_csv(review_template_path, enrich_template(review_rows))

    # key deltas from taxonomy distribution
    tax_sorted = sorted(
        tax_rows,
        key=lambda r: abs(float(r["delta_rate_top_minus_random"])),
        reverse=True,
    )
    tax_delta_lines = []
    for r in tax_sorted[:6]:
        delta = float(r["delta_rate_top_minus_random"])
        direction = "Top > Random" if delta > 0 else "Random > Top"
        tax_delta_lines.append(
            f"- {r['label']}: {direction} by {abs(delta)*100:.1f}pp "
            f"(Top {float(r['top_rate'])*100:.1f}% vs Random {float(r['random_rate'])*100:.1f}%)"
        )

    top = summary["top"]
    rnd = summary["random"]
    top_c = summary["top_concentration"]
    rnd_c = summary["random_concentration"]
    popular_n = int(top["n"])
    random_n = int(rnd["n"])

    brief_lines = [
        "# Empirical Brief (Popular vs Random)",
        "",
        "## 1) Data Status",
        "",
        f"- Cohort size: Popular={popular_n}, Random={random_n}",
        "- Download status: all selected skills have local content",
        "",
        "## 2) Structural Differences",
        "",
        f"- Avg file count: Popular {top['avg_file_count']:.2f} vs Random {rnd['avg_file_count']:.2f}",
        f"- Avg SKILL.md words: Popular {top['avg_skill_md_words']:.1f} vs Random {rnd['avg_skill_md_words']:.1f}",
        f"- Script presence: Popular {pct(top['rate_has_scripts'])} vs Random {pct(rnd['rate_has_scripts'])}",
        f"- Template presence: Popular {pct(top['rate_has_templates'])} vs Random {pct(rnd['rate_has_templates'])}",
        f"- Docs-folder presence: Popular {pct(top['rate_has_docs'])} vs Random {pct(rnd['rate_has_docs'])}",
        "",
        "## 3) Composition Bias / Concentration",
        "",
        f"- Popular cohort unique repos: {top_c['unique_repos']} (Random: {rnd_c['unique_repos']})",
        f"- Popular cohort dominant repo: {top_c['top_repo']} ({pct(top_c['top_repo_share'])})",
        f"- Random cohort dominant repo: {rnd_c['top_repo']} ({pct(rnd_c['top_repo_share'])})",
        "- Interpretation: the popular cohort is more concentrated, so some differences may reflect source-repo style.",
        "",
        "## 4) Taxonomy Delta (Largest Gaps)",
        "",
        *tax_delta_lines,
        "",
        "## 5) Security Signal Snapshot",
        "",
        f"- Risk-signal rate: Popular {pct(top['rate_has_security_risk_signal'])} vs Random {pct(rnd['rate_has_security_risk_signal'])}",
        f"- Avg risk score: Popular {top['avg_security_risk_score']:.2f} vs Random {rnd['avg_security_risk_score']:.2f}",
        "- Note: security findings are rule-based and need manual validation.",
        "",
        "## 6) Manual Review Plan",
        "",
        f"- Manual review queue prepared: {len(review_rows)} skills",
        "- Stratification: security-high + structure-heavy + long-instruction + balanced-fill",
        "- Annotation template includes taxonomy correction, boundary quality, security controls/risks, and overall quality.",
    ]

    brief_path = analysis_dir / "empirical_brief.md"
    brief_path.write_text("\n".join(brief_lines), encoding="utf-8")

    print(f"[INFO] review candidates: {review_candidates_path}")
    print(f"[INFO] review template: {review_template_path}")
    print(f"[INFO] brief: {brief_path}")
    print(f"[INFO] review size: {len(review_rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
