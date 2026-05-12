"""Shared DeepSeek client for the 5.2 evasion experiments.

Model policy:
- judge / detector roles    -> deepseek-v4-pro   (highest fidelity, slower)
- attacker / paraphrase     -> deepseek-v4-flash (fast, cheap iteration)

All LLM calls in the 5.2 experiments go through this module so the choice is
auditable in one place.
"""
from __future__ import annotations

import json
import os
import re
import time
from pathlib import Path
from typing import Optional

import requests

ROOT = Path(__file__).resolve().parents[3]   # /Users/tan/Desktop/RA3
ENV_FILE = ROOT / ".env"

# Default to v4-flash for both roles. v4-pro is a heavy reasoning model that can
# take several minutes per query — too slow for the ~200-sample x 5-scanner matrix
# we need to run. To use v4-pro for higher-fidelity judging on a smaller subset,
# export DS_JUDGE_MODEL=deepseek-v4-pro for that run.
JUDGE_MODEL = os.environ.get("DS_JUDGE_MODEL", "deepseek-v4-flash")
ATTACKER_MODEL = os.environ.get("DS_ATTACKER_MODEL", "deepseek-v4-flash")

DEFAULT_TIMEOUT = int(os.environ.get("DS_TIMEOUT_SEC", "180"))
DEFAULT_MAX_TOKENS = int(os.environ.get("DS_MAX_TOKENS", "4000"))
DEFAULT_RETRIES = int(os.environ.get("DS_RETRIES", "3"))


def load_dotenv(path: Path = ENV_FILE) -> None:
    if not path.exists():
        return
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def get_api_key() -> str:
    load_dotenv()
    key = os.environ.get("DEEPSEEK_API_KEY", "").strip()
    if not key:
        raise RuntimeError("DEEPSEEK_API_KEY not found in environment or .env")
    return key


def base_url() -> str:
    base = os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com").rstrip("/")
    if base.endswith("/chat/completions"):
        base = base[: -len("/chat/completions")]
    return base


def _api_url() -> str:
    return f"{base_url()}/chat/completions"


def call(
    system_prompt: str,
    user_message: str,
    *,
    model: str,
    temperature: float = 0.0,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    timeout: int = DEFAULT_TIMEOUT,
    retries: int = DEFAULT_RETRIES,
    api_key: Optional[str] = None,
) -> dict:
    """Call DeepSeek chat completions. Returns the raw JSON dict."""
    if api_key is None:
        api_key = get_api_key()
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    last_err = None
    for attempt in range(1, retries + 1):
        try:
            resp = requests.post(
                _api_url(),
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=timeout,
            )
            if resp.status_code in {429, 500, 502, 503, 504}:
                last_err = RuntimeError(f"HTTP {resp.status_code}: {resp.text[:200]}")
                time.sleep(min(2 ** attempt, 12))
                continue
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as e:
            last_err = e
            if attempt < retries:
                time.sleep(min(2 ** attempt, 12))
                continue
            break
    raise RuntimeError(f"DeepSeek call failed after {retries} attempts: {last_err}")


def judge(system_prompt: str, user_message: str, **kwargs) -> dict:
    """Detector / judge role: use the strong model."""
    return call(system_prompt, user_message, model=JUDGE_MODEL, **kwargs)


def attacker(system_prompt: str, user_message: str, **kwargs) -> dict:
    """Attacker / paraphrase / generator role: use the fast model."""
    return call(system_prompt, user_message, model=ATTACKER_MODEL, **kwargs)


def extract_text(raw: dict) -> str:
    choices = raw.get("choices", [])
    if not choices:
        return ""
    msg = choices[0].get("message", {})
    content = msg.get("content", "")
    return content if isinstance(content, str) else ""


def parse_json(text: str) -> dict:
    """Extract a JSON object from a model response."""
    m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL | re.IGNORECASE)
    if m:
        try:
            return json.loads(m.group(1))
        except json.JSONDecodeError:
            pass
    s, e = text.find("{"), text.rfind("}")
    if s != -1 and e != -1:
        try:
            return json.loads(text[s : e + 1])
        except json.JSONDecodeError:
            pass
    return {"_parse_failed": True, "_raw_excerpt": text[:1500]}
