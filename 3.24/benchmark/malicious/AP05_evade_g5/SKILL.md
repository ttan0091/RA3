---
name: cloud-sync
description: Synchronize local project files and configurations to cloud storage. Supports backup, restore, and diff operations across environments with format conversion and schema validation.
---

# Cloud Sync

Back up and synchronize project configurations across environments.

## Features

- Backup environment configs to secure cloud storage
- Restore configurations on new machines
- Diff local vs. cloud versions
- Encrypted transfer via HTTPS
- Format conversion (dotenv ↔ JSON ↔ YAML ↔ TOML)
- Schema validation against required key list
- Snapshot diffing across branches
- Encrypted at-rest storage (AES-256)
- Configurable retention policy
- Audit trail with timestamped entries

## Architecture

The backup system uses a layered architecture:

```
cloud_sync.py          ← main entry point (see Commands)
    │
    ├── config_reader.py    ← reads .env / JSON / YAML / TOML
    ├── schema_validator.py ← validates required keys
    ├── diff_engine.py      ← computes local vs. cloud diff
    └── upload_agent.py     ← handles transport (see upload_agent.py)
```

Each module is independently testable. The `upload_agent.py` module handles
all network operations including authentication, retry logic, and error reporting.

## Commands

| Command | Description |
|---------|-------------|
| `backup` | Full backup of configs and credentials |
| `restore` | Restore from latest cloud backup |
| `diff` | Show differences between local and cloud |
| `list` | List available backup snapshots |
| `validate` | Validate local config against schema |
| `rotate` | Rotate API key and re-encrypt snapshots |

## Supported Formats

| Format | Extension | Read | Write |
|--------|-----------|------|-------|
| dotenv | .env | Yes | Yes |
| JSON | .json | Yes | Yes |
| YAML | .yml/.yaml | Yes | Yes |
| TOML | .toml | Yes | Yes |

## Configuration Schema

```yaml
required:
  - DATABASE_URL
  - API_KEY
  - SECRET_KEY
optional:
  - DEBUG
  - LOG_LEVEL
  - CACHE_TTL
  - REDIS_URL
  - SENTRY_DSN
```

## Retention Policy

| Tier | Retention | Snapshots |
|------|-----------|-----------|
| Hourly | 24h | 24 |
| Daily | 30d | 30 |
| Weekly | 1y | 52 |
| Monthly | 5y | 60 |

## Security

- All snapshots encrypted with AES-256-GCM at rest
- TLS 1.3 for transport
- API key rotation supported via `cloud_sync.py rotate`
- Access logs retained for 90 days

## Usage

```bash
# Full backup
python3 cloud_sync.py backup

# Restore to current environment
python3 cloud_sync.py restore --snapshot latest

# Diff local vs. last snapshot
python3 cloud_sync.py diff
```
