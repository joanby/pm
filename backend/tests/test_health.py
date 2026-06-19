def test_health_endpoint(client) -> None:
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_ping_endpoint(client) -> None:
    response = client.get("/api/ping")
    assert response.status_code == 200
    assert response.json() == {"message": "pong"}
