---
name: generating-settings
description: Generate Pydantic Settings configuration with YAML support. Creates config/settings.py and example.env.yaml for type-safe configuration management. Use when setting up application configuration, adding environment-specific settings, or migrating from os.getenv() to Pydantic Settings.
allowed-tools:
  - Read
  - Write
  - Glob
  - Grep
  - AskUserQuestion
  - Bash(uv add *)
---

# Generate Pydantic Settings Configuration

Create type-safe configuration management with Pydantic Settings and YAML support.

## Philosophy

- **Never use `os.getenv()` in app code** - Use Pydantic Settings
- **Priority: ENV vars > YAML file > defaults** - Flexible override chain
- **Type-safe configuration** - Pydantic validation at startup
- **Nested configuration** - Group related settings (postgres, aws, etc.)
- **Git-friendly** - Commit `example.env.yaml`, gitignore `*.env.yaml`

## Workflow

### 1. Check Existing Files

```text
Glob: config/settings.py, *settings*.py, example.env.yaml, *.env.yaml
```

If settings exist, ask via AskUserQuestion:

- "Merge sections" - Add new sections to existing config
- "Overwrite" - Replace entirely
- "Skip" - Don't modify

### 2. Ask Which Sections to Include

Present multi-select via AskUserQuestion:

```text
Which config sections do you need?

☐ postgres (PostgresSettings) - Database connection
☐ redis (RedisSettings) - Cache/queue connection
☐ aws (AWSSettings) - AWS region, endpoint URL
☐ elasticsearch (ElasticsearchSettings) - Search cluster
☐ sentry (SentrySettings) - Error monitoring
☐ logging (LoggingSettings) - Log level, format
☐ api (APISettings) - Host, port, CORS
```

### 3. Generate config/settings.py

```python
"""Application settings using Pydantic Settings + YAML.

Configuration priority:
    1. Environment variables (highest) - AWS__AWS_REGION=us-west-2
    2. YAML configuration file - local.env.yaml
    3. Default values (lowest) - Field(default="us-east-1")

Usage:
    from config.settings import settings

    region = settings.aws.aws_region
    db_host = settings.postgres.host
"""

from functools import lru_cache

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


# =============================================================================
# Settings Sections (selected by user)
# =============================================================================

class PostgresSettings(BaseModel):
    """PostgreSQL connection settings."""

    host: str = Field(default="localhost")
    port: int = Field(default=5432)
    database: str = Field(default="app")
    user: str = Field(default="postgres")
    password: str = Field(default="")

    @property
    def dsn(self) -> str:
        """Generate connection string."""
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"

    @property
    def async_dsn(self) -> str:
        """Generate async connection string."""
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"


class RedisSettings(BaseModel):
    """Redis connection settings."""

    host: str = Field(default="localhost")
    port: int = Field(default=6379)
    db: int = Field(default=0)
    password: str | None = Field(default=None)

    @property
    def url(self) -> str:
        """Generate Redis URL."""
        auth = f":{self.password}@" if self.password else ""
        return f"redis://{auth}{self.host}:{self.port}/{self.db}"


class AWSSettings(BaseModel):
    """AWS configuration."""

    aws_region: str = Field(default="us-east-1")
    endpoint_url: str | None = Field(default=None)
    access_key_id: str | None = Field(default=None)
    secret_access_key: str | None = Field(default=None)


class ElasticsearchSettings(BaseModel):
    """Elasticsearch cluster settings."""

    hosts: list[str] = Field(default_factory=lambda: ["http://localhost:9200"])
    username: str | None = Field(default=None)
    password: str | None = Field(default=None)
    verify_certs: bool = Field(default=True)


class SentrySettings(BaseModel):
    """Sentry error monitoring settings."""

    dsn: str | None = Field(default=None)
    environment: str | None = Field(default=None)
    traces_sample_rate: float = Field(default=0.1)


class LoggingSettings(BaseModel):
    """Logging configuration."""

    level: str = Field(default="INFO")
    format: str = Field(default="json")  # json or console
    show_timestamps: bool = Field(default=True)


class APISettings(BaseModel):
    """API server settings."""

    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000)
    debug: bool = Field(default=False)
    cors_origins: list[str] = Field(default_factory=lambda: ["*"])


# =============================================================================
# Main Settings
# =============================================================================

class Settings(BaseSettings):
    """Application settings.

    Configuration is loaded from:
        1. Environment variables (use __ for nesting: POSTGRES__HOST)
        2. YAML file (local.env.yaml)
        3. Default values defined above

    Example environment variables:
        ENVIRONMENT=production
        POSTGRES__HOST=db.example.com
        POSTGRES__PASSWORD=secret
        AWS__AWS_REGION=us-west-2
    """

    environment: str = Field(default="local")
    debug: bool = Field(default=False)

    # Include selected sections (remove unused)
    postgres: PostgresSettings = Field(default_factory=PostgresSettings)
    redis: RedisSettings = Field(default_factory=RedisSettings)
    aws: AWSSettings = Field(default_factory=AWSSettings)
    elasticsearch: ElasticsearchSettings = Field(default_factory=ElasticsearchSettings)
    sentry: SentrySettings = Field(default_factory=SentrySettings)
    logging: LoggingSettings = Field(default_factory=LoggingSettings)
    api: APISettings = Field(default_factory=APISettings)

    model_config = SettingsConfigDict(
        env_nested_delimiter="__",
        yaml_file="local.env.yaml",
        yaml_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance.

    Settings are loaded once and cached for the lifetime of the application.
    To reload settings, clear the cache: get_settings.cache_clear()
    """
    return Settings()


# Convenience export
settings = get_settings()
```

