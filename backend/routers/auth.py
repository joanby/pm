import secrets
from typing import Annotated

from fastapi import APIRouter, Header, HTTPException, status
from pydantic import BaseModel

from backend.db import find_user, get_db_path

router = APIRouter(prefix="/api/auth", tags=["auth"])

# Simulated sessions: token -> username
sessions: dict[str, str] = {}


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    username: str
    token: str


def require_auth(authorization: Annotated[str | None, Header()] = None) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No autenticado")
    username = sessions.get(authorization.removeprefix("Bearer "))
    if username is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Sesión inválida")
    return username


@router.post("/login")
def login(request: LoginRequest) -> LoginResponse:
    user = find_user(request.username, get_db_path())
    if user is None or user["password_hash"] != request.password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales inválidas")

    token = secrets.token_urlsafe(32)
    sessions[token] = user["username"]

    return LoginResponse(username=user["username"], token=token)


@router.post("/logout")
def logout(authorization: Annotated[str | None, Header()] = None) -> dict:
    if authorization and authorization.startswith("Bearer "):
        sessions.pop(authorization.removeprefix("Bearer "), None)
    return {"message": "Sesión cerrada"}
