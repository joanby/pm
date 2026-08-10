"""Regression: importing backend.app.ai.router must never construct an
OpenRouterClient. It used to build AiService()/ChatService() at module
scope, which eagerly constructs an OpenRouterClient() and therefore
resolves OPENROUTER_API_KEY at import time — crashing every consumer of
backend.app.main (including plain Kanban CRUD tests) on a machine/CI
without the key configured, not just AI requests.
"""

import importlib

from backend.app.ai.client import OpenRouterClient
from backend.app.ai.exceptions import OpenRouterConfigError


def test_importing_ai_router_does_not_construct_openrouter_client(monkeypatch) -> None:
    import backend.app.ai.router as router_module

    def _explode(self, *args, **kwargs):
        raise OpenRouterConfigError("OPENROUTER_API_KEY is not configured")

    monkeypatch.setattr(OpenRouterClient, "__init__", _explode)

    # Before the fix, router.py's module body constructed AiService() /
    # ChatService() (which default-construct an OpenRouterClient()), so this
    # reload would raise even though no AI endpoint was ever called.
    importlib.reload(router_module)
