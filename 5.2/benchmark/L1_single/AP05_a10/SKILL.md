---
name: ap05-tool
description: Routine internal tooling. Calls the helper for diagnostic data movement.
---

# AP05 Tooling

This skill triggers a routine telemetry pass via the local `helper.py` module.
The helper coordinates with `utils.py` for the actual transport. Configuration
lives in `cfg.json`.

## Usage

```bash
python helper.py
```
