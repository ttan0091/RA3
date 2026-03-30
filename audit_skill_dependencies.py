#!/usr/bin/env python3
"""
Audit high-precision cross-skill dependency evidence in sampled skills.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import random
import re
from concurrent.futures import ThreadPoolExecutor
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


TEXT_EXTENSIONS = {
    ".md",
    ".txt",
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

IGNORE_DIRS = {
    "node_modules",
    "dist",
    "build",
    ".next",
    "coverage",
    "vendor",
    "venv",
    ".venv",
    "target",
    "out",
}

PLACEHOLDER_NAMES = {
    "arguments",
    "project",
    "utils",
    "input_json",
    "description",
    "subagent",
    "this",
    "that",
    "another",
    "any",
}

RELATIVE_SKILL_LINK_RE = re.compile(r"\]\(([^)]*?/SKILL\.md)\)", re.IGNORECASE)
PATH_REF_RE = re.compile(
    r"(?:~?/?.*?\.claude/skills|/mnt/skills|/Users/[^/\s]+/.claude/skills)/([A-Za-z0-9._-]+)/",
    re.IGNORECASE,
)
EXPLICIT_SKILL_REFS = [
    re.compile(r"see the \*\*?([A-Za-z0-9._-]+)\*\*? skill", re.IGNORECASE),
    re.compile(r"use ([A-Za-z0-9._-]+) skill", re.IGNORECASE),
    re.compile(r"invoke ([A-Za-z0-9._-]+) skill", re.IGNORECASE),
    re.compile(r"terminal state is invoking ([A-Za-z0-9._-]+)", re.IGNORECASE),
    re.compile(r"the only skill you invoke .*? is ([A-Za-z0-9._-]+)", re.IGNORECASE),
]


@dataclass
class SkillRecord:
    cohort: str
    skill_id: str
    skill_name: str
    repo_slug: str
    skill_dirname: str
    content_dir: Path


@dataclass(frozen=True)
class TargetRecord:
    skill_id: str
    skill_name: str
    repo_slug: str
    skill_dirname: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit high-precision skill dependency evidence.")
    parser.add_argument(
        "--sample-dir",
        default="skills_data/sampled_skills_1000",
        help="Directory containing popular/ and random/ skill cohorts.",
    )
    parser.add_argument(
        "--output-dir",
        default="skills_data/sampled_skills_1000/analysis_baseline",
        help="Directory where audit artifacts will be written.",
    )
    parser.add_argument(
        "--metadata-json",
        default="skills_data/skills_metadata.json",
        help="Global skill metadata used to improve target-name resolution.",
    )
    parser.add_argument(
        "--review-sample-size",
        type=int,
        default=120,
        help="Max number of rows to keep in dependency_review_sample.csv.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=20260309,
        help="Random seed for review sample selection.",
    )
    parser.add_argument(
        "--max-skills-per-cohort",
        type=int,
        default=0,
        help="Optional cap for smoke tests. 0 means all skills.",
    )
    parser.add_argument(
        "--max-file-bytes",
        type=int,
        default=524288,
        help="Skip very large files during auditing to keep the scan high-precision and fast.",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=max(1, min(8, os.cpu_count() or 1)),
        help="Number of worker threads to use for per-skill scanning.",
    )
    return parser.parse_args()


def safe_read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="ignore")


def repo_slug_from_url(url: str) -> str:
    parsed = urlparse(url)
    parts = [x for x in parsed.path.split("/") if x]
    if len(parts) >= 2:
        return f"{parts[0]}/{parts[1]}"
    return "unknown/unknown"


def iter_text_files(content_dir: Path, max_file_bytes: int) -> list[Path]:
    files: list[Path] = []
    for path in content_dir.rglob("*"):
        if not path.is_file():
            continue
        if any(part in IGNORE_DIRS for part in path.relative_to(content_dir).parts):
            continue
        if max_file_bytes > 0 and path.stat().st_size > max_file_bytes:
            continue
        if path.suffix.lower() in TEXT_EXTENSIONS or path.name == "SKILL.md":
            files.append(path)
    return files


def normalize_name(name: str) -> str:
    return re.sub(r"[^a-z0-9._-]+", "-", name.lower()).strip("-")


def extract_candidate_from_link(link_target: str) -> str:
    link_path = Path(link_target)
    parts = [p for p in link_path.parts if p not in {".", ".."}]
    if len(parts) >= 2 and parts[-1].lower() == "skill.md":
        return parts[-2]
    if len(parts) >= 1 and parts[-1].lower() == "skill.md":
        return parts[0]
    return ""


def build_skill_index(sample_dir: Path, max_skills_per_cohort: int) -> tuple[list[SkillRecord], dict[str, list[SkillRecord]]]:
    records: list[SkillRecord] = []
    name_index: dict[str, list[TargetRecord]] = defaultdict(list)
    alias_seen: dict[str, set[str]] = defaultdict(set)
    for cohort in ["popular", "random"]:
        cohort_dir = sample_dir / cohort
        skill_dirs = sorted(p for p in cohort_dir.iterdir() if p.is_dir())
        if max_skills_per_cohort > 0:
            skill_dirs = skill_dirs[:max_skills_per_cohort]
        for skill_dir in skill_dirs:
            metadata = json.loads((skill_dir / "metadata.json").read_text(encoding="utf-8"))
            skill = metadata.get("skill", {})
            record = SkillRecord(
                cohort=cohort,
                skill_id=str(skill.get("id", skill_dir.name)),
                skill_name=str(skill.get("name", "")),
                repo_slug=repo_slug_from_url(str(skill.get("githubUrl", ""))),
                skill_dirname=skill_dir.name,
                content_dir=skill_dir / "content",
            )
            records.append(record)

            aliases = {
                normalize_name(record.skill_name),
                normalize_name(record.skill_id),
                normalize_name(record.skill_dirname),
            }
            for alias in aliases:
                if alias and record.skill_id not in alias_seen[alias]:
                    name_index[alias].append(
                        TargetRecord(
                            skill_id=record.skill_id,
                            skill_name=record.skill_name,
                            repo_slug=record.repo_slug,
                            skill_dirname=record.skill_dirname,
                        )
                    )
                    alias_seen[alias].add(record.skill_id)
    return records, name_index


def extend_skill_index_with_metadata(
    metadata_json: Path,
    name_index: dict[str, list[TargetRecord]],
) -> None:
    if not metadata_json.exists():
        return

    payload = json.loads(metadata_json.read_text(encoding="utf-8"))
    skills = payload.get("skills", []) if isinstance(payload, dict) else payload
    alias_seen: dict[str, set[str]] = defaultdict(set)
    for alias, records in name_index.items():
        alias_seen[alias].update(record.skill_id for record in records)

    for skill in skills:
        skill_id = str(skill.get("id", "")).strip()
        if not skill_id:
            continue
        skill_name = str(skill.get("name", "")).strip()
        repo_slug = repo_slug_from_url(str(skill.get("githubUrl", "")))
        skill_dirname = skill_id
        aliases = {
            normalize_name(skill_name),
            normalize_name(skill_id),
            normalize_name(skill_dirname),
        }
        for alias in aliases:
            if not alias or skill_id in alias_seen[alias]:
                continue
            name_index[alias].append(
                TargetRecord(
                    skill_id=skill_id,
                    skill_name=skill_name,
                    repo_slug=repo_slug,
                    skill_dirname=skill_dirname,
                )
            )
            alias_seen[alias].add(skill_id)


def resolve_target(
    source: SkillRecord,
    candidate_name: str,
    name_index: dict[str, list[TargetRecord]],
) -> tuple[str, str, str]:
    normalized = normalize_name(candidate_name)
    if not normalized or normalized in PLACEHOLDER_NAMES:
        return "", "", "unresolved"

    matches = [record for record in name_index.get(normalized, []) if record.skill_id != source.skill_id]
    if not matches:
        return "", normalized, "unresolved"

    same_repo = [record for record in matches if record.repo_slug == source.repo_slug]
    if len(same_repo) == 1:
        return same_repo[0].skill_id, normalized, "same_repo_unique"
    if len(matches) == 1:
        return matches[0].skill_id, normalized, "global_unique"
    return "", normalized, "ambiguous"


def make_row(
    source: SkillRecord,
    target_skill_id: str,
    target_candidate: str,
    resolution: str,
    evidence_type: str,
    confidence: str,
    evidence_text: str,
    file_path: Path,
    line_no: int,
) -> dict[str, Any]:
    return {
        "cohort": source.cohort,
        "source_skill_id": source.skill_id,
        "source_skill_name": source.skill_name,
        "source_repo": source.repo_slug,
        "target_skill_id": target_skill_id,
        "target_candidate": target_candidate,
        "resolution": resolution,
        "evidence_type": evidence_type,
        "confidence": confidence,
        "local_path": str(file_path),
        "line_no": line_no,
        "evidence_text": evidence_text.strip(),
    }


def extract_rows_for_file(
    source: SkillRecord,
    file_path: Path,
    name_index: dict[str, list[TargetRecord]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    text = safe_read_text(file_path)
    rel_path = file_path.relative_to(source.content_dir)

    for line_no, line in enumerate(text.splitlines(), start=1):
        for match in RELATIVE_SKILL_LINK_RE.finditer(line):
            candidate = extract_candidate_from_link(match.group(1))
            if not candidate:
                continue
            target_skill_id, normalized, resolution = resolve_target(source, candidate, name_index)
            rows.append(
                make_row(
                    source=source,
                    target_skill_id=target_skill_id,
                    target_candidate=normalized or candidate,
                    resolution=resolution,
                    evidence_type="relative_skill_link",
                    confidence="high",
                    evidence_text=line,
                    file_path=source.content_dir / rel_path,
                    line_no=line_no,
                )
            )

        for match in PATH_REF_RE.finditer(line):
            candidate = match.group(1)
            target_skill_id, normalized, resolution = resolve_target(source, candidate, name_index)
            if normalized in PLACEHOLDER_NAMES:
                continue
            rows.append(
                make_row(
                    source=source,
                    target_skill_id=target_skill_id,
                    target_candidate=normalized or candidate,
                    resolution=resolution,
                    evidence_type="skill_path_reference",
                    confidence="high",
                    evidence_text=line,
                    file_path=source.content_dir / rel_path,
                    line_no=line_no,
                )
            )

        for pattern in EXPLICIT_SKILL_REFS:
            for match in pattern.finditer(line):
                candidate = match.group(1)
                if normalize_name(candidate) in PLACEHOLDER_NAMES:
                    continue
                target_skill_id, normalized, resolution = resolve_target(source, candidate, name_index)
                confidence = "medium" if resolution == "ambiguous" else "high"
                evidence_type = "workflow_invocation" if "invoke" in pattern.pattern or "terminal state" in pattern.pattern else "explicit_skill_reference"
                rows.append(
                    make_row(
                        source=source,
                        target_skill_id=target_skill_id,
                        target_candidate=normalized or candidate,
                        resolution=resolution,
                        evidence_type=evidence_type,
                        confidence=confidence,
                        evidence_text=line,
                        file_path=source.content_dir / rel_path,
                        line_no=line_no,
                    )
                )

    deduped: list[dict[str, Any]] = []
    seen: set[tuple[str, str, str, str, int]] = set()
    for row in rows:
        key = (
            row["source_skill_id"],
            row["target_candidate"],
            row["evidence_type"],
            row["local_path"],
            row["line_no"],
        )
        if key in seen:
            continue
        seen.add(key)
        deduped.append(row)
    return deduped


def extract_rows_for_record(
    record: SkillRecord,
    name_index: dict[str, list[TargetRecord]],
    max_file_bytes: int,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not record.content_dir.exists():
        return rows
    for file_path in iter_text_files(record.content_dir, max_file_bytes):
        rows.extend(extract_rows_for_file(record, file_path, name_index))
    return rows


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fieldnames = list(rows[0].keys())
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def build_review_sample(rows: list[dict[str, Any]], limit: int, seed: int) -> list[dict[str, Any]]:
    rng = random.Random(seed)
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[(row["evidence_type"], row["confidence"])].append(row)

    picked: list[dict[str, Any]] = []
    for group_rows in grouped.values():
        rng.shuffle(group_rows)
        picked.extend(group_rows[: min(20, len(group_rows))])

    if len(picked) > limit:
        rng.shuffle(picked)
        picked = picked[:limit]

    enriched = []
    for row in picked:
        x = dict(row)
        x.update(
            {
                "reviewer": "",
                "is_true_dependency": "",
                "target_corrected": "",
                "mechanism_label": "",
                "notes": "",
            }
        )
        enriched.append(x)
    return enriched


def build_audit_markdown(rows: list[dict[str, Any]]) -> str:
    cohort_counter = Counter(row["cohort"] for row in rows)
    evidence_counter = Counter(row["evidence_type"] for row in rows)
    resolution_counter = Counter(row["resolution"] for row in rows)
    resolved_targets = Counter(row["target_skill_id"] for row in rows if row["target_skill_id"])

    lines = [
        "# Dependency Audit",
        "",
        "## Summary",
        "",
        f"- Total evidence rows: {len(rows)}",
        f"- Popular rows: {cohort_counter.get('popular', 0)}",
        f"- Random rows: {cohort_counter.get('random', 0)}",
        "",
        "## Evidence Types",
        "",
    ]
    for evidence_type, count in sorted(evidence_counter.items()):
        lines.append(f"- {evidence_type}: {count}")

    lines.extend(
        [
            "",
            "## Resolution",
            "",
        ]
    )
    for resolution, count in sorted(resolution_counter.items()):
        lines.append(f"- {resolution}: {count}")

    lines.extend(
        [
            "",
            "## Top Resolved Targets",
            "",
        ]
    )
    if resolved_targets:
        for target, count in resolved_targets.most_common(10):
            lines.append(f"- {target}: {count}")
    else:
        lines.append("- No resolved targets found.")

    lines.extend(
        [
            "",
            "## Example Rows",
            "",
        ]
    )
    for row in rows[:10]:
        lines.append(
            f"- `{row['source_skill_id']}` -> `{row['target_skill_id'] or row['target_candidate']}` "
            f"[{row['evidence_type']}, {row['confidence']}] "
            f"{row['local_path']}:{row['line_no']}"
        )

    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    sample_dir = Path(args.sample_dir)
    output_dir = Path(args.output_dir)
    metadata_json = Path(args.metadata_json)
    output_dir.mkdir(parents=True, exist_ok=True)

    records, name_index = build_skill_index(sample_dir, args.max_skills_per_cohort)
    extend_skill_index_with_metadata(metadata_json, name_index)
    rows: list[dict[str, Any]] = []
    if args.workers <= 1:
        for record in records:
            rows.extend(extract_rows_for_record(record, name_index, args.max_file_bytes))
    else:
        with ThreadPoolExecutor(max_workers=args.workers) as executor:
            futures = [
                executor.submit(extract_rows_for_record, record, name_index, args.max_file_bytes)
                for record in records
            ]
            for future in futures:
                rows.extend(future.result())

    rows = sorted(
        rows,
        key=lambda row: (
            row["cohort"],
            row["source_skill_id"],
            row["target_candidate"],
            row["evidence_type"],
            row["local_path"],
            row["line_no"],
        ),
    )

    write_csv(output_dir / "dependency_candidates.csv", rows)
    write_csv(
        output_dir / "dependency_review_sample.csv",
        build_review_sample(rows, args.review_sample_size, args.seed),
    )
    (output_dir / "dependency_audit.md").write_text(
        build_audit_markdown(rows),
        encoding="utf-8",
    )

    print(f"[INFO] dependency rows: {len(rows)}")
    print(f"[INFO] output dir: {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
