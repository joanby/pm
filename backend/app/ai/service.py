from __future__ import annotations

from backend.app.ai.client import OpenRouterClient
from backend.app.ai.config import CONNECTIVITY_PROMPT, get_openrouter_model
from backend.app.ai.models import AiPingResponse


class AiService:
    def __init__(self, client: OpenRouterClient | None = None) -> None:
        self.client = client or OpenRouterClient()

    def ping(self) -> AiPingResponse:
        response = self.client.ping()
        return AiPingResponse(
            model=self.client.model,
            prompt=CONNECTIVITY_PROMPT,
            response=response,
        )
