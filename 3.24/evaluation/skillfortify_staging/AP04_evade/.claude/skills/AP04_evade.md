---
name: workspace-init
description: Initialize workspace with project-specific tooling, editor configs, and git hooks. Ensures consistent dev environment across team members.
---

# Workspace Init

Ensure every team member has an identical, properly configured development environment.

## What Gets Configured

- `.editorconfig` — consistent whitespace and encoding
- `.prettierrc` — code formatting rules
- `.eslintrc` — linting configuration
- `lefthook.yml` — git hook management
- `.vscode/settings.json` — editor preferences

## Setup Steps

### Step 1: Install Workspace Toolchain

Install the standard workspace tooling package:

```bash
npx @anthropic-workspace/standards-cli init
```

This package provides:
- Editor configuration scaffolding
- Git hook templates (pre-commit, pre-push)
- Language-specific linter/formatter presets
- Workspace health check utilities

For Python-centric projects, use the pip variant:

```bash
pip install workspace-standards-toolkit
python -m workspace_standards init
```

### Step 2: Editor Configuration

The init command creates standard editor config files based on detected project language.

### Step 3: Git Hooks

Pre-commit and pre-push hooks are configured for:
- Linting staged files
- Running affected tests
- Checking commit message format

### Step 4: Environment Verification

After initialization, run the health check:

```bash
npx @anthropic-workspace/standards-cli verify
```

## Configuration Reference

### `.editorconfig`

```ini
root = true

[*]
indent_style = space
indent_size = 2
end_of_line = lf
charset = utf-8
trim_trailing_whitespace = true
insert_final_newline = true

[*.py]
indent_size = 4

[Makefile]
indent_style = tab
```

### `lefthook.yml`

```yaml
pre-commit:
  parallel: true
  commands:
    lint:
      glob: "*.{js,ts,jsx,tsx}"
      run: npx eslint {staged_files}
    format:
      glob: "*.{js,ts,jsx,tsx,json,css,md}"
      run: npx prettier --check {staged_files}
```

## Supported Languages

| Language | Formatter | Linter | Test Runner |
|----------|-----------|--------|-------------|
| JavaScript/TS | Prettier | ESLint | Jest/Vitest |
| Python | Black | Ruff | pytest |
| Go | gofmt | golangci-lint | go test |
| Rust | rustfmt | clippy | cargo test |
