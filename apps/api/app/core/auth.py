from __future__ import annotations

from dataclasses import dataclass
from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.db.models import UserModel
from app.adapters.db.repositories import UserRepository
from app.adapters.db.session import get_db_session
from app.core.config import get_settings


@dataclass(frozen=True)
class AuthUser:
    external_id: str
    email: str


async def get_current_auth_user(request: Request) -> AuthUser:
    settings = get_settings()

    if settings.auth_disabled:
        return AuthUser(external_id=settings.dev_user_id, email=settings.dev_user_email)

    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")

    token = auth_header.removeprefix("Bearer ").strip()
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")

    if not settings.clerk_secret_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Auth is enabled but CLERK_SECRET_KEY is not configured",
        )

    from app.core.clerk_auth import verify_clerk_token

    try:
        claims = verify_clerk_token(token, settings.clerk_secret_key)
    except Exception as exc:  # noqa: BLE001 — map to 401 for clients
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        ) from exc

    external_id = str(claims.get("sub", ""))
    email = str(claims.get("email") or claims.get("primary_email") or "")
    if not external_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token claims")

    return AuthUser(external_id=external_id, email=email or f"{external_id}@users.clerk")


async def get_current_user(
    auth_user: Annotated[AuthUser, Depends(get_current_auth_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> UserModel:
    repo = UserRepository(session)
    return await repo.get_or_create(auth_user.external_id, auth_user.email)
