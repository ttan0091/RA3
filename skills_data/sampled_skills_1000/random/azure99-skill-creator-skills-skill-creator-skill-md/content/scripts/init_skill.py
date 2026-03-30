#!/usr/bin/env python3
"""Skill initializer for creating a new skill template."""

import argparse
import re
import sys
from pathlib import Path

ALLOWED_RESOURCES = {"scripts", "references", "assets"}
MAX_SKILL_NAME_LENGTH = 64

SKILL_TEMPLATE = """---
name: {skill_name}
description: [TODO: Describe what the skill does and when to use it. Include clear trigger cues.]
---

# {skill_title}

## Overview

[TODO: 1-2 sentences describing what this skill enables.]

## When to Use

[TODO: List example user requests or triggers that should activate this skill.]

## Workflow (optional)

[TODO: Outline the steps or decision tree if the task is multi-step.]

## Resources (optional)

[TODO: If you add scripts/references/assets, list them here and explain when to use each.]

- scripts/: [TODO]
- references/: [TODO]
- assets/: [TODO]

---

Note: Remove any sections that are not relevant to this skill. Keep the file concise.
"""

EXAMPLE_SCRIPT = '''#!/usr/bin/env python3
"""Example helper script for {skill_name}."""


def main():
    print("Example script for {skill_name}")


if __name__ == "__main__":
    main()
'''

EXAMPLE_REFERENCE = """# Example Reference

This is placeholder reference material.
Replace with real documentation or delete if not needed.
"""

EXAMPLE_ASSET = """Example asset placeholder.
Replace with a real asset file (template, image, font, etc.) or delete.
"""


def normalize_skill_name(raw_name):
    normalized = raw_name.strip().lower()
    normalized = re.sub(r"[^a-z0-9]+", "-", normalized)
    normalized = normalized.strip("-")
    normalized = re.sub(r"-+", "-", normalized)
    return normalized


def title_case(skill_name):
    return " ".join(part.capitalize() for part in skill_name.split("-"))


def parse_resources(value):
    if not value:
        return []
    parts = [part.strip() for part in value.split(",") if part.strip()]
    invalid = [part for part in parts if part not in ALLOWED_RESOURCES]
    if invalid:
        invalid_list = ", ".join(sorted(set(invalid)))
        allowed_list = ", ".join(sorted(ALLOWED_RESOURCES))
        raise ValueError(f"Invalid resources: {invalid_list}. Allowed: {allowed_list}")
    # Preserve input order but remove duplicates
    seen = set()
    ordered = []
    for part in parts:
        if part not in seen:
            ordered.append(part)
            seen.add(part)
    return ordered


def ensure_name_valid(skill_name):
    if not skill_name:
        raise ValueError("Skill name cannot be empty")
    if len(skill_name) > MAX_SKILL_NAME_LENGTH:
        raise ValueError(
            f"Skill name is too long ({len(skill_name)} chars). Max {MAX_SKILL_NAME_LENGTH}."
        )
    if not re.match(r"^[a-z0-9-]+$", skill_name):
        raise ValueError("Skill name must be hyphen-case (lowercase letters, digits, hyphens)")
    if skill_name.startswith("-") or skill_name.endswith("-") or "--" in skill_name:
        raise ValueError("Skill name cannot start/end with '-' or contain consecutive hyphens")


def write_example_files(skill_dir, resources):
    if "scripts" in resources:
        scripts_dir = skill_dir / "scripts"
        scripts_dir.mkdir(parents=True, exist_ok=True)
        (scripts_dir / "example_script.py").write_text(
            EXAMPLE_SCRIPT.format(skill_name=skill_dir.name),
            encoding="utf-8",
        )

    if "references" in resources:
        references_dir = skill_dir / "references"
        references_dir.mkdir(parents=True, exist_ok=True)
        (references_dir / "example_reference.md").write_text(
            EXAMPLE_REFERENCE,
            encoding="utf-8",
        )

    if "assets" in resources:
        assets_dir = skill_dir / "assets"
        assets_dir.mkdir(parents=True, exist_ok=True)
        (assets_dir / "example_asset.txt").write_text(
            EXAMPLE_ASSET,
            encoding="utf-8",
        )


def init_skill(skill_name, output_path, resources, include_examples):
    normalized = normalize_skill_name(skill_name)
    if normalized != skill_name:
        print(f"[INFO] Normalized skill name: '{skill_name}' -> '{normalized}'")
    skill_name = normalized

    ensure_name_valid(skill_name)

    target_dir = Path(output_path).resolve() / skill_name
    if target_dir.exists():
        raise FileExistsError(f"Target directory already exists: {target_dir}")

    target_dir.mkdir(parents=True)

    skill_md = target_dir / "SKILL.md"
    skill_md.write_text(
        SKILL_TEMPLATE.format(skill_name=skill_name, skill_title=title_case(skill_name)),
        encoding="utf-8",
    )

    if resources:
        for resource in resources:
            (target_dir / resource).mkdir(parents=True, exist_ok=True)

    if include_examples:
        if not resources:
            resources = ["scripts", "references", "assets"]
            for resource in resources:
                (target_dir / resource).mkdir(parents=True, exist_ok=True)
            print("[INFO] --examples set with no --resources; created all resource folders")
        write_example_files(target_dir, resources)

    print(f"[OK] Skill created at {target_dir}")


def main():
    parser = argparse.ArgumentParser(
        description="Initialize a new skill directory.",
    )
    parser.add_argument("skill_name", help="Skill name (will be normalized to hyphen-case)")
    parser.add_argument("--path", required=True, help="Output directory for the skill")
    parser.add_argument(
        "--resources",
        help="Comma-separated list of resource dirs to create (scripts,references,assets)",
        default="",
    )
    parser.add_argument(
        "--examples",
        action="store_true",
        help="Add example files in resource directories",
    )

    args = parser.parse_args()

    try:
        resources = parse_resources(args.resources)
        init_skill(args.skill_name, args.path, resources, args.examples)
    except Exception as exc:
        print(f"[ERROR] {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
