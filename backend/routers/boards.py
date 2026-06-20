from fastapi import APIRouter, Depends, HTTPException, status

from backend.db import create_board, delete_board, get_board, get_db_path, list_boards_for_user
from backend.db import rename_board, update_board_data
from backend.main_models import (
    BoardCreateRequest,
    BoardData,
    BoardDetail,
    BoardRenameRequest,
    BoardSummary,
)
from backend.routers.auth import require_auth

router = APIRouter(prefix="/api/boards", tags=["boards"])


def _require_board(board_id: str, user_id: str) -> dict:
    board = get_board(board_id, user_id, get_db_path())
    if board is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tablero no encontrado")
    return board


@router.get("")
def get_boards(user: dict = Depends(require_auth)) -> list[BoardSummary]:
    return [BoardSummary(**board) for board in list_boards_for_user(user["id"], get_db_path())]


@router.post("", status_code=status.HTTP_201_CREATED)
def create_board_endpoint(
    request: BoardCreateRequest, user: dict = Depends(require_auth)
) -> BoardDetail:
    board = create_board(user["id"], request.name, path=get_db_path())
    return BoardDetail(**board)


@router.get("/{board_id}")
def get_board_endpoint(board_id: str, user: dict = Depends(require_auth)) -> BoardDetail:
    return BoardDetail(**_require_board(board_id, user["id"]))


@router.put("/{board_id}")
def update_board_endpoint(
    board_id: str, board: BoardData, user: dict = Depends(require_auth)
) -> dict:
    _require_board(board_id, user["id"])
    update_board_data(board_id, user["id"], board.model_dump(), get_db_path())
    return {"status": "ok", "message": "Tablero actualizado"}


@router.patch("/{board_id}")
def rename_board_endpoint(
    board_id: str, request: BoardRenameRequest, user: dict = Depends(require_auth)
) -> dict:
    _require_board(board_id, user["id"])
    rename_board(board_id, user["id"], request.name, get_db_path())
    return {"status": "ok", "message": "Tablero renombrado"}


@router.delete("/{board_id}")
def delete_board_endpoint(board_id: str, user: dict = Depends(require_auth)) -> dict:
    _require_board(board_id, user["id"])
    delete_board(board_id, user["id"], get_db_path())
    return {"status": "ok", "message": "Tablero eliminado"}
