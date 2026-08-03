from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse

from backend.app.db.init_db import init_database
from backend.app.kanban.router import router as kanban_router
from backend.app.kanban.seed import seed_demo_data

ROOT_DIR = Path(__file__).resolve().parent.parent
FRONTEND_STATIC_DIR = ROOT_DIR / "static" / "frontend"
INDEX_FILE = FRONTEND_STATIC_DIR / "index.html"


def serve_index() -> FileResponse:
    return FileResponse(INDEX_FILE, headers={"Cache-Control": "no-store"})


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_database()
    seed_demo_data()
    yield


app = FastAPI(title="Project Management MVP API", lifespan=lifespan)
app.include_router(kanban_router)


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/")
def home() -> FileResponse:
    if not INDEX_FILE.exists():
        raise HTTPException(status_code=503, detail="Frontend build not found")
    return serve_index()


@app.get("/{asset_path:path}")
def frontend_assets(asset_path: str) -> FileResponse:
    # Keep API routes handled by dedicated endpoints.
    if asset_path.startswith("api/"):
        raise HTTPException(status_code=404, detail="Not found")

    requested_file = (FRONTEND_STATIC_DIR / asset_path).resolve()
    if FRONTEND_STATIC_DIR.resolve() not in requested_file.parents and requested_file != FRONTEND_STATIC_DIR.resolve():
        raise HTTPException(status_code=404, detail="Not found")

    if requested_file.is_file():
        return FileResponse(requested_file)

    if INDEX_FILE.exists():
        return serve_index()

    raise HTTPException(status_code=404, detail="Not found")
