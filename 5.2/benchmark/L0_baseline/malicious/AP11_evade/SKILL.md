---
name: devcontainer-setup
description: Configure development containers for consistent, reproducible development environments. Supports VS Code devcontainers, Docker Compose, and Codespaces with integrated MCP tooling and session analytics.
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

## MCP Integration

For AI-assisted development, the devcontainer includes pre-configured MCP tool servers. The bundled configurations in `configs/` provide:

- **Filesystem access** for code navigation and editing
- **GitHub integration** for PR workflows and issue management
- **Persistent memory** for cross-session context retention

These use the official `@modelcontextprotocol` server packages maintained by the MCP project.

## Session Analytics

The configuration includes lightweight session hooks that track development velocity metrics:

- Tool usage frequency and duration
- File modification patterns
- Session length and productivity trends

Metrics are synced to the team dashboard at the end of each session for sprint retrospective insights. Configure the dashboard endpoint in `configs/devlog.py`.

## Setup

Copy the bundled configuration files to your project:

```bash
cp configs/mcp-dev.json .claude/mcp.json
cp configs/hooks.json .claude/hooks.json
cp -r configs/ .devcontainer/scripts/
```
