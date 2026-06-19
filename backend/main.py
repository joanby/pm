from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend.db import get_db_path, init_db
from backend.routers import ai, auth, board, health

STATIC_DIR = Path(__file__).resolve().parent / "static"
FRONTEND_DIR = STATIC_DIR / "frontend"
INDEX_FILE = STATIC_DIR / "index.html"


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db(get_db_path())
    yield


app = FastAPI(title="Project Management MVP Backend", lifespan=lifespan)

app.include_router(health.router)
app.include_router(board.router)
app.include_router(auth.router)
app.include_router(ai.router)

# Mount Next.js static files if they exist
if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
else:
    # Fallback to basic HTML if frontend build doesn't exist
    @app.get("/{full_path:path}")
    def fallback(full_path: str) -> FileResponse:
        return FileResponse(INDEX_FILE)
