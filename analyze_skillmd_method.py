#!/usr/bin/env python3
"""
Build WP3 artifacts for SKILL.md methodology analysis.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import statistics
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any


TRIGGER_PATTERNS = [
    r"\buse (?:this|the) skill when\b",
    r"\bthis skill (?:is|can be) (?:used|for)\b",
    r"\bwhen to use\b",
    r"\buse when\b",
    r"\bprerequisites?\b",
    r"\bpreconditions?\b",
    r"\bbefore you start\b",
    r"\bif you need to\b",
]

CONSTRAINT_PATTERNS = [
    r"\bdo not\b",
    r"\bdon't\b",
    r"\bmust not\b",
    r"\bnever\b",
    r"\bavoid\b",
    r"\bonly if\b",
    r"\bunless\b",
    r"\blimit(?:ation|s)?\b",
    r"\bguardrail(?:s)?\b",
]

ERROR_PATTERNS = [
    r"\bif .* fails\b",
    r"\bfallback\b",
    r"\botherwise\b",
    r"\btroubleshoot(?:ing)?\b",
    r"\bretry\b",
    r"\brollback\b",
    r"\brecover(?:y)?\b",
    r"\bif unavailable\b",
    r"\bon error\b",
]

IO_PATTERNS = [
    r"\binput(?:s)?\b",
    r"\boutput(?:s)?\b",
    r"\barguments?\b",
    r"\bparameters?\b",
    r"\brequired (?:fields?|variables?|files?)\b",
    r"\breturns?\b",
    r"\bproduces?\b",
    r"\bformat\b",
    r"\bschema\b",
    r"\bwrite to\b",
    r"\bread from\b",
]

SEQUENCE_PATTERNS = [
    r"\bfirst\b",
    r"\bthen\b",
    r"\bnext\b",
    r"\bfinally\b",
    r"\bstep\b",
    r"\bworkflow\b",
]

EXAMPLE_PATTERNS = [
    r"\bexample(?:s)?\b",
    r"\bfor example\b",
    r"\be\.g\.\b",
    r"\bfor instance\b",
]

DSL_PATTERNS = [
    r"\bDSL\b",
    r"\bgrammar\b",
    r"\bBNF\b",
    r"\bJSON schema\b",
    r"\bOpenAPI\b",
]

LOGIC_MATH_PATTERNS = [
    r"\$\$",
    r"\\\(",
    r"\\\)",
    r"\btheorem\b",
    r"\biff\b",
    r"[∀∃⇒⇔∧∨]",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build WP3 SKILL.md methodology artifacts.")
    parser.add_argument(
        "--run-dir",
        default="skills_data/sampled_skills_1000",
        help="Directory containing sampled popular/random cohorts.",
    )
    parser.add_argument(
        "--analysis-dir",
        default="skills_data/sampled_skills_1000/analysis_baseline",
        help="Directory where WP3 artifacts will be written.",
    )
    parser.add_argument(
        "--manual-labels",
        default="skills_data/sampled_skills_1000/analysis_baseline/manual_labels.csv",
        help="Adjudicated manual label file.",
    )
    parser.add_argument(
        "--pilot-sample",
        default="skills_data/sampled_skills_1000/analysis_baseline/skillmd_pilot_sample.csv",
        help="Pilot sample used for manual coding.",
    )
    parser.add_argument(
        "--cohorts",
        nargs="+",
        default=["popular", "random"],
        help="Cohorts to score.",
    )
    parser.add_argument(
        "--max-skills-per-cohort",
        type=int,
        default=0,
        help="Optional cap for smoke tests. 0 means all skills.",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=max(1, min(8, os.cpu_count() or 1)),
        help="Number of worker threads to use for per-skill SKILL.md scoring.",
    )
    return parser.parse_args()


def safe_read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="ignore")


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fieldnames = list(rows[0].keys())
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def find_skill_md(content_dir: Path) -> Path | None:
    if not content_dir.exists():
        return None
    candidates = [path for path in content_dir.rglob("*") if path.is_file() and path.name.lower() == "skill.md"]
    if not candidates:
        return None
    candidates.sort(key=lambda path: (len(path.relative_to(content_dir).parts), str(path).lower()))
    return candidates[0]


def saturating_score(hit_count: int, thresholds: tuple[int, int], scores: tuple[int, int, int]) -> int:
    low_threshold, high_threshold = thresholds
    low_score, mid_score, high_score = scores
    if hit_count >= high_threshold:
        return high_score
    if hit_count >= low_threshold:
        return mid_score
    return low_score


def count_patterns(text: str, patterns: list[str]) -> int:
    return sum(len(re.findall(pattern, text, flags=re.IGNORECASE | re.MULTILINE)) for pattern in patterns)


def classify_spec_form(
    text: str,
    heading_count: int,
    ordered_list_count: int,
    bullet_list_count: int,
    code_fence_count: int,
    placeholder_count: int,
) -> str:
    structured_signal = (
        heading_count >= 6
        or ordered_list_count >= 3
        or bullet_list_count >= 8
        or placeholder_count >= 4
    )
    code_signal = code_fence_count >= 6
    dsl_signal = count_patterns(text, DSL_PATTERNS) > 0
    logic_signal = count_patterns(text, LOGIC_MATH_PATTERNS) > 0

    active = [structured_signal, code_signal, dsl_signal, logic_signal]
    if sum(1 for flag in active if flag) >= 2:
        return "mixed"
    if dsl_signal:
        return "dsl"
    if logic_signal:
        return "logic_math"
    if code_signal:
        return "code_pseudocode"
    if structured_signal:
        return "structured_template"
    return "natural_language"


def score_skill_dir(skill_dir: Path, cohort: str) -> dict[str, Any]:
    metadata = json.loads(safe_read_text(skill_dir / "metadata.json"))
    skill = metadata.get("skill", {})
    content_dir = skill_dir / "content"
    skill_md_path = find_skill_md(content_dir)
    text = safe_read_text(skill_md_path) if skill_md_path else ""

    heading_count = len(re.findall(r"^\s*#{1,6}\s+", text, flags=re.MULTILINE))
    ordered_list_count = len(re.findall(r"^\s*\d+\.\s+", text, flags=re.MULTILINE))
    bullet_list_count = len(re.findall(r"^\s*[-*]\s+", text, flags=re.MULTILINE))
    code_fence_count = text.count("```") // 2
    placeholder_count = len(re.findall(r"\$[A-Z_][A-Z0-9_]*|\{[a-zA-Z_][a-zA-Z0-9_.-]*\}", text))

    trigger_hits = count_patterns(text, TRIGGER_PATTERNS)
    constraint_hits = count_patterns(text, CONSTRAINT_PATTERNS)
    error_hits = count_patterns(text, ERROR_PATTERNS)
    io_hits = count_patterns(text, IO_PATTERNS)
    sequence_hits = count_patterns(text, SEQUENCE_PATTERNS)
    example_hits = count_patterns(text, EXAMPLE_PATTERNS)

    trigger_score = saturating_score(trigger_hits, (1, 2), (0, 10, 20))
    constraint_score = saturating_score(constraint_hits, (1, 2), (0, 10, 20))
    step_score = 15 if (ordered_list_count >= 2 or sequence_hits >= 3) else 8 if (ordered_list_count >= 1 or sequence_hits >= 1) else 0
    error_score = saturating_score(error_hits, (1, 2), (0, 8, 15))
    io_score = 15 if (io_hits >= 2 or placeholder_count >= 2) else 8 if (io_hits >= 1 or placeholder_count >= 1) else 0
    example_score = 15 if (example_hits >= 2 or code_fence_count >= 2) else 8 if (example_hits >= 1 or code_fence_count >= 1) else 0

    spec_form = classify_spec_form(
        text=text,
        heading_count=heading_count,
        ordered_list_count=ordered_list_count,
        bullet_list_count=bullet_list_count,
        code_fence_count=code_fence_count,
        placeholder_count=placeholder_count,
    )

    return {
        "cohort": cohort,
        "skill_id": str(skill.get("id", skill_dir.name)),
        "skill_name": str(skill.get("name", "")),
        "skill_md_path": str(skill_md_path) if skill_md_path else "",
        "trigger_hits": trigger_hits,
        "constraint_hits": constraint_hits,
        "error_hits": error_hits,
        "io_hits": io_hits,
        "sequence_hits": sequence_hits,
        "example_hits": example_hits,
        "heading_count": heading_count,
        "ordered_list_count": ordered_list_count,
        "bullet_list_count": bullet_list_count,
        "code_fence_count": code_fence_count,
        "placeholder_count": placeholder_count,
        "spec_form_auto": spec_form,
        "trigger_score": trigger_score,
        "constraint_score": constraint_score,
        "step_score": step_score,
        "error_score": error_score,
        "io_score": io_score,
        "example_score": example_score,
        "structuredness_score": trigger_score + constraint_score + step_score + error_score + io_score + example_score,
    }


def iter_skill_dirs(run_dir: Path, cohort: str, max_skills: int) -> list[Path]:
    cohort_dir = run_dir / cohort
    skill_dirs = sorted(path for path in cohort_dir.iterdir() if path.is_dir())
    if max_skills > 0:
        return skill_dirs[:max_skills]
    return skill_dirs


def to_float(values: list[float]) -> float:
    if not values:
        return 0.0
    return float(statistics.fmean(values))


def median(values: list[float]) -> float:
    if not values:
        return 0.0
    return float(statistics.median(values))


def cohen_kappa(left: list[str], right: list[str]) -> float:
    if not left or len(left) != len(right):
        return 0.0
    categories = sorted(set(left) | set(right))
    n = len(left)
    observed = sum(1 for a, b in zip(left, right) if a == b) / n
    left_probs = {category: left.count(category) / n for category in categories}
    right_probs = {category: right.count(category) / n for category in categories}
    expected = sum(left_probs[c] * right_probs[c] for c in categories)
    if expected >= 1.0:
        return 1.0
    return (observed - expected) / (1.0 - expected)


def to_binary_component(value: str) -> int:
    return 1 if str(value).strip() in {"1", "true", "True"} else 0


def example_component_score(value: str) -> int:
    normalized = str(value).strip()
    if normalized == "2":
        return 15
    if normalized == "1":
        return 8
    return 0


def build_manual_label_summary(manual_rows: list[dict[str, str]]) -> tuple[dict[str, float], list[dict[str, Any]]]:
    if not manual_rows:
        return {}, []

    kappa_fields = [
        "has_trigger_condition",
        "has_constraints",
        "has_error_fallback",
        "has_io_spec",
        "spec_form",
        "has_stepwise_procedure",
        "example_quality",
    ]
    kappa_summary: dict[str, float] = {}
    for field in kappa_fields:
        left = [row[f"rater_a_{field}"] for row in manual_rows]
        right = [row[f"rater_b_{field}"] for row in manual_rows]
        kappa_summary[field] = cohen_kappa(left, right)

    resolved_rows: list[dict[str, Any]] = []
    for row in manual_rows:
        resolved_score = (
            20 * to_binary_component(row["resolved_has_trigger_condition"])
            + 20 * to_binary_component(row["resolved_has_constraints"])
            + 15 * to_binary_component(row["resolved_has_stepwise_procedure"])
            + 15 * to_binary_component(row["resolved_has_error_fallback"])
            + 15 * to_binary_component(row["resolved_has_io_spec"])
            + example_component_score(row["resolved_example_quality"])
        )
        resolved_rows.append(
            {
                "cohort": row["cohort"],
                "review_bucket": row["review_bucket"],
                "skill_id": row["skill_id"],
                "skill_name": row["skill_name"],
                "skill_md_path": row["skill_md_path"],
                "rater_a_has_trigger_condition": row["rater_a_has_trigger_condition"],
                "rater_b_has_trigger_condition": row["rater_b_has_trigger_condition"],
                "resolved_has_trigger_condition": row["resolved_has_trigger_condition"],
                "rater_a_has_constraints": row["rater_a_has_constraints"],
                "rater_b_has_constraints": row["rater_b_has_constraints"],
                "resolved_has_constraints": row["resolved_has_constraints"],
                "rater_a_has_error_fallback": row["rater_a_has_error_fallback"],
                "rater_b_has_error_fallback": row["rater_b_has_error_fallback"],
                "resolved_has_error_fallback": row["resolved_has_error_fallback"],
                "rater_a_has_io_spec": row["rater_a_has_io_spec"],
                "rater_b_has_io_spec": row["rater_b_has_io_spec"],
                "resolved_has_io_spec": row["resolved_has_io_spec"],
                "rater_a_spec_form": row["rater_a_spec_form"],
                "rater_b_spec_form": row["rater_b_spec_form"],
                "resolved_spec_form": row["resolved_spec_form"],
                "rater_a_has_stepwise_procedure": row["rater_a_has_stepwise_procedure"],
                "rater_b_has_stepwise_procedure": row["rater_b_has_stepwise_procedure"],
                "resolved_has_stepwise_procedure": row["resolved_has_stepwise_procedure"],
                "rater_a_example_quality": row["rater_a_example_quality"],
                "rater_b_example_quality": row["rater_b_example_quality"],
                "resolved_example_quality": row["resolved_example_quality"],
                "resolved_structuredness_score": resolved_score,
                "adjudication_notes": row.get("adjudication_notes", ""),
            }
        )
    return kappa_summary, resolved_rows


def build_method_results(
    score_rows: list[dict[str, Any]],
    manual_rows: list[dict[str, Any]],
    kappa_summary: dict[str, float],
    pilot_rows: list[dict[str, str]],
) -> str:
    grouped_scores: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in score_rows:
        grouped_scores[row["cohort"]].append(row)

    lines = [
        "# SKILL.md Method Results",
        "",
        "## Pilot",
        "",
        f"- Pilot sample rows: {len(pilot_rows)}",
        f"- Manual labels available: {len(manual_rows)}",
    ]

    if kappa_summary:
        lines.extend(["", "## Cohen's Kappa", ""])
        for field, value in sorted(kappa_summary.items()):
            lines.append(f"- {field}: {value:.3f}")

    lines.extend(["", "## Structuredness Score", ""])
    for cohort in ["popular", "random"]:
        cohort_rows = grouped_scores.get(cohort, [])
        values = [float(row["structuredness_score"]) for row in cohort_rows]
        lines.append(
            f"- {cohort}: n={len(values)}, mean={to_float(values):.2f}, median={median(values):.2f}"
        )

    spec_counter: dict[str, Counter[str]] = defaultdict(Counter)
    for row in score_rows:
        spec_counter[row["cohort"]][row["spec_form_auto"]] += 1

    lines.extend(["", "## Auto Spec Form Distribution", ""])
    for cohort in ["popular", "random"]:
        parts = [f"{label}:{count}" for label, count in spec_counter.get(cohort, Counter()).most_common()]
        lines.append(f"- {cohort}: {'; '.join(parts) if parts else 'none'}")

    if manual_rows:
        resolved_counter: dict[str, Counter[str]] = defaultdict(Counter)
        resolved_scores: dict[str, list[int]] = defaultdict(list)
        for row in manual_rows:
            resolved_counter[row["cohort"]][row["resolved_spec_form"]] += 1
            resolved_scores[row["cohort"]].append(int(row["resolved_structuredness_score"]))

        lines.extend(["", "## Pilot Resolved Labels", ""])
        for cohort in ["popular", "random"]:
            spec_parts = [f"{label}:{count}" for label, count in resolved_counter.get(cohort, Counter()).most_common()]
            score_values = resolved_scores.get(cohort, [])
            lines.append(
                f"- {cohort}: resolved_mean={to_float(score_values):.2f}, resolved_median={median(score_values):.2f}, "
                f"spec_forms={' ; '.join(spec_parts) if spec_parts else 'none'}"
            )

    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- Structuredness score is heuristic and auditable; it is not a causal quality measure.",
            "- Pilot kappa is based on blind dual coding over the fixed pilot sample.",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    run_dir = Path(args.run_dir)
    analysis_dir = Path(args.analysis_dir)
    analysis_dir.mkdir(parents=True, exist_ok=True)

    tasks: list[tuple[Path, str]] = []
    for cohort in args.cohorts:
        for skill_dir in iter_skill_dirs(run_dir, cohort, args.max_skills_per_cohort):
            tasks.append((skill_dir, cohort))

    score_rows: list[dict[str, Any]] = []
    if args.workers <= 1:
        for skill_dir, cohort in tasks:
            score_rows.append(score_skill_dir(skill_dir, cohort))
    else:
        with ThreadPoolExecutor(max_workers=args.workers) as executor:
            futures = [executor.submit(score_skill_dir, skill_dir, cohort) for skill_dir, cohort in tasks]
            for future in futures:
                score_rows.append(future.result())

    score_rows = sorted(score_rows, key=lambda row: (row["cohort"], row["skill_id"]))
    write_csv(analysis_dir / "structuredness_score.csv", score_rows)

    manual_source_rows = read_csv(Path(args.manual_labels))
    kappa_summary, manual_rows = build_manual_label_summary(manual_source_rows)
    if manual_rows:
        write_csv(analysis_dir / "manual_labels.csv", manual_rows)

    pilot_rows = read_csv(Path(args.pilot_sample))
    (analysis_dir / "method_results_skillmd.md").write_text(
        build_method_results(score_rows, manual_rows, kappa_summary, pilot_rows),
        encoding="utf-8",
    )

    print(f"[INFO] output_dir={analysis_dir}")
    print(f"[INFO] structuredness_rows={len(score_rows)}")
    print(f"[INFO] manual_rows={len(manual_rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
