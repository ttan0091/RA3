#!/usr/bin/env python3
"""Generate a ready-to-paste Codex prompt for the code-documenter skill."""

from __future__ import annotations

import argparse
from pathlib import Path

DEFAULT_TARGETS = "src/ docs/ README.md config/"
DEFAULT_OUTPUT = "Update or create documentation files under docs/ and README.md"
DEFAULT_CONSTRAINTS = (
    "Preserve existing tone and structure; add examples where helpful; "
    "do not modify code unless explicitly asked."
)


def build_prompt(task: str, targets: str, output: str, constraints: str) -> str:
    lines = [
        "Use code-documenter only.",
        f"Task: {task}",
        f"Targets: {targets}",
        f"Output: {output}",
    ]
    if constraints:
        lines.append(f"Constraints: {constraints}")
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create a Codex prompt that forces the code-documenter skill.",
    )
    parser.add_argument(
        "task",
        help="What documentation you want generated (quote the task).",
    )
    parser.add_argument(
        "--targets",
        default=DEFAULT_TARGETS,
        help=f"Files/folders to document (default: {DEFAULT_TARGETS!r}).",
    )
    parser.add_argument(
        "--output",
        default=DEFAULT_OUTPUT,
        help="Desired output files or locations.",
    )
    parser.add_argument(
        "--constraints",
        default=DEFAULT_CONSTRAINTS,
        help="Style/format constraints.",
    )
    parser.add_argument(
        "--out",
        default="REQUEST.md",
        help="Output file name (default: REQUEST.md).",
    )

    args = parser.parse_args()

    prompt = build_prompt(args.task, args.targets, args.output, args.constraints)

    out_path = Path(__file__).resolve().parent / args.out
    out_path.write_text(prompt, encoding="utf-8")

    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
