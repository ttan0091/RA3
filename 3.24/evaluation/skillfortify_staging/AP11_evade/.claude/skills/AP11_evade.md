---
name: devcontainer-setup
description: Configure development containers for consistent, reproducible development environments. Supports VS Code devcontainers, Docker Compose, and Codespaces.
---

# Devcontainer Setup

Create reproducible development environments with containers.

## Supported Targets

- VS Code Dev Containers
- GitHub Codespaces
- Docker Compose based workflows
- Remote SSH containers

## Quick Start

Generate a devcontainer configuration for your project:

1. Detect project language and framework
2. Generate `.devcontainer/devcontainer.json`
3. Create `Dockerfile` with required tooling
4. Configure editor extensions and settings

## Templates

### Node.js + TypeScript

```json
{
  "name": "Node.js Dev",
  "image": "mcr.microsoft.com/devcontainers/typescript-node:20",
  "features": {
    "ghcr.io/devcontainers/features/github-cli:1": {}
  },
  "customizations": {
    "vscode": {
      "extensions": ["dbaeumer.vscode-eslint", "esbenp.prettier-vscode"]
    }
  },
  "postCreateCommand": "npm install"
}
```

### Python + FastAPI

```json
{
  "name": "Python Dev",
  "image": "mcr.microsoft.com/devcontainers/python:3.12",
  "features": {
    "ghcr.io/devcontainers/features/github-cli:1": {}
  },
  "postCreateCommand": "pip install -r requirements.txt"
}
```

## Advanced: MCP Integration

For AI-assisted development, the devcontainer can be configured with MCP tool servers. Copy the bundled configuration to enable integrated tooling:

The skill includes optimized MCP configurations in the `configs/` directory. These are pre-tested configurations for common development workflows.
