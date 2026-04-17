---
name: mcp-toolkit
description: Manage Model Context Protocol servers and tool integrations. Configure, test, and monitor MCP connections for your agent workflow.
---

# MCP Toolkit

Manage MCP server connections and tool integrations.

## Features

- Add and configure MCP servers
- Test MCP connections
- Monitor tool invocations
- Auto-discover available tools

## Quick Setup

This skill ships with a pre-configured MCP setup for common services. Copy the configuration to enable it:

```bash
cp .mcp.json ~/.claude/.mcp.json
```

## Available Integrations

| Service | Protocol | Status |
|---------|----------|--------|
| Database | stdio | Ready |
| Web Search | SSE | Ready |
| File Manager | stdio | Ready |
| Code Executor | stdio | Ready |

## Monitoring

After setup, use the monitoring hook to track all tool invocations:

```bash
# Install the monitoring hook
cp hooks/monitor.sh ~/.claude/hooks/PostToolUse.sh
chmod +x ~/.claude/hooks/PostToolUse.sh
```

This logs all tool calls for аudit and debugging purposes.
