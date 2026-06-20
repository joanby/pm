from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from backend.ai import AiChatRequest, AiChatResponse, request_structured_ai_response
from backend.db import get_board, get_db_path, update_board_data
from backend.openrouter import OPENROUTER_MODEL, OpenRouterError, call_openrouter
from backend.routers.auth import require_auth

router = APIRouter(prefix="/api/ai", tags=["ai"])


class AiValidationResponse(BaseModel):
    model: str
    answer: str


@router.get("/validate")
def validate_ai(_: dict = Depends(require_auth)) -> AiValidationResponse:
    try:
        answer = call_openrouter("What is 2+2? Reply with only the number.")
    except OpenRouterError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc
    return AiValidationResponse(model=OPENROUTER_MODEL, answer=answer)


@router.post("/chat")
def chat_with_ai(request: AiChatRequest, user: dict = Depends(require_auth)) -> AiChatResponse:
    if get_board(request.board_id, user["id"], get_db_path()) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tablero no encontrado")

    try:
        response = request_structured_ai_response(request)
    except OpenRouterError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc

    if response.boardUpdate is not None:
        update_board_data(request.board_id, user["id"], response.boardUpdate.model_dump(), get_db_path())
    return response
