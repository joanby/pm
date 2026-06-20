def test_admin_can_create_and_list_users(client, auth_headers) -> None:
    create_response = client.post(
        "/api/users",
        json={
            "username": "nuevo",
            "password": "clave-segura",
            "display_name": "Usuario Nuevo",
            "role": "member",
        },
        headers=auth_headers,
    )
    assert create_response.status_code == 201
    created = create_response.json()
    assert created["username"] == "nuevo"
    assert created["role"] == "member"
    assert "password" not in created
    assert "password_hash" not in created

    list_response = client.get("/api/users", headers=auth_headers)
    usernames = {user["username"] for user in list_response.json()}
    assert {"usuario", "nuevo"} <= usernames


def test_creating_duplicate_username_returns_conflict(client, auth_headers) -> None:
    payload = {
        "username": "duplicado",
        "password": "clave-segura",
        "display_name": "Usuario Duplicado",
        "role": "member",
    }
    first = client.post("/api/users", json=payload, headers=auth_headers)
    assert first.status_code == 201
    second = client.post("/api/users", json=payload, headers=auth_headers)
    assert second.status_code == 409


def test_member_cannot_create_users(client, member_headers) -> None:
    response = client.post(
        "/api/users",
        json={
            "username": "otro",
            "password": "clave-segura",
            "display_name": "Otro",
            "role": "member",
        },
        headers=member_headers,
    )
    assert response.status_code == 403


def test_member_cannot_list_users(client, member_headers) -> None:
    response = client.get("/api/users", headers=member_headers)
    assert response.status_code == 403


def test_get_me_returns_current_user(client, member_headers) -> None:
    response = client.get("/api/users/me", headers=member_headers)
    assert response.status_code == 200
    assert response.json()["username"] == "miembro"


def test_user_can_update_own_display_name(client, member_headers) -> None:
    response = client.patch(
        "/api/users/me", json={"display_name": "Nuevo Nombre"}, headers=member_headers
    )
    assert response.status_code == 200
    assert response.json()["display_name"] == "Nuevo Nombre"


def test_member_cannot_escalate_own_role(client, member_headers) -> None:
    # UserUpdateRequest used by /me intentionally has no role field exposed via this route,
    # so attempting to send one is simply ignored rather than rejected.
    response = client.patch("/api/users/me", json={"role": "admin"}, headers=member_headers)
    assert response.status_code == 200
    me = client.get("/api/users/me", headers=member_headers).json()
    assert me["role"] == "member"


def test_admin_can_change_member_role(client, auth_headers, member_headers) -> None:
    me = client.get("/api/users/me", headers=member_headers).json()
    response = client.patch(
        f"/api/users/{me['id']}", json={"role": "admin"}, headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["role"] == "admin"


def test_admin_cannot_delete_self(client, auth_headers) -> None:
    me = client.get("/api/users/me", headers=auth_headers).json()
    response = client.delete(f"/api/users/{me['id']}", headers=auth_headers)
    assert response.status_code == 400


def test_cannot_demote_last_admin(client, auth_headers) -> None:
    admin_me = client.get("/api/users/me", headers=auth_headers).json()
    response = client.patch(
        f"/api/users/{admin_me['id']}", json={"role": "member"}, headers=auth_headers
    )
    assert response.status_code == 400


def test_can_demote_admin_when_another_admin_remains(client, auth_headers, member_headers) -> None:
    me = client.get("/api/users/me", headers=member_headers).json()
    client.patch(f"/api/users/{me['id']}", json={"role": "admin"}, headers=auth_headers)

    admin_me = client.get("/api/users/me", headers=auth_headers).json()
    response = client.patch(
        f"/api/users/{admin_me['id']}", json={"role": "member"}, headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["role"] == "member"


def test_deleting_unknown_user_returns_404(client, auth_headers) -> None:
    response = client.delete("/api/users/does-not-exist", headers=auth_headers)
    assert response.status_code == 404


def test_admin_can_delete_member(client, auth_headers, member_headers) -> None:
    me = client.get("/api/users/me", headers=member_headers).json()
    response = client.delete(f"/api/users/{me['id']}", headers=auth_headers)
    assert response.status_code == 200

    follow_up = client.get("/api/users/me", headers=member_headers)
    assert follow_up.status_code == 401
