import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from backend.db import DB_PATH_ENV

TEST_DB_PATH = Path(__file__).resolve().parent.parent / "test-kanban.db"
ROOT_ENV_PATH = Path(__file__).resolve().parent.parent.parent / ".env"

if ROOT_ENV_PATH.exists():
    for line in ROOT_ENV_PATH.read_text().splitlines():
        key, separator, value = line.partition("=")
        if separator and key == "OPENROUTER_API_KEY":
            os.environ.setdefault(key, value.strip())


@pytest.fixture(autouse=True)
def _isolated_db():
    os.environ[DB_PATH_ENV] = str(TEST_DB_PATH)
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()
    yield
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()
    os.environ.pop(DB_PATH_ENV, None)


@pytest.fixture
def client():
    from backend.main import app

    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def auth_headers(client) -> dict:
    response = client.post(
        "/api/auth/login", json={"username": "usuario", "password": "contraseña"}
    )
    token = response.json()["token"]
    return {"Authorization": f"Bearer {token}"}
