#!/usr/bin/env python3
"""
Run the baseline pipeline described in 3.2/plan.md against the local sampled skills.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the phase-0/baseline analysis pipeline.")
    parser.add_argument(
        "--sample-dir",
        default="skills_data/sampled_skills_1000",
        help="Directory containing popular/ and random/ sampled skill cohorts.",
    )
    parser.add_argument(
        "--output-dir",
        default="skills_data/sampled_skills_1000/analysis_baseline",
        help="Directory where baseline artifacts will be written.",
    )
    parser.add_argument(
        "--docs-dir",
        default="3.2",
        help="Directory where phase-0 protocol docs will be written.",
    )
    parser.add_argument(
        "--skip-wp1",
        action="store_true",
        help="Skip dependency auditing even if the script exists.",
    )
    parser.add_argument(
        "--skip-wp4",
        action="store_true",
        help="Skip artifact analysis even if the script exists.",
    )
    return parser.parse_args()


def run_cmd(cmd: list[str], cwd: Path) -> None:
    subprocess.run(cmd, cwd=cwd, check=True)


def count_skill_dirs(sample_dir: Path, cohort: str) -> int:
    cohort_dir = sample_dir / cohort
    if not cohort_dir.exists():
        return 0
    return sum(1 for p in cohort_dir.iterdir() if p.is_dir())


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")


def build_run_manifest(
    sample_dir: Path,
    output_dir: Path,
    docs_dir: Path,
    dependency_script: Path,
    artifact_script: Path,
    skillmd_script: Path,
    wp1_executed: bool,
    wp4_executed: bool,
    wp3_executed: bool,
) -> dict[str, Any]:
    optional_outputs = {
        "dependency_candidates.csv": (output_dir / "dependency_candidates.csv").exists(),
        "dependency_audit.md": (output_dir / "dependency_audit.md").exists(),
        "script_ops.csv": (output_dir / "script_ops.csv").exists(),
        "example_stats.csv": (output_dir / "example_stats.csv").exists(),
        "data_asset_stats.csv": (output_dir / "data_asset_stats.csv").exists(),
        "artifact_profile.md": (output_dir / "artifact_profile.md").exists(),
        "structuredness_score.csv": (output_dir / "structuredness_score.csv").exists(),
        "manual_labels.csv": (output_dir / "manual_labels.csv").exists(),
        "method_results_skillmd.md": (output_dir / "method_results_skillmd.md").exists(),
    }
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "comparison_scope": ["popular", "random"],
        "sample_dir": str(sample_dir),
        "output_dir": str(output_dir),
        "docs_dir": str(docs_dir),
        "sample_counts": {
            "popular": count_skill_dirs(sample_dir, "popular"),
            "random": count_skill_dirs(sample_dir, "random"),
        },
        "source_files": {
            "metadata": "skills_data/skills_metadata.json",
            "popular_manifest": str(sample_dir / "manifests" / "popular_top.json"),
            "random_manifest": str(sample_dir / "manifests" / "random_sample.json"),
            "combined_manifest": str(sample_dir / "manifests" / "combined_sample.json"),
        },
        "pipeline_scripts": {
            "baseline_analysis": "analyze_sampled_skills.py",
            "review_pack": "prepare_review_pack.py",
            "skillmd_method": skillmd_script.name if skillmd_script.exists() else None,
            "dependency_audit": dependency_script.name if dependency_script.exists() else None,
            "artifact_analysis": artifact_script.name if artifact_script.exists() else None,
        },
        "step_execution": {
            "wp3_skillmd_method": wp3_executed,
            "wp1_dependency_audit": wp1_executed,
            "wp4_artifact_analysis": wp4_executed,
        },
        "baseline_contract_files": [
            "features_all.csv",
            "summary_metrics.json",
            "taxonomy_distribution.csv",
            "manual_review_candidates.csv",
            "manual_review_template.csv",
            "empirical_brief.md",
        ],
        "optional_outputs_present": optional_outputs,
    }


def write_data_protocol(path: Path, manifest: dict[str, Any]) -> None:
    lines = [
        "# Data Protocol",
        "",
        "## Scope",
        "",
        "- Main comparison only uses two cohorts: `popular` and `random`.",
        "- Official skills are not treated as a separate cohort in this baseline pipeline.",
        "",
        "## Inputs",
        "",
        f"- Sample directory: `{manifest['sample_dir']}`",
        f"- Popular count: {manifest['sample_counts']['popular']}",
        f"- Random count: {manifest['sample_counts']['random']}",
        f"- Metadata source: `{manifest['source_files']['metadata']}`",
        "",
        "## Output Contract",
        "",
        f"- Baseline output directory: `{manifest['output_dir']}`",
        "- Core baseline files remain stable:",
        "  - `features_all.csv`",
        "  - `summary_metrics.json`",
        "  - `taxonomy_distribution.csv`",
        "- Review-pack generation reads those filenames directly.",
        "",
        "## Pipeline",
        "",
        "1. Run `analyze_sampled_skills.py` to build baseline cohort features.",
        "2. Run `prepare_review_pack.py` to build manual-review artifacts.",
        "3. Run `analyze_skillmd_method.py` for WP3 structuredness scoring.",
        "4. Optionally run `audit_skill_dependencies.py` for WP1.",
        "5. Optionally run `analyze_skill_artifacts.py` for WP4.",
    ]
    write_text(path, "\n".join(lines))


def build_analysis_baseline_text(output_dir: Path) -> str:
    summary_path = output_dir / "summary_metrics.json"
    if not summary_path.exists():
        return "# Analysis Baseline\n\nBaseline summary has not been generated yet."

    summary = read_json(summary_path)
    top = summary["top"]
    rnd = summary["random"]

    optional_outputs = [
        "dependency_candidates.csv",
        "dependency_audit.md",
        "script_ops.csv",
        "example_stats.csv",
        "data_asset_stats.csv",
        "artifact_profile.md",
        "structuredness_score.csv",
        "manual_labels.csv",
        "method_results_skillmd.md",
    ]
    optional_lines = [
        f"- `{name}`: {'present' if (output_dir / name).exists() else 'missing'}"
        for name in optional_outputs
    ]

    lines = [
        "# Analysis Baseline",
        "",
        "## Cohort Summary",
        "",
        f"- Popular sample size: {top['n']}",
        f"- Random sample size: {rnd['n']}",
        f"- Avg file count: Popular {top['avg_file_count']:.2f} vs Random {rnd['avg_file_count']:.2f}",
        f"- Avg SKILL.md words: Popular {top['avg_skill_md_words']:.1f} vs Random {rnd['avg_skill_md_words']:.1f}",
        f"- Script presence: Popular {top['rate_has_scripts']*100:.1f}% vs Random {rnd['rate_has_scripts']*100:.1f}%",
        "",
        "## Files Generated",
        "",
        "- Required baseline files:",
        "  - `features_all.csv`",
        "  - `summary_metrics.json`",
        "  - `taxonomy_distribution.csv`",
        "  - `manual_review_candidates.csv`",
        "  - `manual_review_template.csv`",
        "  - `empirical_brief.md`",
        "",
        "## Optional WP Outputs",
        "",
        *optional_lines,
        "",
        "## Notes",
        "",
        "- This baseline keeps the existing CSV/JSON filename contract intact.",
        "- Historical `analysis_v2` outputs remain untouched and can be used for comparison.",
    ]
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    repo_root = Path(__file__).resolve().parent
    sample_dir = (repo_root / args.sample_dir).resolve()
    output_dir = (repo_root / args.output_dir).resolve()
    docs_dir = (repo_root / args.docs_dir).resolve()

    output_dir.mkdir(parents=True, exist_ok=True)
    docs_dir.mkdir(parents=True, exist_ok=True)

    run_cmd(
        [
            sys.executable,
            "analyze_sampled_skills.py",
            "--run-dir",
            str(sample_dir),
            "--output-dir",
            str(output_dir),
        ],
        cwd=repo_root,
    )
    run_cmd(
        [
            sys.executable,
            "prepare_review_pack.py",
            "--run-dir",
            str(sample_dir),
            "--analysis-dir",
            str(output_dir),
        ],
        cwd=repo_root,
    )

    dependency_script = repo_root / "audit_skill_dependencies.py"
    artifact_script = repo_root / "analyze_skill_artifacts.py"
    skillmd_script = repo_root / "analyze_skillmd_method.py"

    wp3_executed = False
    if skillmd_script.exists():
        run_cmd(
            [
                sys.executable,
                str(skillmd_script),
                "--run-dir",
                str(sample_dir),
                "--analysis-dir",
                str(output_dir),
            ],
            cwd=repo_root,
        )
        wp3_executed = True

    wp1_executed = False
    if dependency_script.exists() and not args.skip_wp1:
        run_cmd(
            [
                sys.executable,
                str(dependency_script),
                "--sample-dir",
                str(sample_dir),
                "--output-dir",
                str(output_dir),
            ],
            cwd=repo_root,
        )
        wp1_executed = True

    wp4_executed = False
    if artifact_script.exists() and not args.skip_wp4:
        run_cmd(
            [
                sys.executable,
                str(artifact_script),
                "--run-dir",
                str(sample_dir),
                "--output-dir",
                str(output_dir),
            ],
            cwd=repo_root,
        )
        wp4_executed = True

    manifest = build_run_manifest(
        sample_dir=sample_dir,
        output_dir=output_dir,
        docs_dir=docs_dir,
        dependency_script=dependency_script,
        artifact_script=artifact_script,
        skillmd_script=skillmd_script,
        wp1_executed=wp1_executed,
        wp4_executed=wp4_executed,
        wp3_executed=wp3_executed,
    )
    write_json(docs_dir / "run_manifest.json", manifest)
    write_data_protocol(docs_dir / "data_protocol.md", manifest)
    write_text(docs_dir / "analysis_baseline.md", build_analysis_baseline_text(output_dir))

    print(f"[INFO] pipeline completed: {output_dir}")
    print(f"[INFO] docs written to: {docs_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
