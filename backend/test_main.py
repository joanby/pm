from pathlib import Path
import os

from .db import DB_PATH_ENV

TEST_DB_PATH = Path(__file__).resolve().parent / "test-kanban.db"

os.environ[DB_PATH_ENV] = str(TEST_DB_PATH)

from fastapi.testclient import TestClient
from .main import app


def setup_module() -> None:
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()
    os.environ[DB_PATH_ENV] = str(TEST_DB_PATH)


def teardown_module() -> None:
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()
    os.environ.pop(DB_PATH_ENV, None)


def test_health_endpoint() -> None:
    with TestClient(app) as client:
        response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_board_endpoints_initialize_and_read() -> None:
    with TestClient(app) as client:
        response = client.get("/api/board")
        assert response.status_code == 200
        body = response.json()
    assert "columns" in body
    assert "cards" in body
    assert len(body["columns"]) == 5


def test_board_update_endpoint() -> None:
    with TestClient(app) as client:
        board_response = client.get("/api/board")
        board = board_response.json()
        board["columns"][0]["title"] = "Backlog Updated"
        update_response = client.post("/api/board", json=board)
        assert update_response.status_code == 200
        assert update_response.json()["status"] == "ok"

        read_back = client.get("/api/board").json()
    assert read_back["columns"][0]["title"] == "Backlog Updated"
