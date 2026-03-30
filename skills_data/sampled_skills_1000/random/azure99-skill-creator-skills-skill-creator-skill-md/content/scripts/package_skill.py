#!/usr/bin/env python3
"""Package a skill folder into a .skill archive."""

import argparse
import sys
import zipfile
from pathlib import Path

from quick_validate import validate_skill

EXCLUDE_NAMES = {
    "__pycache__",
    ".DS_Store",
    ".git",
}


def _should_skip(path):
    if path.name in EXCLUDE_NAMES:
        return True
    if path.suffix in {".pyc", ".pyo"}:
        return True
    return False


def _walk_files(root):
    for path in root.rglob("*"):
        if _should_skip(path):
            continue
        if path.is_file():
            yield path


def _validate_skill_folder(skill_path):
    result, frontmatter = validate_skill(skill_path)

    if frontmatter and "name" in frontmatter:
        declared_name = frontmatter["name"].strip()
        if declared_name and skill_path.name != declared_name:
            result.errors.append(
                f"folder name '{skill_path.name}' does not match frontmatter name '{declared_name}'"
            )

    return result


def package_skill(skill_path, output_dir=None):
    skill_path = Path(skill_path).resolve()

    if not skill_path.exists():
        raise FileNotFoundError(f"Skill folder not found: {skill_path}")
    if not skill_path.is_dir():
        raise NotADirectoryError(f"Not a directory: {skill_path}")

    result = _validate_skill_folder(skill_path)
    for warning in result.warnings:
        print(f"[WARN] {warning}")

    if not result.ok():
        for error in result.errors:
            print(f"[ERROR] {error}")
        raise ValueError("Validation failed")

    output_path = Path(output_dir).resolve() if output_dir else Path.cwd()
    output_path.mkdir(parents=True, exist_ok=True)

    skill_filename = output_path / f"{skill_path.name}.skill"

    with zipfile.ZipFile(skill_filename, "w", zipfile.ZIP_DEFLATED) as zipf:
        for file_path in _walk_files(skill_path):
            arcname = file_path.relative_to(skill_path.parent)
            zipf.write(file_path, arcname)

    return skill_filename


def main():
    parser = argparse.ArgumentParser(description="Package a skill into a .skill file")
    parser.add_argument("skill_path", help="Path to the skill folder")
    parser.add_argument(
        "output_dir",
        nargs="?",
        default=None,
        help="Optional output directory for the .skill file",
    )

    args = parser.parse_args()

    try:
        skill_file = package_skill(args.skill_path, args.output_dir)
        print(f"[OK] Packaged skill to {skill_file}")
    except Exception as exc:
        print(f"[ERROR] {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
