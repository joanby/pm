from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from backend.app.ai.chat_service import ChatService
from backend.app.ai.exceptions import OpenRouterConfigError, OpenRouterError, OpenRouterResponseError
from backend.app.ai.models import AiPingResponse, ChatHistoryResponse, ChatRequest, ChatResponse
from backend.app.ai.service import AiService
from backend.app.auth import get_current_username
from backend.app.kanban.repository import KanbanNotFoundError

router = APIRouter(prefix="/api/ai", tags=["ai"])


def _handle_openrouter_error(error: Exception) -> None:
    if isinstance(error, OpenRouterConfigError):
        raise HTTPException(status_code=503, detail=str(error)) from error
    if isinstance(error, OpenRouterResponseError):
        raise HTTPException(status_code=502, detail=str(error)) from error
    if isinstance(error, OpenRouterError):
        message = str(error)
        status_code = 504 if "timed out" in message.lower() else 502
        raise HTTPException(status_code=status_code, detail=message) from error
    if isinstance(error, KanbanNotFoundError):
        raise HTTPException(status_code=404, detail=str(error)) from error
    raise error


@router.get("/ping")
def ping_ai(username: str = Depends(get_current_username)) -> AiPingResponse:
    del username
    try:
        return AiService().ping()
    except Exception as error:
        _handle_openrouter_error(error)


@router.post("/chat")
def chat_with_ai(
    payload: ChatRequest,
    username: str = Depends(get_current_username),
) -> ChatResponse:
    try:
        return ChatService().chat(username, payload.message)
    except Exception as error:
        _handle_openrouter_error(error)


@router.get("/history")
def get_chat_history(username: str = Depends(get_current_username)) -> ChatHistoryResponse:
    try:
        return ChatService().get_history(username)
    except Exception as error:
        _handle_openrouter_error(error)
