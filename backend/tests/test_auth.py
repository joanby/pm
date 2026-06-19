def test_login_success(client) -> None:
    response = client.post(
        "/api/auth/login", json={"username": "usuario", "password": "contraseña"}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["username"] == "usuario"
    assert body["token"]


def test_login_invalid_credentials(client) -> None:
    response = client.post(
        "/api/auth/login", json={"username": "usuario", "password": "wrong"}
    )
    assert response.status_code == 401


def test_board_requires_auth(client) -> None:
    response = client.get("/api/board")
    assert response.status_code == 401


def test_logout_invalidates_session(client, auth_headers) -> None:
    response = client.post("/api/auth/logout", headers=auth_headers)
    assert response.status_code == 200

    follow_up = client.get("/api/board", headers=auth_headers)
    assert follow_up.status_code == 401
