import re

import pytest
from fastapi.testclient import TestClient

from backend.app.main import INDEX_FILE, app

client = TestClient(app)


@pytest.fixture
def requires_frontend_build() -> None:
    if not INDEX_FILE.exists():
        pytest.skip("Frontend build not found at backend/static/frontend")


def test_spa_fallback_returns_index(requires_frontend_build: None) -> None:
    response = client.get("/some/deep/client/route")
    assert response.status_code == 200
    assert "Kanban Studio" in response.text


def test_favicon_is_served(requires_frontend_build: None) -> None:
    response = client.get("/favicon.ico")
    assert response.status_code == 200


def test_next_static_assets_from_index_are_served(requires_frontend_build: None) -> None:
    index_html = INDEX_FILE.read_text(encoding="utf-8")
    asset_paths = set(re.findall(r'(?:src|href)="(/_next/[^"?]+)', index_html))
    assert asset_paths, "Expected Next.js static asset references in index.html"

    for path in sorted(asset_paths):
        response = client.get(path)
        assert response.status_code == 200, f"Failed to load asset: {path}"


def test_unknown_api_route_is_not_served_as_static() -> None:
    response = client.get("/api/unknown-endpoint")
    assert response.status_code == 404
