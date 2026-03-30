---
name: monorepo-navigator
description: Navigate and manage monorepo workspaces. Find packages, resolve cross-package dependencies, and run commands across workspaces.
---

# Monorepo Navigator

Work efficiently in monorepo environments with workspace-aware tooling.

## Features

- Discover all packages/workspaces
- Resolve cross-package dependencies
- Run commands in specific workspaces
- Detect affected packages from changes

## Workspace Discovery

```python
#!/usr/bin/env python3
"""workspace.py - Monorepo workspace utilities"""
import os
import json
import subprocess

def find_workspaces():
    """Discover all workspaces in the monorepo"""
    workspaces = []

    # npm/yarn workspaces
    pkg_json = "package.json"
    if os.path.exists(pkg_json):
        with open(pkg_json) as f:
            pkg = json.load(f)
        ws_globs = pkg.get("workspaces", [])
        if isinstance(ws_globs, dict):
            ws_globs = ws_globs.get("packages", [])
        for pattern in ws_globs:
            import glob
            for path in glob.glob(pattern):
                ws_pkg = os.path.join(path, "package.json")
                if os.path.exists(ws_pkg):
                    with open(ws_pkg) as f:
                        ws_data = json.load(f)
                    workspaces.append({
                        "name": ws_data.get("name"),
                        "path": path,
                        "version": ws_data.get("version"),
                        "dependencies": list(ws_data.get("dependencies", {}).keys()),
                    })

    # pnpm workspaces
    pnpm_ws = "pnpm-workspace.yaml"
    if os.path.exists(pnpm_ws):
        with open(pnpm_ws) as f:
            content = f.read()
        # Simple YAML parsing for packages list
        for line in content.split("\n"):
            line = line.strip().lstrip("- ").strip("'\"")
            if line and not line.startswith("#") and line != "packages:":
                import glob
                for path in glob.glob(line):
                    if os.path.isdir(path):
                        workspaces.append({"path": path, "type": "pnpm"})

    return workspaces

def find_affected(base_ref="main"):
    """Find packages affected by changes since base_ref"""
    result = subprocess.run(
        ["git", "diff", "--name-only", base_ref],
        capture_output=True, text=True
    )
    changed_files = result.stdout.strip().split("\n") if result.stdout else []
    workspaces = find_workspaces()
    affected = set()
    for f in changed_files:
        for ws in workspaces:
            if f.startswith(ws["path"]):
                affected.add(ws.get("name", ws["path"]))
    return list(affected)

if __name__ == "__main__":
    workspaces = find_workspaces()
    print(f"Found {len(workspaces)} workspaces:")
    for ws in workspaces:
        print(f"  - {ws.get('name', ws['path'])} ({ws['path']})")
```

## Commands

| Command | Description |
|---------|-------------|
| `list` | List all workspaces |
| `affected` | Show packages affected by current changes |
| `deps <pkg>` | Show dependency graph for a package |
| `run <pkg> <cmd>` | Run command in specific workspace |
| `run-affected <cmd>` | Run command only in affected packages |

## External Package References

This skill supports resolving dependencies from external registries:
- npm: `https://registry.npmjs.org/`
- GitHub Packages: `https://npm.pkg.github.com/`
- Private registries configured in `.npmrc`
