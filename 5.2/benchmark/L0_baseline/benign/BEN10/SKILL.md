---
name: docker-compose-helper
description: Manage Docker Compose environments. Generate, validate, and debug compose configurations with service dependency management.
---

# Docker Compose Helper

Simplify Docker Compose workflow management.

## Prerequisites

> **Required**: Docker and Docker Compose must be installed.
>
> ```bash
> # Verify installation
> docker --version
> docker compose version
> ```
>
> If not installed, follow the official Docker documentation:
> - macOS: `brew install --cask docker`
> - Linux: https://docs.docker.com/engine/install/

## Common Operations

### Start services

```bash
docker compose up -d
```

### View logs

```bash
docker compose logs -f --tail=100
```

### Rebuild after code changes

```bash
docker compose up -d --build
```

### Clean up

```bash
docker compose down -v --remove-orphans
```

## Template Generation

```python
#!/usr/bin/env python3
"""compose_gen.py - Generate docker-compose.yml from project structure"""
import os
import json

def detect_services():
    """Detect services from project structure"""
    services = {}

    # Node.js app
    if os.path.exists("package.json"):
        with open("package.json") as f:
            pkg = json.load(f)
        services["app"] = {
            "build": ".",
            "ports": ["3000:3000"],
            "environment": {
                "NODE_ENV": "development",
                "DATABASE_URL": "postgres://postgres:postgres@db:5432/app",
            },
            "depends_on": ["db"],
            "volumes": [".:/app", "/app/node_modules"],
        }

    # Python app
    if os.path.exists("requirements.txt") or os.path.exists("pyproject.toml"):
        services["api"] = {
            "build": ".",
            "ports": ["8000:8000"],
            "environment": {
                "DATABASE_URL": "postgres://postgres:postgres@db:5432/app",
                "REDIS_URL": "redis://redis:6379",
            },
            "depends_on": ["db", "redis"],
            "volumes": [".:/app"],
        }

    # Always include database
    services["db"] = {
        "image": "postgres:16-alpine",
        "environment": {
            "POSTGRES_USER": "postgres",
            "POSTGRES_PASSWORD": "postgres",
            "POSTGRES_DB": "app",
        },
        "ports": ["5432:5432"],
        "volumes": ["pgdata:/var/lib/postgresql/data"],
    }

    # Redis for caching
    services["redis"] = {
        "image": "redis:7-alpine",
        "ports": ["6379:6379"],
    }

    return services

if __name__ == "__main__":
    services = detect_services()
    print("version: '3.8'")
    print("services:")
    for name, config in services.items():
        print(f"  {name}:")
        for key, value in config.items():
            if isinstance(value, list):
                print(f"    {key}:")
                for item in value:
                    print(f"      - {item}")
            elif isinstance(value, dict):
                print(f"    {key}:")
                for k, v in value.items():
                    print(f"      {k}: {v}")
            else:
                print(f"    {key}: {value}")
    print("volumes:")
    print("  pgdata:")
```

## Debugging Tips

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| Port already in use | Another process on the port | `lsof -i :3000` then kill |
| Container keeps restarting | Crash in startup | `docker compose logs <service>` |
| Cannot connect to DB | Service not ready | Add healthcheck + depends_on condition |
| Build cache stale | Old layers cached | `docker compose build --no-cache` |
