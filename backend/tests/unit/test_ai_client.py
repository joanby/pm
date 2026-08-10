import pytest

from backend.app.ai.client import build_chat_request, build_openrouter_headers, parse_chat_response
from backend.app.ai.config import CONNECTIVITY_PROMPT, DEFAULT_MODEL
from backend.app.ai.exceptions import OpenRouterResponseError


def test_build_chat_request_uses_model_and_messages() -> None:
    payload = build_chat_request(
        "openai/gpt-oss-120b",
        [{"role": "user", "content": "Hello"}],
        json_mode=True,
    )

    assert payload == {
        "model": "openai/gpt-oss-120b",
        "messages": [{"role": "user", "content": "Hello"}],
        "response_format": {"type": "json_object"},
    }


def test_build_openrouter_headers_includes_bearer_token() -> None:
    headers = build_openrouter_headers("test-key")

    assert headers["Authorization"] == "Bearer test-key"
    assert headers["Content-Type"] == "application/json"
    assert headers["HTTP-Referer"] == "http://localhost:8000"
    assert headers["X-OpenRouter-Title"] == "Project Management MVP"


def test_parse_chat_response_extracts_assistant_content() -> None:
    payload = {
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    "content": "4",
                }
            }
        ]
    }

    assert parse_chat_response(payload) == "4"


def test_parse_chat_response_rejects_missing_content() -> None:
    with pytest.raises(OpenRouterResponseError, match="missing assistant content"):
        parse_chat_response({"choices": [{"message": {"role": "assistant", "content": "   "}}]})


def test_connectivity_prompt_is_math_question() -> None:
    assert "2+2" in CONNECTIVITY_PROMPT
    assert DEFAULT_MODEL == "openai/gpt-oss-120b:free"
