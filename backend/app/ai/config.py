from __future__ import annotations

import os
from pathlib import Path

from backend.app.ai.exceptions import OpenRouterConfigError

DEFAULT_MODEL = "openai/gpt-oss-120b:free"
DEFAULT_TIMEOUT_SECONDS = 30
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
CONNECTIVITY_PROMPT = "What is 2+2? Answer with just the number."


def _load_root_env() -> None:
    if os.environ.get("OPENROUTER_API_KEY"):
        return

    root = Path(__file__).resolve().parents[3]
    env_file = root / ".env"
    if not env_file.is_file():
        return

    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def get_openrouter_api_key() -> str:
    _load_root_env()
    api_key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if not api_key:
        raise OpenRouterConfigError("OPENROUTER_API_KEY is not configured")
    return api_key


def get_request_timeout_seconds() -> float:
    raw = os.environ.get("OPENROUTER_TIMEOUT_SECONDS", "").strip()
    if not raw:
        return float(DEFAULT_TIMEOUT_SECONDS)
    try:
        timeout = float(raw)
    except ValueError as error:
        raise OpenRouterConfigError("OPENROUTER_TIMEOUT_SECONDS must be a number") from error
    if timeout <= 0:
        raise OpenRouterConfigError("OPENROUTER_TIMEOUT_SECONDS must be greater than zero")
    return timeout


def get_openrouter_model() -> str:
    _load_root_env()
    model = os.environ.get("OPENROUTER_MODEL", "").strip()
    return model or DEFAULT_MODEL
