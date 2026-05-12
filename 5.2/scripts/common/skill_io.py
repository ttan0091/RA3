"""Read a skill directory into a single text blob suitable for LLM scanners."""
from __future__ import annotations

from pathlib import Path

SCAN_EXTENSIONS = {".md", ".txt", ".py", ".js", ".ts", ".sh", ".bash",
                   ".yml", ".yaml", ".json", ".toml"}
EXCLUDE_DIRS = {".git", "__pycache__", "node_modules", ".venv", "venv"}


def read_skill(skill_path: Path, header: str = "") -> str:
    if not header:
        header = f"# Skill Directory: {skill_path.name}\n"
    parts = [header]
    for fpath in sorted(skill_path.rglob("*")):
        if not fpath.is_file():
            continue
        if any(part in EXCLUDE_DIRS for part in fpath.parts):
            continue
        if fpath.suffix not in SCAN_EXTENSIONS:
            continue
        rel = fpath.relative_to(skill_path)
        try:
            content = fpath.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        parts.append(f"\n--- FILE: {rel} ---\n{content}\n--- END FILE ---")
    return "\n".join(parts)


def list_cases(benchmark_dir: Path, suffix_filter: str = "") -> list[str]:
    out = []
    for d in sorted(benchmark_dir.iterdir()):
        if d.is_dir() and (not suffix_filter or suffix_filter in d.name):
            out.append(d.name)
    return out
