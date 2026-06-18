from pathlib import Path
import os

from .db import DB_PATH_ENV

TEST_DB_PATH = Path(__file__).resolve().parent / "test-kanban.db"
ROOT_ENV_PATH = Path(__file__).resolve().parent.parent / ".env"

os.environ[DB_PATH_ENV] = str(TEST_DB_PATH)

if ROOT_ENV_PATH.exists():
    for line in ROOT_ENV_PATH.read_text().splitlines():
        key, separator, value = line.partition("=")
        if separator and key == "OPENROUTER_API_KEY":
            os.environ.setdefault(key, value.strip())

from fastapi.testclient import TestClient
from .ai import parse_ai_response
from .main import app
from .openrouter import OpenRouterError


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


def test_ai_validation_reaches_openrouter() -> None:
    with TestClient(app) as client:
        response = client.get("/api/ai/validate")
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["model"] == "openai/gpt-oss-120b:free"
    assert "4" in body["answer"]


def test_ai_chat_returns_structured_response_from_openrouter() -> None:
    with TestClient(app) as client:
        board = client.get("/api/board").json()
        response = client.post(
            "/api/ai/chat",
            json={
                "message": "Reply with message exactly 'ok'. Do not change the board.",
                "board": board,
                "history": [],
            },
        )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["message"].lower() == "ok"
    assert body["boardUpdate"] is None


def test_parse_ai_response_rejects_invalid_json() -> None:
    try:
        parse_ai_response("not json")
    except OpenRouterError as exc:
        assert "valid JSON" in str(exc)
    else:
        raise AssertionError("Expected invalid JSON to be rejected")


def test_parse_ai_response_rejects_missing_message() -> None:
    try:
        parse_ai_response('{"boardUpdate": null}')
    except OpenRouterError as exc:
        assert "expected schema" in str(exc)
    else:
        raise AssertionError("Expected invalid schema to be rejected")


def test_parse_ai_response_rejects_invalid_board_update() -> None:
    try:
        parse_ai_response(
            """
            {
              "message": "updated",
              "boardUpdate": {
                "columns": [
                  {"id": "col-1", "title": "Todo", "cardIds": ["missing-card"]}
                ],
                "cards": {}
              }
            }
            """
        )
    except OpenRouterError as exc:
        assert "expected schema" in str(exc)
    else:
        raise AssertionError("Expected invalid boardUpdate to be rejected")