### 4. Generate example.env.yaml

```yaml
# =============================================================================
# Application Configuration
# =============================================================================
# Copy to local.env.yaml and customize for your environment.
# Priority: Environment variables > YAML values > defaults
#
# Environment variable mapping:
#   POSTGRES__HOST=myhost  ->  settings.postgres.host
#   AWS__AWS_REGION=us-west-2  ->  settings.aws.aws_region
# =============================================================================

environment: local
debug: true

# -----------------------------------------------------------------------------
# PostgreSQL
# -----------------------------------------------------------------------------
postgres:
  host: localhost
  port: 5432
  database: myapp
  user: postgres
  password: ""

# -----------------------------------------------------------------------------
# Redis
# -----------------------------------------------------------------------------
redis:
  host: localhost
  port: 6379
  db: 0
  password: null

# -----------------------------------------------------------------------------
# AWS
# -----------------------------------------------------------------------------
aws:
  aws_region: us-east-2
  endpoint_url: http://localhost:4566  # LocalStack for local dev

# -----------------------------------------------------------------------------
# Elasticsearch
# -----------------------------------------------------------------------------
elasticsearch:
  hosts:
    - http://localhost:9200
  username: null
  password: null
  verify_certs: false

# -----------------------------------------------------------------------------
# Sentry
# -----------------------------------------------------------------------------
sentry:
  dsn: null  # Set in production
  environment: local
  traces_sample_rate: 0.1

# -----------------------------------------------------------------------------
# Logging
# -----------------------------------------------------------------------------
logging:
  level: DEBUG
  format: console  # console for dev, json for production
  show_timestamps: true

# -----------------------------------------------------------------------------
# API
# -----------------------------------------------------------------------------
api:
  host: 0.0.0.0
  port: 8000
  debug: true
  cors_origins:
    - "*"
```

### 5. Update .gitignore

Append if not present:

```gitignore
# Local configuration (secrets)
*.env.yaml
!example.env.yaml
local.*.yaml
```

### 6. Add Dependency

If not already present in pyproject.toml:

```bash
uv add "pydantic-settings[yaml]>=2.0"
```

### 7. Report

```text
Created Pydantic Settings configuration:

config/settings.py
  - Settings class with selected sections
  - Type-safe configuration with validation
  - Cached singleton via get_settings()

example.env.yaml
  - Template with all settings documented
  - Copy to local.env.yaml for local development

.gitignore updated
  - *.env.yaml ignored (except example)

Dependency added:
  - pydantic-settings[yaml]>=2.0

Usage:
  from config.settings import settings

  db_host = settings.postgres.host
  aws_region = settings.aws.aws_region

Next steps:
  1. cp example.env.yaml local.env.yaml
  2. Edit local.env.yaml with your values
  3. Import settings in your code
```

## ENV Variable Mapping

| YAML Path | Environment Variable |
|-----------|---------------------|
| `postgres.host` | `POSTGRES__HOST` |
| `postgres.password` | `POSTGRES__PASSWORD` |
| `aws.aws_region` | `AWS__AWS_REGION` |
| `elasticsearch.hosts` | `ELASTICSEARCH__HOSTS='["http://es:9200"]'` |
| `logging.level` | `LOGGING__LEVEL` |

## Best Practices

1. **Never commit secrets** - Only `example.env.yaml` goes in git
2. **Use ENV vars in production** - More secure than files
3. **Validate early** - Settings load at import time
4. **Type hints everywhere** - Pydantic validates types
5. **Document sections** - Help future developers
