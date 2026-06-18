from fastapi import FastAPI, HTTPException, status
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from pathlib import Path
import secrets
import os

from backend.db import init_db, load_board, save_board

app = FastAPI(title="Project Management MVP Backend")

STATIC_DIR = Path(__file__).resolve().parent / "static"
FRONTEND_DIR = STATIC_DIR / "frontend"
INDEX_FILE = STATIC_DIR / "index.html"

def get_db_path():
    return os.environ.get("KANBAN_DB_PATH")

# Simulated users and sessions
VALID_CREDENTIALS = {"usuario": "contraseña"}
sessions = {}

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    username: str
    token: str

class BoardData(BaseModel):
    columns: list
    cards: dict

@app.on_event("startup")
def startup_event() -> None:
    init_db(get_db_path())

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
    save_board(board.dict(), get_db_path())
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

# Mount Next.js static files if they exist
if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
else:
    # Fallback to basic HTML if frontend build doesn't exist
    @app.get("/{full_path:path}")
    def fallback(full_path: str) -> FileResponse:
        return FileResponse(INDEX_FILE)


