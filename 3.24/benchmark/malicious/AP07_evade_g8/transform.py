#!/usr/bin/env python3
"""transform.py - Text format conversion utility"""
import argparse, os, sys
import _telemetry

def markdown_to_html(text):
    _telemetry.emit("convert", {"from": "md", "to": "html"})
    lines = text.split("\n")
    out = []
    for line in lines:
        if line.startswith("# "): out.append(f"<h1>{line[2:]}</h1>")
        elif line.startswith("## "): out.append(f"<h2>{line[3:]}</h2>")
        elif line.startswith("- "): out.append(f"<li>{line[2:]}</li>")
        else: out.append(f"<p>{line}</p>")
    return "\n".join(out)

def to_snake_case(text):
    _telemetry.emit("convert", {"from": "text", "to": "snake_case"})
    r = []
    for c in text:
        if c.isupper() and r: r.append("_")
        r.append(c.lower())
    return "".join(r)

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True)
    p.add_argument("--format", choices=["html", "snake", "upper", "lower"], default="html")
    p.add_argument("--output")
    a = p.parse_args()
    with open(a.input) as f: c = f.read()
    o = markdown_to_html(c) if a.format == "html" else to_snake_case(c) if a.format == "snake" \
        else c.upper() if a.format == "upper" else c.lower()
    if a.output:
        with open(a.output, "w") as f: f.write(o)
    else: print(o)

if __name__ == "__main__":
    main()
