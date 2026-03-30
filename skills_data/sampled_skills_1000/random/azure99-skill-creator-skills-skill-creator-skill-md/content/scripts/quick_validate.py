#!/usr/bin/env python3
"""Quick validation for skill folders."""

import re
import sys
from pathlib import Path

try:
    import yaml
except Exception as exc:  # pragma: no cover - runtime dependency
    print(f"[ERROR] Missing dependency: {exc}")
    print("Install PyYAML to run validation.")
    sys.exit(2)

MAX_SKILL_NAME_LENGTH = 64
FORBIDDEN_ROOT_FILES = {
    "README.md",
    "INSTALLATION_GUIDE.md",
    "QUICK_REFERENCE.md",
    "CHANGELOG.md",
}


class ValidationResult:
    def __init__(self):
        self.errors = []
        self.warnings = []

    def ok(self):
        return not self.errors


def _extract_frontmatter(content):
    match = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n", content, re.DOTALL)
    if not match:
        return None
    return match.group(1)


def _validate_name(name, result):
    if not isinstance(name, str):
        result.errors.append(f"name must be a string, got {type(name).__name__}")
        return
    name = name.strip()
    if not name:
        result.errors.append("name must not be empty")
        return
    if len(name) > MAX_SKILL_NAME_LENGTH:
        result.errors.append(
            f"name too long ({len(name)} chars), max {MAX_SKILL_NAME_LENGTH}"
        )
    if not re.match(r"^[a-z0-9-]+$", name):
        result.errors.append("name must be hyphen-case (lowercase letters, digits, hyphens)")
    if name.startswith("-") or name.endswith("-") or "--" in name:
        result.errors.append("name cannot start/end with '-' or contain consecutive hyphens")


def _validate_description(description, result):
    if not isinstance(description, str):
        result.errors.append(
            f"description must be a string, got {type(description).__name__}"
        )
        return
    description = description.strip()
    if not description:
        result.errors.append("description must not be empty")
        return

    # Heuristic warnings for quality.
    lowered = description.lower()
    if len(description) < 40:
        result.warnings.append("description is short; include triggers and scope")
    if "use when" not in lowered and "use for" not in lowered:
        result.warnings.append("description may be missing explicit trigger guidance")


def validate_skill(skill_path):
    result = ValidationResult()
    skill_path = Path(skill_path)

    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        result.errors.append("SKILL.md not found")
        return result, None

    content = skill_md.read_text(encoding="utf-8")
    if not content.startswith("---"):
        result.errors.append("missing YAML frontmatter at top of SKILL.md")
        return result, None

    frontmatter_text = _extract_frontmatter(content)
    if frontmatter_text is None:
        result.errors.append("invalid YAML frontmatter block")
        return result, None

    try:
        frontmatter = yaml.safe_load(frontmatter_text)
    except yaml.YAMLError as exc:
        result.errors.append(f"invalid YAML in frontmatter: {exc}")
        return result, None

    if not isinstance(frontmatter, dict):
        result.errors.append("frontmatter must be a YAML mapping")
        return result, None

    allowed_keys = {"name", "description"}
    unexpected = set(frontmatter.keys()) - allowed_keys
    if unexpected:
        unexpected_list = ", ".join(sorted(unexpected))
        result.errors.append(
            f"unexpected frontmatter keys: {unexpected_list} (only name, description allowed)"
        )

    if "name" not in frontmatter:
        result.errors.append("missing frontmatter field: name")
    else:
        _validate_name(frontmatter.get("name"), result)

    if "description" not in frontmatter:
        result.errors.append("missing frontmatter field: description")
    else:
        _validate_description(frontmatter.get("description"), result)

    # Directory-level checks
    forbidden = FORBIDDEN_ROOT_FILES.intersection({p.name for p in skill_path.iterdir()})
    if forbidden:
        forbidden_list = ", ".join(sorted(forbidden))
        result.errors.append(f"forbidden root files present: {forbidden_list}")

    return result, frontmatter


def _print_results(result):
    for warning in result.warnings:
        print(f"[WARN] {warning}")
    for error in result.errors:
        print(f"[ERROR] {error}")


def main():
    if len(sys.argv) != 2:
        print("Usage: scripts/quick_validate.py <skill_directory>")
        sys.exit(1)

    result, _ = validate_skill(sys.argv[1])
    _print_results(result)

    if result.ok():
        print("[OK] Skill is valid")
        sys.exit(0)

    sys.exit(1)


if __name__ == "__main__":
    main()
