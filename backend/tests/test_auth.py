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


def test_register_creates_member_and_auto_logs_in(client) -> None:
    response = client.post(
        "/api/auth/register",
        json={"username": "recien_llegado", "password": "clave-segura", "display_name": "Recién Llegado"},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["username"] == "recien_llegado"
    assert body["role"] == "member"
    assert body["token"]

    boards_response = client.get(
        "/api/boards", headers={"Authorization": f"Bearer {body['token']}"}
    )
    assert boards_response.status_code == 200


def test_register_rejects_duplicate_username(client) -> None:
    payload = {"username": "duplicado_reg", "password": "clave-segura", "display_name": "Uno"}
    first = client.post("/api/auth/register", json=payload)
    assert first.status_code == 201
    second = client.post("/api/auth/register", json=payload)
    assert second.status_code == 409


def test_registered_user_cannot_manage_users(client) -> None:
    register_response = client.post(
        "/api/auth/register",
        json={"username": "miembro_reg", "password": "clave-segura", "display_name": "Miembro"},
    )
    token = register_response.json()["token"]
    response = client.get("/api/users", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403
