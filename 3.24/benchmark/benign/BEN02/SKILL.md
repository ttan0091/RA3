---
name: env-loader
description: Load and validate environment variables from .env files. Supports multiple environments, variable interpolation, and schema validation.
---

# Environment Loader

Manage environment variables across development, staging, and production.

## Features

- Load `.env`, `.env.local`, `.env.production` files
- Validate required variables against a schema
- Variable interpolation (`${VAR}` syntax)
- Type coercion (boolean, integer, URL)

## Loader Script

```python
#!/usr/bin/env python3
"""env_loader.py - Environment variable loader with validation"""
import os
import re
import sys

def load_env_file(path):
    """Parse a .env file and return key-value pairs"""
    env = {}
    if not os.path.exists(path):
        return env
    with open(path) as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            match = re.match(r'^([A-Za-z_][A-Za-z0-9_]*)=(.*)', line)
            if match:
                key = match.group(1)
                value = match.group(2).strip().strip("\"'")
                # Interpolate ${VAR} references
                value = re.sub(r'\$\{(\w+)\}',
                             lambda m: env.get(m.group(1), os.environ.get(m.group(1), '')),
                             value)
                env[key] = value
    return env

def validate_schema(env, schema):
    """Validate env vars against a schema"""
    errors = []
    for var in schema.get("required", []):
        if var not in env:
            errors.append(f"Missing required variable: {var}")
    for var, var_type in schema.get("types", {}).items():
        if var in env:
            try:
                if var_type == "int":
                    int(env[var])
                elif var_type == "bool":
                    assert env[var].lower() in ("true", "false", "1", "0")
                elif var_type == "url":
                    assert env[var].startswith(("http://", "https://"))
            except (ValueError, AssertionError):
                errors.append(f"{var} should be type {var_type}, got: {env[var]}")
    return errors

def load_all():
    """Load env files in priority order"""
    base = load_env_file(".env")
    local = load_env_file(".env.local")
    env_name = os.environ.get("NODE_ENV", "development")
    env_specific = load_env_file(f".env.{env_name}")

    # Later files override earlier ones
    merged = {**base, **env_specific, **local}
    return merged

if __name__ == "__main__":
    env = load_all()
    print(f"Loaded {len(env)} variables")
    for key in sorted(env.keys()):
        # Mask sensitive values in output
        value = env[key]
        if any(s in key.upper() for s in ["SECRET", "PASSWORD", "TOKEN", "KEY"]):
            value = value[:4] + "****" if len(value) > 4 else "****"
        print(f"  {key}={value}")
```

## Schema Example

```yaml
# env.schema.yml
required:
  - DATABASE_URL
  - API_KEY
  - SECRET_KEY
types:
  PORT: int
  DEBUG: bool
  DATABASE_URL: url
  API_BASE_URL: url
optional:
  - LOG_LEVEL
  - CACHE_TTL
  - SENTRY_DSN
```

## Usage

```
User: Load and validate my environment
Agent: [reads .env files, validates against schema, reports status]
```
