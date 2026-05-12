---
name: text-transform
description: Text formatting and transformation utility. Converts between formats (Markdown, HTML, reStructuredText), adjusts casing, and cleans whitespace. No network access required.
metadata:
  allowed_tools: ["Read", "Write", "Edit"]
  network: false
  filesystem: read_only
---

# Internal Text Normalization Helper

A straightforward, offline text normalization and conversion helper for internal documentation consistency.

## Purpose

- Normalize casing for uniform display (UPPER, lower, Title, camelCase, snake_case)
- Convert between documentation formats to maintain a single standard (Markdown to HTML, HTML to Markdown, MD to RST)
- Audit and clean whitespace in files
- Sanitize Unicode characters to avoid rendering issues

## How to Use

When a user requests text normalization, invoke the bundled helper script:

```bash
python3 transform.py --input file.md --format html --output file.html
```

## Notes

- This tool runs entirely offline with no external network calls
- All processing is local and uses the provided transform.py script
- Operates as a diagnostic helper for documentation consistency checks