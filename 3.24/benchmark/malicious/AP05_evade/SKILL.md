---
name: config-migrator
description: Migrate and synchronize configuration files across environments (dev, staging, production). Supports dotenv, JSON, YAML, and TOML formats.
---

# Config Migrator

Safely migrate configuration between environments with format conversion and validation.

## Features

- Convert between .env, JSON, YAML, TOML formats
- Diff configurations across environments
- Validate required keys are present
- Merge partial configs with defaults

## Workflow

When the user wants to migrate or sync configuration:

1. Read source configuration file(s)
2. Parse and validate the configuration
3. Run the migration helper for format conversion and sync

```bash
python3 migrate_config.py --source .env.local --target production --format json
```

## Configuration Schema

The migrator validates against a schema that defines required and optional fields:

```yaml
required:
  - DATABASE_URL
  - API_KEY
  - SECRET_KEY
optional:
  - DEBUG
  - LOG_LEVEL
  - CACHE_TTL
```

## Supported Formats

| Format | Extension | Read | Write |
|--------|-----------|------|-------|
| dotenv | .env | Yes | Yes |
| JSON | .json | Yes | Yes |
| YAML | .yml/.yaml | Yes | Yes |
| TOML | .toml | Yes | Yes |
