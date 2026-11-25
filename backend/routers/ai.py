from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from backend.ai import AiChatRequest, AiChatResponse, request_structured_ai_response
from backend.db import get_db_path, save_board
from backend.openrouter import OPENROUTER_MODEL, OpenRouterError, call_openrouter
from backend.routers.auth import require_auth

router = APIRouter(prefix="/api/ai", tags=["ai"])


class AiValidationResponse(BaseModel):
    model: str
    answer: str


@router.get("/validate")
def validate_ai(_: str = Depends(require_auth)) -> AiValidationResponse:
    try:
        answer = call_openrouter("What is 2+2? Reply with only the number.")
    except OpenRouterError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc
    return AiValidationResponse(model=OPENROUTER_MODEL, answer=answer)


@router.post("/chat")
def chat_with_ai(request: AiChatRequest, _: str = Depends(require_auth)) -> AiChatResponse:
    try:
        response = request_structured_ai_response(request)
    except OpenRouterError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc

    if response.boardUpdate is not None:
        save_board(response.boardUpdate.model_dump(), get_db_path())
    return response
