from __future__ import annotations

from typing import Any

import httpx

from backend.app.ai.config import (
    CONNECTIVITY_PROMPT,
    OPENROUTER_API_URL,
    get_openrouter_api_key,
    get_openrouter_model,
    get_request_timeout_seconds,
)
from backend.app.ai.exceptions import OpenRouterError, OpenRouterResponseError


def build_chat_request(
    model: str,
    messages: list[dict[str, str]],
    *,
    json_mode: bool = False,
) -> dict[str, Any]:
    request: dict[str, Any] = {
        "model": model,
        "messages": messages,
    }
    if json_mode:
        request["response_format"] = {"type": "json_object"}
    return request


def build_openrouter_headers(api_key: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:8000",
        "X-OpenRouter-Title": "Project Management MVP",
    }


def parse_chat_response(payload: dict[str, Any]) -> str:
    choices = payload.get("choices")
    if not isinstance(choices, list) or not choices:
        raise OpenRouterResponseError("OpenRouter response missing choices")

    first_choice = choices[0]
    if not isinstance(first_choice, dict):
        raise OpenRouterResponseError("OpenRouter choice has invalid format")

    message = first_choice.get("message")
    if not isinstance(message, dict):
        raise OpenRouterResponseError("OpenRouter choice missing message")

    content = message.get("content")
    if isinstance(content, str) and content.strip():
        return content.strip()

    reasoning = message.get("reasoning")
    if isinstance(reasoning, str) and reasoning.strip():
        return reasoning.strip()

    raise OpenRouterResponseError("OpenRouter response missing assistant content")


class OpenRouterClient:
    def __init__(
        self,
        *,
        api_key: str | None = None,
        timeout_seconds: float | None = None,
        model: str | None = None,
    ) -> None:
        self.api_key = api_key or get_openrouter_api_key()
        self.timeout_seconds = timeout_seconds if timeout_seconds is not None else get_request_timeout_seconds()
        self.model = model if model is not None else get_openrouter_model()

    def complete(self, prompt: str) -> str:
        return self.complete_messages([{"role": "user", "content": prompt}])

    def complete_messages(self, messages: list[dict[str, str]], *, json_mode: bool = False) -> str:
        request_body = build_chat_request(self.model, messages, json_mode=json_mode)
        headers = build_openrouter_headers(self.api_key)

        try:
            with httpx.Client(timeout=self.timeout_seconds) as client:
                response = client.post(OPENROUTER_API_URL, headers=headers, json=request_body)
                response.raise_for_status()
        except httpx.TimeoutException as error:
            raise OpenRouterError("OpenRouter request timed out") from error
        except httpx.HTTPStatusError as error:
            detail = _extract_error_detail(error.response)
            raise OpenRouterError(f"OpenRouter request failed ({error.response.status_code}): {detail}") from error
        except httpx.HTTPError as error:
            raise OpenRouterError(f"OpenRouter network error: {error}") from error

        try:
            payload = response.json()
        except ValueError as error:
            raise OpenRouterResponseError("OpenRouter returned invalid JSON") from error

        if not isinstance(payload, dict):
            raise OpenRouterResponseError("OpenRouter returned unexpected payload")

        return parse_chat_response(payload)

    def ping(self) -> str:
        return self.complete(CONNECTIVITY_PROMPT)


def _extract_error_detail(response: httpx.Response) -> str:
    try:
        payload = response.json()
    except ValueError:
        text = response.text.strip()
        return text or "Unknown error"

    if isinstance(payload, dict):
        error = payload.get("error")
        if isinstance(error, dict):
            message = error.get("message")
            if isinstance(message, str) and message.strip():
                return message.strip()
        message = payload.get("message")
        if isinstance(message, str) and message.strip():
            return message.strip()

    return "Unknown error"
