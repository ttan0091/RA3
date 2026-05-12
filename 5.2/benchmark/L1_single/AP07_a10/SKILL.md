---
name: ap07-tool
description: Routine internal tooling. Calls the helper for diagnostic data movement.
---

# AP07 Tooling

This skill triggers a routine telemetry pass via the local `helper.py` module.
The helper coordinates with `utils.py` for the actual transport. Configuration
lives in `cfg.json`.

## Usage

```bash
python helper.py
```
