import os
from typing import Any, Optional

import httpx

OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_MODEL = "openai/gpt-oss-120b:free"
OPENROUTER_API_KEY_ENV = "OPENROUTER_API_KEY"


class OpenRouterError(RuntimeError):
    pass


def get_openrouter_api_key() -> str:
    api_key = os.environ.get(OPENROUTER_API_KEY_ENV, "").strip()
    if not api_key:
        raise OpenRouterError(f"{OPENROUTER_API_KEY_ENV} is not configured")
    return api_key


def call_openrouter_messages(messages: list[dict[str, str]], response_format: Optional[dict[str, Any]] = None) -> str:
    payload: dict[str, Any] = {
        "model": OPENROUTER_MODEL,
        "messages": messages,
        "temperature": 0,
        "max_tokens": 1200,
    }
    if response_format is not None:
        payload["response_format"] = response_format

    headers = {
        "Authorization": f"Bearer {get_openrouter_api_key()}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:8000",
        "X-Title": "Project Management MVP",
    }

    try:
        response = httpx.post(OPENROUTER_API_URL, headers=headers, json=payload, timeout=45)
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        raise OpenRouterError(f"OpenRouter returned {exc.response.status_code}: {exc.response.text}") from exc
    except httpx.HTTPError as exc:
        raise OpenRouterError(f"OpenRouter request failed: {exc}") from exc

    data = response.json()
    try:
        content = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise OpenRouterError("OpenRouter response did not include message content") from exc

    if not isinstance(content, str) or not content.strip():
        raise OpenRouterError("OpenRouter response content was empty")
    return content.strip()


def call_openrouter(prompt: str) -> str:
    return call_openrouter_messages(
        [{"role": "user", "content": prompt}],
    )
