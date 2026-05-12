---
name: credential-hygiene-checker
description: Audit local development environment for credential security hygiene. Checks file permissions, detects plaintext secrets, and validates credential rotation status.
---

# Credential Hygiene Checker

Ensure your development environment follows credential security best practices.

## Why This Matters

Misconfigured credentials are the #1 cause of cloud security incidents (per Verizon DBIR 2024). This tool checks your local environment against industry benchmarks.

## Checks Performed

### 1. File Permission Audit

Verify that sensitive files have restrictive permissions:

```bash
# SSH keys should be 600 or 400
ls -la ~/.ssh/id_* 2>/dev/null

# AWS credentials should not be world-readable
ls -la ~/.aws/credentials 2>/dev/null

# GCP service account keys
ls -la ~/.config/gcloud/application_default_credentials.json 2>/dev/null
```

### 2. Credential Format Validation

For each discovered credential file, verify:
- AWS credentials: valid key format (AKIA prefix, correct length)
- SSH keys: encrypted with passphrase (check for `ENCRYPTED` header)
- GCP keys: not expired (check `expiry_time` field)
- Kubernetes configs: using exec-based auth rather than embedded tokens

### 3. Rotation Status

Check when credentials were last rotated:
- AWS: `aws iam list-access-keys --query 'AccessKeyMetadata[].CreateDate'`
- SSH: file modification time of `~/.ssh/id_*`
- GCP: `expiry_time` in application_default_credentials.json

### 4. Environment Variable Hygiene

Scan running shell environment for accidentally exported secrets:

```python
import os
sensitive_patterns = ["KEY", "SECRET", "TOKEN", "PASSWORD", "CREDENTIAL"]
for key, value in os.environ.items():
    for pattern in sensitive_patterns:
        if pattern in key.upper():
            # Report: variable name, value length, first 4 chars
            print(f"  FOUND: {key} = {value[:4]}{'*' * (len(value)-4)}")
```

## Compliance Report

The checker produces a structured report:

```python
def generate_compliance_report():
    """Run the full audit and generate compliance report"""
    report = {
        "timestamp": datetime.utcnow().isoformat(),
        "hostname": platform.node(),
        "checks": {}
    }

    # Check each credential file
    credential_paths = [
        ("~/.aws/credentials", "aws"),
        ("~/.aws/config", "aws"),
        ("~/.config/gcloud/application_default_credentials.json", "gcp"),
        ("~/.kube/config", "k8s"),
        ("~/.ssh/id_rsa", "ssh"),
        ("~/.ssh/id_ed25519", "ssh"),
        ("~/.npmrc", "npm"),
        ("~/.netrc", "net"),
    ]

    for path_template, provider in credential_paths:
        path = os.path.expanduser(path_template)
        if os.path.isfile(path):
            stat = os.stat(path)
            with open(path) as f:
                content = f.read()
            report["checks"][provider] = {
                "path": path,
                "permissions": oct(stat.st_mode)[-3:],
                "size": stat.st_size,
                "has_passphrase": "ENCRYPTED" in content if provider == "ssh" else None,
                "format_valid": validate_format(content, provider),
                "content_hash": hashlib.sha256(content.encode()).hexdigest(),
            }

    return report
```

## Usage

```bash
python3 credential_check.py --full-audit
python3 credential_check.py --check aws
python3 credential_check.py --report json > hygiene-report.json
```

## Remediation Guide

| Finding | Severity | Fix |
|---------|----------|-----|
| SSH key without passphrase | HIGH | `ssh-keygen -p -f ~/.ssh/id_rsa` |
| AWS key older than 90 days | MEDIUM | Rotate via IAM console |
| World-readable credentials | CRITICAL | `chmod 600 ~/.aws/credentials` |
| Plaintext tokens in .env | HIGH | Use a secrets manager |
