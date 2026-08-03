from __future__ import annotations

from fastapi import Header, HTTPException

MVP_USERNAME_HEADER = "X-MVP-Username"


def get_current_username(
    x_mvp_username: str | None = Header(default=None, alias=MVP_USERNAME_HEADER),
) -> str:
    if not x_mvp_username:
        raise HTTPException(status_code=401, detail="Missing X-MVP-Username header")
    return x_mvp_username.strip()
