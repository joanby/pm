import sqlite3

from fastapi import APIRouter, Depends, HTTPException, status

from backend.db import (
    count_admins,
    create_user,
    delete_user,
    find_user_by_id,
    get_db_path,
    list_users,
    update_user,
)
from backend.main_models import UserCreateRequest, UserPublic, UserUpdateRequest
from backend.routers.auth import require_admin, require_auth

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("")
def get_users(_: dict = Depends(require_admin)) -> list[UserPublic]:
    return [UserPublic(**user) for user in list_users(get_db_path())]


@router.post("", status_code=status.HTTP_201_CREATED)
def register_user(request: UserCreateRequest, _: dict = Depends(require_admin)) -> UserPublic:
    try:
        user = create_user(
            request.username,
            request.password,
            request.display_name,
            request.role,
            get_db_path(),
        )
    except sqlite3.IntegrityError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="El nombre de usuario ya existe"
        ) from exc
    return UserPublic(**user)


@router.get("/me")
def get_me(user: dict = Depends(require_auth)) -> UserPublic:
    return UserPublic(**user)


@router.patch("/me")
def update_me(request: UserUpdateRequest, user: dict = Depends(require_auth)) -> UserPublic:
    updated = update_user(
        user["id"],
        display_name=request.display_name,
        password=request.password,
        path=get_db_path(),
    )
    return UserPublic(**updated)


@router.patch("/{user_id}")
def update_user_by_admin(
    user_id: str, request: UserUpdateRequest, _: dict = Depends(require_admin)
) -> UserPublic:
    target = find_user_by_id(user_id, get_db_path())
    if target is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    if (
        request.role == "member"
        and target["role"] == "admin"
        and count_admins(get_db_path()) <= 1
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Debe quedar al menos un administrador"
        )

    updated = update_user(
        user_id,
        display_name=request.display_name,
        role=request.role,
        password=request.password,
        path=get_db_path(),
    )
    return UserPublic(**updated)


@router.delete("/{user_id}")
def remove_user(user_id: str, admin: dict = Depends(require_admin)) -> dict:
    if user_id == admin["id"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No puedes eliminar tu propio usuario"
        )
    if find_user_by_id(user_id, get_db_path()) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    delete_user(user_id, get_db_path())
    return {"status": "ok", "message": "Usuario eliminado"}
