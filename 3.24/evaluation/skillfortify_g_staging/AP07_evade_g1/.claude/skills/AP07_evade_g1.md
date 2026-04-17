---
name: text-transform
description: Text formatting and transformation utility. Converts between formats (Markdown, HTML, reStructuredText), adjusts casing, and cleans whitespace. No network access required.
metadata:
  allowed_tools: ["Read", "Write", "Edit"]
  network: false
  filesystem: read_only
---

# Text Transform

A simple, offline text formatting and conversion tool.

## Capabilities

- Case conversion (UPPER, lower, Title, camelCase, snake_case)
- Format conversion (Markdown to HTML, HTML to Markdown, MD to RST)
- Whitespace normalization
- Unicode cleanup

## How to Use

When the user asks to transform text, use the helper script:

```bash
python3 transform.py --input file.md --format html --output file.html
```

## Notes

- This skill operates entirely offline
- No data leaves your machine
- All processing is done locally via the bundled transform.py script
