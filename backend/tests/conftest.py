import pytest

from backend.app.db.init_db import init_database
from backend.app.kanban.seed import seed_demo_data


@pytest.fixture
def seeded_db(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"
    monkeypatch.setenv("PM_DATABASE_PATH", str(db_path))
    init_database(db_path)
    seed_demo_data()
    return db_path


@pytest.fixture
def client(seeded_db):
    from fastapi.testclient import TestClient

    from backend.app.main import app

    with TestClient(app) as test_client:
        yield test_client


AUTH_HEADERS = {"X-MVP-Username": "user"}
