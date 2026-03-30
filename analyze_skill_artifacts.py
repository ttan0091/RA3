#!/usr/bin/env python3
"""
Analyze sampled skill artifacts for WP4.

Outputs:
1. script_ops.csv
2. example_stats.csv
3. data_asset_stats.csv
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any


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

IGNORE_DIR_NAMES = {
    ".git",
    ".venv",
    "__pycache__",
    "venv",
    "node_modules",
    "dist",
    "build",
    "coverage",
    ".next",
}

EXAMPLE_DIR_HINTS = {"example", "examples", "sample", "samples"}
DATA_DIR_HINTS = {"data", "dataset", "datasets", "assets", "fixtures", "sample-data", "samples"}

TABULAR_EXTENSIONS = {".csv", ".tsv"}
JSON_LIKE_EXTENSIONS = {".json", ".jsonl", ".ndjson"}
DATABASE_EXTENSIONS = {".db", ".sqlite", ".sqlite3"}
BINARY_DATA_EXTENSIONS = {".parquet", ".feather", ".npy", ".npz", ".pkl", ".pickle"}
TEXT_DATA_EXTENSIONS = {".txt", ".md"}

CONFIG_LIKE_FILENAMES = {
    "package.json",
    "package-lock.json",
    "composer.json",
    "tsconfig.json",
    "jsconfig.json",
    "metadata.json",
    "_meta.json",
    "manifest.json",
    "wrangler.json",
    "settings.json",
    "launch.json",
}

SCRIPT_OP_PATTERNS: dict[str, list[tuple[str, str]]] = {
    "read": [
        ("python_open_read", r"open\s*\([^)]*,\s*[\"'][rb]{1,2}[\"']"),
        ("python_read_text", r"\.(read_text|read_bytes)\s*\("),
        ("python_json_load", r"\bjson\.load\s*\("),
        ("python_csv_reader", r"\bcsv\.(DictReader|reader)\s*\("),
        ("python_pd_read", r"\bpd\.read_[a-z_]+\s*\("),
        ("js_read_file", r"\b(readFile|readFileSync)\s*\("),
        ("go_read_file", r"\bos\.ReadFile\s*\("),
        ("shell_cat", r"(^|\s)(cat|less|head|tail|grep)\s+"),
    ],
    "write": [
        ("python_open_write", r"open\s*\([^)]*,\s*[\"'][wax+bt]{1,4}[\"']"),
        ("python_write_text", r"\.(write_text|write_bytes)\s*\("),
        ("python_json_dump", r"\bjson\.dump[s]?\s*\("),
        ("js_write_file", r"\b(writeFile|writeFileSync|appendFile|appendFileSync)\s*\("),
        ("shell_redirect", r"(>|>>)\s*[$\"'./A-Za-z0-9_-]+"),
        ("mkdir", r"\b(mkdir|makedirs|mkdirs)\b"),
        ("copy_move", r"\b(copy2|copytree|shutil\.copy|rename|replace|mv|cp)\b"),
    ],
    "delete": [
        ("python_remove", r"\b(os\.remove|os\.unlink|Path\.unlink|shutil\.rmtree)\b"),
        ("shell_rm", r"(^|\s)rm\s+-[rfRF]+|(^|\s)rm\s+"),
        ("js_unlink", r"\b(unlink|rmSync|rmdirSync|remove)\s*\("),
        ("go_remove", r"\bos\.Remove(All)?\s*\("),
    ],
    "exec": [
        ("python_subprocess", r"\b(subprocess\.(run|Popen|check_call|check_output)|os\.system)\b"),
        ("python_exec", r"\b(exec|eval)\s*\("),
        ("js_child_process", r"\b(exec|spawn|execSync|spawnSync)\s*\("),
        ("shell_interpreter", r"(^|\s)(python3?|node|bash|sh|zsh|pwsh|powershell|npm|pnpm|yarn|make|cargo|go)\s+"),
    ],
    "network": [
        ("python_requests", r"\brequests\.(get|post|put|patch|delete|request)\b"),
        ("python_httpx", r"\bhttpx\.(get|post|put|patch|delete|request)\b"),
        ("python_urllib", r"\b(urlopen|urllib\.request)\b"),
        ("python_aiohttp", r"\baiohttp\b"),
        ("js_fetch", r"\bfetch\s*\("),
        ("js_axios", r"\baxios\.(get|post|put|patch|delete|request)\b"),
        ("shell_http", r"(^|\s)(curl|wget)\s+"),
        ("go_http", r"\bhttp\.(Get|Post|Do)\s*\("),
    ],
    "credentials_access": [
        ("dotenv", r"\b(dotenv|load_dotenv)\b"),
        ("env_secret", r"\b(getenv|os\.environ|getenv\(|process\.env)\b.{0,40}\b(token|secret|password|api[_-]?key|access[_-]?key)\b"),
        ("credential_words", r"\b(token|secret|password|api[_-]?key|private[_-]?key|aws_secret_access_key|bw_session)\b"),
        ("shell_export_secret", r"\bexport\b.{0,40}\b(token|secret|password|api[_-]?key|bw_session)\b"),
    ],
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyze sampled skill artifacts for WP4.")
    parser.add_argument(
        "--run-dir",
        default="skills_data/sampled_skills_1000",
        help="Directory containing popular/ and random/ cohorts.",
    )
    parser.add_argument(
        "--output-dir",
        default="",
        help="Output directory. Defaults to <run-dir>/analysis_v3.",
    )
    parser.add_argument(
        "--cohorts",
        nargs="+",
        default=["popular", "random"],
        help="Cohorts to analyze.",
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
        help="Number of worker threads to use for per-skill scanning.",
    )
    return parser.parse_args()


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fieldnames = list(rows[0].keys())
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def safe_read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="ignore")


def should_skip_path(path: Path) -> bool:
    return any(part in IGNORE_DIR_NAMES for part in path.parts)


def find_skill_md(content_dir: Path) -> Path | None:
    candidates = [
        path
        for path in content_dir.rglob("*")
        if path.is_file() and path.name.lower() == "skill.md" and not should_skip_path(path.relative_to(content_dir))
    ]
    if not candidates:
        return None
    candidates.sort(key=lambda path: (len(path.relative_to(content_dir).parts), str(path).lower()))
    return candidates[0]


def rel_to_content(path: Path, content_dir: Path) -> str:
    return str(path.relative_to(content_dir)).replace("\\", "/")


def summarize_counter(counter: Counter[str]) -> str:
    return ";".join(f"{key}:{value}" for key, value in sorted(counter.items()))


def load_metadata(skill_dir: Path) -> dict[str, Any]:
    metadata_path = skill_dir / "metadata.json"
    if not metadata_path.exists():
        return {}
    return json.loads(safe_read_text(metadata_path))


def classify_script_ops(text: str) -> tuple[dict[str, bool], dict[str, list[str]]]:
    flags: dict[str, bool] = {}
    evidence: dict[str, list[str]] = {}
    for op_name, entries in SCRIPT_OP_PATTERNS.items():
        matched_labels = [label for label, pattern in entries if re.search(pattern, text, flags=re.IGNORECASE | re.MULTILINE)]
        flags[op_name] = bool(matched_labels)
        evidence[op_name] = matched_labels
    return flags, evidence


def build_script_rows(skill_dir: Path, cohort: str, skill_id: str, skill_name: str) -> list[dict[str, Any]]:
    content_dir = skill_dir / "content"
    rows: list[dict[str, Any]] = []
    if not content_dir.exists():
        return rows

    for path in sorted(content_dir.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in SCRIPT_EXTENSIONS:
            continue
        rel_path = path.relative_to(content_dir)
        if should_skip_path(rel_path):
            continue
        text = safe_read_text(path)
        flags, evidence = classify_script_ops(text)
        matched_ops = [name for name, enabled in flags.items() if enabled]
        evidence_parts = []
        for op_name, labels in evidence.items():
            if labels:
                evidence_parts.append(f"{op_name}=" + ",".join(labels))
        rows.append(
            {
                "cohort": cohort,
                "skill_id": skill_id,
                "skill_name": skill_name,
                "script_relpath": rel_to_content(path, content_dir),
                "script_ext": path.suffix.lower(),
                "script_bytes": path.stat().st_size,
                "op_read": int(flags["read"]),
                "op_write": int(flags["write"]),
                "op_delete": int(flags["delete"]),
                "op_exec": int(flags["exec"]),
                "op_network": int(flags["network"]),
                "op_credentials_access": int(flags["credentials_access"]),
                "matched_ops": ";".join(matched_ops),
                "evidence_patterns": " | ".join(evidence_parts),
            }
        )
    return rows


def collect_example_stats(skill_dir: Path, cohort: str, skill_id: str, skill_name: str) -> dict[str, Any]:
    content_dir = skill_dir / "content"
    example_dir_paths: list[str] = []
    example_file_count = 0
    example_total_bytes = 0
    example_ext_counter: Counter[str] = Counter()

    if content_dir.exists():
        for path in sorted(content_dir.rglob("*")):
            rel_path = path.relative_to(content_dir)
            if should_skip_path(rel_path):
                continue
            lowered_parts = {part.lower() for part in rel_path.parts}
            if path.is_dir() and any(part in EXAMPLE_DIR_HINTS for part in lowered_parts):
                example_dir_paths.append(rel_to_content(path, content_dir))
            if path.is_file() and any(part in EXAMPLE_DIR_HINTS for part in lowered_parts):
                example_file_count += 1
                example_total_bytes += path.stat().st_size
                example_ext_counter[path.suffix.lower() or "<no_ext>"] += 1

    skill_md_path = find_skill_md(content_dir) if content_dir.exists() else None
    skill_md_text = safe_read_text(skill_md_path) if skill_md_path else ""
    embedded_example_mentions = len(re.findall(r"\b(example|examples|for example|e\.g\.)\b", skill_md_text, flags=re.IGNORECASE))
    embedded_code_fence_count = skill_md_text.count("```") // 2 if skill_md_text else 0

    return {
        "cohort": cohort,
        "skill_id": skill_id,
        "skill_name": skill_name,
        "has_skill_md": int(bool(skill_md_path)),
        "embedded_example_mentions": embedded_example_mentions,
        "embedded_code_fence_count": embedded_code_fence_count,
        "example_dir_count": len(example_dir_paths),
        "example_dir_paths": ";".join(example_dir_paths),
        "example_file_count": example_file_count,
        "example_total_bytes": example_total_bytes,
        "example_file_exts": summarize_counter(example_ext_counter),
    }


def is_config_like_json(path: Path) -> bool:
    lowered_name = path.name.lower()
    if lowered_name in CONFIG_LIKE_FILENAMES:
        return True
    return any(part in {"config", "configs", ".github", ".vscode"} for part in (part.lower() for part in path.parts))


def classify_data_asset(path: Path) -> str | None:
    suffix = path.suffix.lower()
    lowered_parts = {part.lower() for part in path.parts}

    if suffix in DATABASE_EXTENSIONS:
        return "database"
    if suffix in TABULAR_EXTENSIONS:
        return "tabular"
    if suffix in JSON_LIKE_EXTENSIONS:
        if is_config_like_json(path):
            return None
        return "json_like"
    if suffix in BINARY_DATA_EXTENSIONS:
        return "binary_data"
    if any(part in DATA_DIR_HINTS for part in lowered_parts):
        if suffix in TEXT_DATA_EXTENSIONS | {".yaml", ".yml", ".xml"}:
            return "support_data"
    return None


def collect_data_asset_stats(skill_dir: Path, cohort: str, skill_id: str, skill_name: str) -> dict[str, Any]:
    content_dir = skill_dir / "content"
    category_counter: Counter[str] = Counter()
    ext_counter: Counter[str] = Counter()
    data_paths: list[str] = []
    total_bytes = 0
    excluded_config_like_count = 0
    largest_file_path = ""
    largest_file_bytes = 0

    if content_dir.exists():
        for path in sorted(content_dir.rglob("*")):
            if not path.is_file():
                continue
            rel_path = path.relative_to(content_dir)
            if should_skip_path(rel_path):
                continue
            category = classify_data_asset(rel_path)
            if category is None:
                if path.suffix.lower() in JSON_LIKE_EXTENSIONS and is_config_like_json(rel_path):
                    excluded_config_like_count += 1
                continue
            file_bytes = path.stat().st_size
            rel_path_str = rel_to_content(path, content_dir)
            data_paths.append(rel_path_str)
            category_counter[category] += 1
            ext_counter[path.suffix.lower() or "<no_ext>"] += 1
            total_bytes += file_bytes
            if file_bytes > largest_file_bytes:
                largest_file_bytes = file_bytes
                largest_file_path = rel_path_str

    return {
        "cohort": cohort,
        "skill_id": skill_id,
        "skill_name": skill_name,
        "has_data_assets": int(bool(data_paths)),
        "data_file_count": len(data_paths),
        "data_total_bytes": total_bytes,
        "json_like_count": category_counter["json_like"],
        "tabular_count": category_counter["tabular"],
        "database_count": category_counter["database"],
        "binary_data_count": category_counter["binary_data"],
        "support_data_count": category_counter["support_data"],
        "largest_data_file_relpath": largest_file_path,
        "largest_data_file_bytes": largest_file_bytes,
        "data_file_exts": summarize_counter(ext_counter),
        "data_file_paths_sample": ";".join(data_paths[:10]),
        "excluded_config_like_count": excluded_config_like_count,
    }


def iter_skill_dirs(run_dir: Path, cohort: str, max_skills: int) -> list[Path]:
    cohort_dir = run_dir / cohort
    if not cohort_dir.exists():
        raise FileNotFoundError(f"missing cohort directory: {cohort_dir}")
    skill_dirs = sorted(path for path in cohort_dir.iterdir() if path.is_dir())
    if max_skills > 0:
        return skill_dirs[:max_skills]
    return skill_dirs


def analyze_skill_dir(skill_dir: Path, cohort: str) -> tuple[list[dict[str, Any]], dict[str, Any], dict[str, Any]]:
    metadata = load_metadata(skill_dir)
    skill = metadata.get("skill", {})
    skill_id = str(skill.get("id", skill_dir.name))
    skill_name = str(skill.get("name", ""))
    return (
        build_script_rows(skill_dir, cohort, skill_id, skill_name),
        collect_example_stats(skill_dir, cohort, skill_id, skill_name),
        collect_data_asset_stats(skill_dir, cohort, skill_id, skill_name),
    )


def mean(values: list[float]) -> float:
    if not values:
        return 0.0
    return float(sum(values) / len(values))


def build_artifact_profile(
    script_rows: list[dict[str, Any]],
    example_rows: list[dict[str, Any]],
    data_rows: list[dict[str, Any]],
) -> str:
    cohorts = ["popular", "random"]
    script_skill_flags: dict[tuple[str, str], dict[str, int]] = {}
    for row in script_rows:
        key = (row["cohort"], row["skill_id"])
        flags = script_skill_flags.setdefault(
            key,
            {
                "op_read": 0,
                "op_write": 0,
                "op_delete": 0,
                "op_exec": 0,
                "op_network": 0,
                "op_credentials_access": 0,
            },
        )
        for flag_name in flags:
            flags[flag_name] = max(flags[flag_name], int(row[flag_name]))

    lines = [
        "# Artifact Profile",
        "",
        "## Cohort Summary",
        "",
    ]
    for cohort in cohorts:
        cohort_examples = [row for row in example_rows if row["cohort"] == cohort]
        cohort_data = [row for row in data_rows if row["cohort"] == cohort]
        skill_keys = [key for key in script_skill_flags if key[0] == cohort]
        skill_count = len(cohort_examples)
        lines.append(
            f"- {cohort}: skills={skill_count}, skills_with_scripts={len(skill_keys)}, "
            f"skills_with_example_files={sum(1 for row in cohort_examples if int(row['example_file_count']) > 0)}, "
            f"skills_with_data_assets={sum(1 for row in cohort_data if int(row['has_data_assets']) > 0)}"
        )

    lines.extend(["", "## Script Operation Rates", ""])
    for cohort in cohorts:
        cohort_keys = [key for key in script_skill_flags if key[0] == cohort]
        denom = len(cohort_keys) or 1
        for flag_name in [
            "op_read",
            "op_write",
            "op_delete",
            "op_exec",
            "op_network",
            "op_credentials_access",
        ]:
            count = sum(script_skill_flags[key][flag_name] for key in cohort_keys)
            lines.append(f"- {cohort} {flag_name}: {count}/{len(cohort_keys)} ({count / denom * 100:.1f}%)")

    lines.extend(["", "## Example Coverage", ""])
    for cohort in cohorts:
        cohort_examples = [row for row in example_rows if row["cohort"] == cohort]
        lines.append(
            f"- {cohort}: avg_example_files={mean([int(row['example_file_count']) for row in cohort_examples]):.2f}, "
            f"avg_embedded_mentions={mean([int(row['embedded_example_mentions']) for row in cohort_examples]):.2f}, "
            f"avg_embedded_code_fences={mean([int(row['embedded_code_fence_count']) for row in cohort_examples]):.2f}"
        )

    lines.extend(["", "## Data Assets", ""])
    for cohort in cohorts:
        cohort_data = [row for row in data_rows if row["cohort"] == cohort]
        lines.append(
            f"- {cohort}: avg_data_files={mean([int(row['data_file_count']) for row in cohort_data]):.2f}, "
            f"avg_data_bytes={mean([int(row['data_total_bytes']) for row in cohort_data]):.1f}, "
            f"database_skills={sum(1 for row in cohort_data if int(row['database_count']) > 0)}"
        )

    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    run_dir = Path(args.run_dir)
    output_dir = Path(args.output_dir) if args.output_dir else run_dir / "analysis_v3"
    output_dir.mkdir(parents=True, exist_ok=True)

    script_rows: list[dict[str, Any]] = []
    example_rows: list[dict[str, Any]] = []
    data_rows: list[dict[str, Any]] = []

    tasks: list[tuple[Path, str]] = []
    for cohort in args.cohorts:
        for skill_dir in iter_skill_dirs(run_dir, cohort, args.max_skills_per_cohort):
            tasks.append((skill_dir, cohort))

    if args.workers <= 1:
        for skill_dir, cohort in tasks:
            script_part, example_part, data_part = analyze_skill_dir(skill_dir, cohort)
            script_rows.extend(script_part)
            example_rows.append(example_part)
            data_rows.append(data_part)
    else:
        with ThreadPoolExecutor(max_workers=args.workers) as executor:
            futures = [executor.submit(analyze_skill_dir, skill_dir, cohort) for skill_dir, cohort in tasks]
            for future in futures:
                script_part, example_part, data_part = future.result()
                script_rows.extend(script_part)
                example_rows.append(example_part)
                data_rows.append(data_part)

    script_rows.sort(key=lambda row: (row["cohort"], row["skill_id"], row["script_relpath"]))
    example_rows.sort(key=lambda row: (row["cohort"], row["skill_id"]))
    data_rows.sort(key=lambda row: (row["cohort"], row["skill_id"]))

    write_csv(output_dir / "script_ops.csv", script_rows)
    write_csv(output_dir / "example_stats.csv", example_rows)
    write_csv(output_dir / "data_asset_stats.csv", data_rows)
    (output_dir / "artifact_profile.md").write_text(
        build_artifact_profile(script_rows, example_rows, data_rows),
        encoding="utf-8",
    )

    print(f"[INFO] output_dir={output_dir}")
    print(f"[INFO] script_rows={len(script_rows)}")
    print(f"[INFO] example_rows={len(example_rows)}")
    print(f"[INFO] data_rows={len(data_rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
