import secrets
from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel

from backend.db import find_user, find_user_by_id, get_db_path, verify_password

router = APIRouter(prefix="/api/auth", tags=["auth"])

# Simulated sessions: token -> user_id
sessions: dict[str, str] = {}


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    id: str
    username: str
    display_name: str | None
    role: str
    token: str


def require_auth(authorization: Annotated[str | None, Header()] = None) -> dict:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No autenticado")
    user_id = sessions.get(authorization.removeprefix("Bearer "))
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Sesión inválida")
    user = find_user_by_id(user_id, get_db_path())
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Sesión inválida")
    return user


def require_admin(user: dict = Depends(require_auth)) -> dict:
    if user["role"] != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Requiere rol de administrador")
    return user


@router.post("/login")
def login(request: LoginRequest) -> LoginResponse:
    user = find_user(request.username, get_db_path())
    if user is None or not verify_password(request.password, user["password_hash"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales inválidas")

    token = secrets.token_urlsafe(32)
    sessions[token] = user["id"]

    return LoginResponse(
        id=user["id"],
        username=user["username"],
        display_name=user["display_name"],
        role=user["role"],
        token=token,
    )


@router.post("/logout")
def logout(authorization: Annotated[str | None, Header()] = None) -> dict:
    if authorization and authorization.startswith("Bearer "):
        sessions.pop(authorization.removeprefix("Bearer "), None)
    return {"message": "Sesión cerrada"}
