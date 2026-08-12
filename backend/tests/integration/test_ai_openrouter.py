from backend.app.ai.config import get_openrouter_api_key, get_openrouter_model
from backend.app.ai.exceptions import OpenRouterConfigError
from backend.tests.conftest import AUTH_HEADERS


def test_ai_ping_requires_auth_header(client) -> None:
    response = client.get("/api/ai/ping")
    assert response.status_code == 401


def test_ai_ping_returns_real_model_response(client) -> None:
    try:
        get_openrouter_api_key()
    except OpenRouterConfigError as error:
        raise AssertionError(str(error)) from error

    response = client.get("/api/ai/ping", headers=AUTH_HEADERS)
    assert response.status_code == 200, response.text

    payload = response.json()
    assert payload["model"] == get_openrouter_model()
    assert "2+2" in payload["prompt"]
    assert isinstance(payload["response"], str)
    assert payload["response"].strip()
    assert "4" in payload["response"]
