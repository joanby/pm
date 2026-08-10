import pytest

from backend.app.ai.config import get_openrouter_api_key
from backend.app.ai.exceptions import OpenRouterConfigError


def test_get_openrouter_api_key_reads_from_env(monkeypatch) -> None:
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")

    assert get_openrouter_api_key() == "test-key"


def test_get_openrouter_api_key_requires_configuration(monkeypatch) -> None:
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    monkeypatch.setattr(
        "backend.app.ai.config._load_root_env",
        lambda: None,
    )

    with pytest.raises(OpenRouterConfigError, match="OPENROUTER_API_KEY is not configured"):
        get_openrouter_api_key()
