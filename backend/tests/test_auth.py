def test_login_success(client) -> None:
    response = client.post(
        "/api/auth/login", json={"username": "usuario", "password": "contraseña"}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["username"] == "usuario"
    assert body["role"] == "admin"
    assert body["id"]
    assert body["token"]


def test_login_invalid_credentials(client) -> None:
    response = client.post(
        "/api/auth/login", json={"username": "usuario", "password": "wrong"}
    )
    assert response.status_code == 401


def test_login_unknown_user(client) -> None:
    response = client.post(
        "/api/auth/login", json={"username": "no-existe", "password": "lo-que-sea"}
    )
    assert response.status_code == 401


def test_boards_require_auth(client) -> None:
    response = client.get("/api/boards")
    assert response.status_code == 401


def test_logout_invalidates_session(client, auth_headers) -> None:
    response = client.post("/api/auth/logout", headers=auth_headers)
    assert response.status_code == 200

    follow_up = client.get("/api/boards", headers=auth_headers)
    assert follow_up.status_code == 401
