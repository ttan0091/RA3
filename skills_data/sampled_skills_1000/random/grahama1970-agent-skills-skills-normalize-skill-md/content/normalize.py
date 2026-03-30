#!/usr/bin/env python3
"""
Text normalization tool for handling PDF encoding issues.

Comprehensive Unicode normalization based on patterns from text_toolz.
Handles:
- Windows-1252 characters (common in old PDFs)
- Unicode whitespace variants
- Hyphen/dash variants
- Quote variants
- Ligatures
- Directional formatting
- Control characters
- Line-break hyphenation
"""

import re
import sys
import unicodedata
from pathlib import Path
from typing import Optional


def normalize_text(text: str) -> str:
    """Normalize text to handle encoding issues and invisible characters.

    PDFs often have 15+ different encodings for hyphens, various Unicode
    whitespace, ligatures, and other characters. This normalizes them for
    consistent pattern matching.
    """
    if not text:
        return ""

    # Step 1: Convert Windows-1252 characters FIRST (before control char removal)
    windows_1252_map = {
        "\x91": "'",   # Left single quote
        "\x92": "'",   # Right single quote
        "\x93": '"',   # Left double quote
        "\x94": '"',   # Right double quote
        "\x95": "-",   # Bullet
        "\x96": "-",   # En dash
        "\x97": "-",   # Em dash
        "\x85": "...", # Horizontal ellipsis
        "\x99": "(TM)", # Trademark
        "\xa9": "(C)", # Copyright
        "\xae": "(R)", # Registered
    }
    for old, new in windows_1252_map.items():
        text = text.replace(old, new)

    # Step 2: NFKC Unicode Normalization (foundational)
    text = unicodedata.normalize("NFKC", text)

    # Step 3: Remove directional formatting characters
    directional_pattern = "[\u200e\u200f\u202a\u202b\u202c\u202d\u202e\u2066\u2067\u2068\u2069]"
    text = re.sub(directional_pattern, "", text)

    # Step 4: Remove control characters (C0/C1) but preserve newlines/tabs
    control_pattern = "[\u0000-\u0008\u000b\u000c\u000e-\u001f\u007f-\u009f]"
    text = re.sub(control_pattern, "", text)

    # Step 5: Whitespace variants -> ASCII space
    whitespace_map = {
        "\u00a0": " ",  # Non-breaking space
        "\u2002": " ",  # En space
        "\u2003": " ",  # Em space
        "\u2009": " ",  # Thin space
        "\u200a": " ",  # Hair space
        "\u202f": " ",  # Narrow no-break space
        "\u205f": " ",  # Medium mathematical space
        "\u3000": " ",  # Ideographic space
        "\u200b": "",   # Zero-width space
        "\u200c": "",   # Zero-width non-joiner
        "\u200d": "",   # Zero-width joiner
        "\ufeff": "",   # BOM
        "\u2060": "",   # Word joiner
    }
    for old, new in whitespace_map.items():
        text = text.replace(old, new)

    # Step 6: Hyphen/Dash variants -> ASCII hyphen
    hyphen_chars = "\u2010\u2011\u2012\u2013\u2014\u2015\u2212\u058a\u05be\u1400\u1806\u2e17\u2e1a\u30a0\ufe58\ufe63\uff0d"
    for hc in hyphen_chars:
        text = text.replace(hc, "-")
    text = text.replace("\u00ad", "")  # Soft hyphen (remove)

    # Step 7: Quote variants -> ASCII quotes
    single_quotes = "\u2018\u2019\u201a\u201b\u2032\u2035"
    double_quotes = "\u201c\u201d\u201e\u201f\u2033\u2036\u00ab\u00bb"
    for qc in single_quotes:
        text = text.replace(qc, "'")
    for qc in double_quotes:
        text = text.replace(qc, '"')

    # Step 8: Period/Dot variants
    text = text.replace("\u2024", ".")  # One dot leader
    text = text.replace("\u2027", ".")  # Hyphenation point
    text = text.replace("\u30fb", ".")  # Katakana middle dot
    text = text.replace("\u2026", "...")  # Horizontal ellipsis

    # Step 9: Bullet points -> hyphen
    bullet_chars = "\u2022\u25cf\u25e6\u25cb\u25aa\u25ab\u25a0\u25a1\u2023\u2043"
    for bc in bullet_chars:
        text = text.replace(bc, "-")

    # Step 10: Ligatures (expand)
    ligatures = {
        "\ufb00": "ff",
        "\ufb01": "fi",
        "\ufb02": "fl",
        "\ufb03": "ffi",
        "\ufb04": "ffl",
        "\ufb05": "st",
        "\ufb06": "st",
    }
    for old, new in ligatures.items():
        text = text.replace(old, new)

    # Step 11: Fix hyphenated words at line breaks
    text = re.sub(r"(\w+)-\n(\w+)", r"\1\2", text)

    # Step 12: Collapse multiple whitespace to single space
    text = " ".join(text.split())
    return text.strip()


def normalize_file(input_path: Path, output_path: Optional[Path] = None) -> str:
    """Normalize text from a file."""
    text = input_path.read_text(encoding="utf-8", errors="replace")
    normalized = normalize_text(text)

    if output_path:
        output_path.write_text(normalized, encoding="utf-8")
        return f"Normalized text written to {output_path}"

    return normalized


app = typer.Typer(help="Normalize text to handle PDF/Unicode encoding issues")


@app.command()
def main(
    input: str = typer.Argument(None, help="Input file path or text (reads from stdin if not provided)"),
    output: Path = typer.Option(None, "-o", "--output", help="Output file path (prints to stdout if not provided)"),
    text: bool = typer.Option(False, "-t", "--text", help="Treat input as text instead of file path"),
    stats: bool = typer.Option(False, "--stats", help="Show normalization statistics"),
) -> None:
    """Normalize text to handle PDF/Unicode encoding issues."""
    # Get input text
    if input:
        if text:
            raw_text = input
        else:
            raw_text = Path(input).read_text(encoding="utf-8", errors="replace")
    elif not sys.stdin.isatty():
        # Handle stdin with encoding errors gracefully (common with PDF text)
        raw_text = sys.stdin.buffer.read().decode("utf-8", errors="replace")
    else:
        raise typer.Exit(1)

    # Normalize
    original_len = len(raw_text)
    normalized = normalize_text(raw_text)

    # Output
    if output:
        output.write_text(normalized, encoding="utf-8")
        print(f"Normalized text written to {output}", file=sys.stderr)
    else:
        print(normalized)

    # Stats
    if stats:
        print(f"\n--- Statistics ---", file=sys.stderr)
        print(f"Original length: {original_len} chars", file=sys.stderr)
        print(f"Normalized length: {len(normalized)} chars", file=sys.stderr)
        print(f"Reduction: {original_len - len(normalized)} chars", file=sys.stderr)


if __name__ == "__main__":
    app()
