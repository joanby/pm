from fastapi import APIRouter, Depends

from backend.db import get_db_path, load_board, save_board
from backend.main_models import BoardData
from backend.routers.auth import require_auth

router = APIRouter(prefix="/api/board", tags=["board"])


@router.get("")
def get_board(_: str = Depends(require_auth)) -> BoardData:
    return load_board(get_db_path())


@router.post("")
def update_board(board: BoardData, _: str = Depends(require_auth)) -> dict:
    save_board(board.model_dump(), get_db_path())
    return {"status": "ok", "message": "Board updated"}
