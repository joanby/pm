from fastapi.testclient import TestClient

from backend.app.main import app


def test_home_page_serves_kanban_frontend_html() -> None:
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code in {200, 503}
    if response.status_code == 503:
        # Local unit/integration runs may execute without a built frontend artifact.
        assert response.json() == {"detail": "Frontend build not found"}
    else:
        assert "Kanban Studio" in response.text
