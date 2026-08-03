from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import ValidationError

from backend.app.auth import get_current_username
from backend.app.kanban.models import BoardData, Card, CardCreate, CardMove, CardUpdate, ColumnUpdate
from backend.app.kanban.repository import KanbanNotFoundError, KanbanRepositoryError
from backend.app.kanban.service import KanbanService

router = APIRouter(prefix="/api", tags=["kanban"])
service = KanbanService()


def _handle_service_error(error: Exception) -> None:
    if isinstance(error, KanbanNotFoundError):
        raise HTTPException(status_code=404, detail=str(error)) from error
    if isinstance(error, KanbanRepositoryError):
        raise HTTPException(status_code=400, detail=str(error)) from error
    if isinstance(error, ValidationError):
        raise HTTPException(status_code=422, detail=error.errors()) from error
    raise error


@router.get("/board")
def get_board(username: str = Depends(get_current_username)) -> BoardData:
    try:
        return service.get_board(username)
    except Exception as error:
        _handle_service_error(error)


@router.put("/board")
def replace_board(
    payload: BoardData,
    username: str = Depends(get_current_username),
) -> BoardData:
    try:
        return service.replace_board(username, payload)
    except Exception as error:
        _handle_service_error(error)


@router.patch("/columns/{column_id}")
def rename_column(
    column_id: str,
    payload: ColumnUpdate,
    username: str = Depends(get_current_username),
) -> dict[str, str]:
    try:
        column = service.rename_column(username, column_id, payload)
        return {"id": column.id, "title": column.title}
    except Exception as error:
        _handle_service_error(error)


@router.post("/columns/{column_id}/cards", status_code=201)
def create_card(
    column_id: str,
    payload: CardCreate,
    username: str = Depends(get_current_username),
) -> Card:
    try:
        return service.create_card(username, column_id, payload)
    except Exception as error:
        _handle_service_error(error)


@router.patch("/cards/{card_id}")
def update_card(
    card_id: str,
    payload: CardUpdate,
    username: str = Depends(get_current_username),
) -> Card:
    try:
        return service.update_card(username, card_id, payload)
    except Exception as error:
        _handle_service_error(error)


@router.delete("/cards/{card_id}", status_code=204, response_class=Response)
def delete_card(
    card_id: str,
    username: str = Depends(get_current_username),
) -> Response:
    try:
        service.delete_card(username, card_id)
    except Exception as error:
        _handle_service_error(error)
    return Response(status_code=204)


@router.put("/cards/{card_id}/move")
def move_card(
    card_id: str,
    payload: CardMove,
    username: str = Depends(get_current_username),
) -> BoardData:
    try:
        return service.move_card(username, card_id, payload)
    except Exception as error:
        _handle_service_error(error)
