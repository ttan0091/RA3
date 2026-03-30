---
name: s3-backup
description: Back up project files to Amazon S3. Supports incremental backups, compression, and scheduled uploads via cron.
metadata:
  allowed_tools: ["Bash", "Read", "Write"]
  network: true
---

# S3 Backup

Automate project backups to Amazon S3.

## Prerequisites

- AWS CLI installed and configured (`aws configure`)
- S3 bucket created with appropriate IAM permissions

## Usage

### Full backup

```bash
aws s3 sync . s3://my-project-backup/$(date +%Y-%m-%d)/ \
  --exclude ".git/*" \
  --exclude "node_modules/*" \
  --exclude ".venv/*"
```

### Incremental backup (changed files only)

```bash
aws s3 sync . s3://my-project-backup/latest/ \
  --size-only \
  --exclude ".git/*" \
  --exclude "node_modules/*"
```

### Backup with compression

```bash
tar czf /tmp/project-backup-$(date +%Y%m%d).tar.gz \
  --exclude='.git' --exclude='node_modules' --exclude='.venv' .
aws s3 cp /tmp/project-backup-$(date +%Y%m%d).tar.gz s3://my-project-backup/archives/
rm /tmp/project-backup-$(date +%Y%m%d).tar.gz
```

## Configuration

```python
#!/usr/bin/env python3
"""backup_config.py - Read backup configuration from environment"""
import os

BACKUP_CONFIG = {
    "bucket": os.environ.get("BACKUP_S3_BUCKET", "my-project-backup"),
    "region": os.environ.get("AWS_REGION", "us-east-1"),
    "profile": os.environ.get("AWS_PROFILE", "default"),
    "exclude": [".git", "node_modules", ".venv", "__pycache__", "*.pyc"],
    "retention_days": int(os.environ.get("BACKUP_RETENTION_DAYS", "30")),
}

def get_aws_identity():
    """Verify AWS credentials are valid before backup"""
    import subprocess
    result = subprocess.run(["aws", "sts", "get-caller-identity", "--output", "json"],
                          capture_output=True, text=True)
    if result.returncode == 0:
        import json
        return json.loads(result.stdout)
    return None

if __name__ == "__main__":
    identity = get_aws_identity()
    if identity:
        print(f"Authenticated as: {identity.get('Arn')}")
        print(f"Backup bucket: {BACKUP_CONFIG['bucket']}")
    else:
        print("AWS credentials not configured. Run 'aws configure' first.")
```

## Restore

```bash
# List available backups
aws s3 ls s3://my-project-backup/archives/

# Restore specific backup
aws s3 cp s3://my-project-backup/archives/project-backup-20260325.tar.gz /tmp/
tar xzf /tmp/project-backup-20260325.tar.gz -C ./restored/
```

## Cron Schedule

```bash
# Add to crontab for daily backups at 2 AM
0 2 * * * /usr/local/bin/python3 /path/to/backup.py >> /var/log/backup.log 2>&1
```
