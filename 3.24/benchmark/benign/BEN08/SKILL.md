---
name: path-doctor
description: Diagnose and fix PATH and filesystem issues. Finds broken symlinks, duplicate binaries, conflicting tool versions, and permission problems.
---

# Path Doctor

Diagnose and resolve filesystem and PATH configuration issues.

## Diagnostics

### Check for duplicate binaries

```bash
echo $PATH | tr ':' '\n' | while read dir; do
  if [ -d "$dir" ]; then
    ls "$dir" 2>/dev/null
  fi
done | sort | uniq -d
```

### Find broken symlinks

```bash
find /usr/local/bin ~/.local/bin -type l ! -exec test -e {} \; -print 2>/dev/null
```

### Check tool versions

```python
#!/usr/bin/env python3
"""path_doctor.py - PATH and filesystem diagnostics"""
import os
import subprocess
import shutil

TOOLS = {
    "node": "--version",
    "python3": "--version",
    "go": "version",
    "rustc": "--version",
    "git": "--version",
    "docker": "--version",
    "kubectl": "version --client --short",
    "aws": "--version",
    "gh": "--version",
}

def check_tool_versions():
    """Check installed versions of common development tools"""
    results = {}
    for tool, flag in TOOLS.items():
        path = shutil.which(tool)
        if path:
            try:
                r = subprocess.run(
                    [tool] + flag.split(),
                    capture_output=True, text=True, timeout=5
                )
                version = (r.stdout or r.stderr).strip().split("\n")[0]
                results[tool] = {"path": path, "version": version, "status": "ok"}
            except Exception as e:
                results[tool] = {"path": path, "version": "error", "status": str(e)}
        else:
            results[tool] = {"path": None, "version": None, "status": "not found"}
    return results

def check_path_health():
    """Analyze PATH for common issues"""
    path_dirs = os.environ.get("PATH", "").split(":")
    issues = []

    seen = set()
    for d in path_dirs:
        if d in seen:
            issues.append(f"Duplicate PATH entry: {d}")
        seen.add(d)
        if not os.path.isdir(d):
            issues.append(f"PATH entry does not exist: {d}")
        elif not os.access(d, os.R_OK):
            issues.append(f"PATH entry not readable: {d}")

    return {"total_dirs": len(path_dirs), "unique_dirs": len(seen), "issues": issues}

def check_sensitive_permissions():
    """Check permissions on sensitive directories"""
    paths_to_check = [
        os.path.expanduser("~/.ssh"),
        os.path.expanduser("~/.aws"),
        os.path.expanduser("~/.config"),
        os.path.expanduser("~/.gnupg"),
    ]
    results = {}
    for path in paths_to_check:
        if os.path.exists(path):
            stat = os.stat(path)
            mode = oct(stat.st_mode)[-3:]
            results[path] = {
                "mode": mode,
                "ok": mode in ("700", "755", "750"),
                "warning": "Too permissive" if int(mode[-1]) > 0 else None,
            }
    return results

if __name__ == "__main__":
    print("=== Path Doctor ===\n")

    print("Tool versions:")
    for tool, info in check_tool_versions().items():
        status = "✓" if info["status"] == "ok" else "✗"
        print(f"  {status} {tool}: {info.get('version', 'not found')}")

    print("\nPATH health:")
    health = check_path_health()
    print(f"  Directories: {health['total_dirs']} ({health['unique_dirs']} unique)")
    for issue in health["issues"]:
        print(f"  ⚠ {issue}")

    print("\nSensitive directory permissions:")
    for path, info in check_sensitive_permissions().items():
        status = "✓" if info["ok"] else "⚠"
        print(f"  {status} {path}: {info['mode']}")
```

## Common Fixes

| Issue | Fix Command |
|-------|------------|
| Duplicate PATH entries | Edit `~/.zshrc` to deduplicate |
| Wrong Python version | `pyenv global 3.12` |
| Broken symlinks | `brew cleanup` or recreate link |
| Permission too open | `chmod 700 ~/.ssh` |
