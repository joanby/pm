from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, status
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from pathlib import Path
import secrets
import os

from backend.ai import AiChatRequest, AiChatResponse, request_structured_ai_response
from backend.db import init_db, load_board, save_board
from backend.main_models import BoardData
from backend.openrouter import OPENROUTER_MODEL, OpenRouterError, call_openrouter

STATIC_DIR = Path(__file__).resolve().parent / "static"
FRONTEND_DIR = STATIC_DIR / "frontend"
INDEX_FILE = STATIC_DIR / "index.html"


def get_db_path():
    return os.environ.get("KANBAN_DB_PATH")


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db(get_db_path())
    yield


app = FastAPI(title="Project Management MVP Backend", lifespan=lifespan)

# Simulated users and sessions
VALID_CREDENTIALS = {"usuario": "contraseña"}
sessions = {}


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    username: str
    token: str


class AiValidationResponse(BaseModel):
    model: str
    answer: str


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/api/ping")
def ping() -> dict:
    return {"message": "pong"}


@app.get("/api/board")
def get_board() -> BoardData:
    board = load_board(get_db_path())
    return board


@app.post("/api/board")
def update_board(board: BoardData) -> dict:
    save_board(board.model_dump(), get_db_path())
    return {"status": "ok", "message": "Board updated"}


@app.post("/api/auth/login")
def login(request: LoginRequest) -> LoginResponse:
    if request.username not in VALID_CREDENTIALS or VALID_CREDENTIALS[request.username] != request.password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales inválidas")

    token = secrets.token_urlsafe(32)
    sessions[token] = request.username

    return LoginResponse(username=request.username, token=token)


@app.post("/api/auth/logout")
def logout() -> dict:
    return {"message": "Sesión cerrada"}


@app.get("/api/ai/validate")
def validate_ai() -> AiValidationResponse:
    try:
        answer = call_openrouter("What is 2+2? Reply with only the number.")
    except OpenRouterError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc
    return AiValidationResponse(model=OPENROUTER_MODEL, answer=answer)


@app.post("/api/ai/chat")
def chat_with_ai(request: AiChatRequest) -> AiChatResponse:
    try:
        response = request_structured_ai_response(request)
    except OpenRouterError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc

    if response.boardUpdate is not None:
        save_board(response.boardUpdate.model_dump(), get_db_path())
    return response

# Mount Next.js static files if they exist
if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
else:
    # Fallback to basic HTML if frontend build doesn't exist
    @app.get("/{full_path:path}")
    def fallback(full_path: str) -> FileResponse:
        return FileResponse(INDEX_FILE)
