from fastapi import FastAPI, HTTPException, status
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from pathlib import Path
import secrets

app = FastAPI(title="Project Management MVP Backend")

STATIC_DIR = Path(__file__).resolve().parent / "static"
FRONTEND_DIR = STATIC_DIR / "frontend"
INDEX_FILE = STATIC_DIR / "index.html"

# Simulated users and sessions
VALID_CREDENTIALS = {"usuario": "contraseña"}
sessions: dict[str, str] = {}

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    username: str
    token: str

@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}

@app.get("/api/ping")
def ping() -> dict:
    return {"message": "pong"}

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


