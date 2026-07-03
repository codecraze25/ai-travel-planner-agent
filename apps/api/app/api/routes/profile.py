from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.db.models import UserModel
from app.adapters.db.session import get_db_session
from app.api.schemas.profile import ProfileResponse, ProfileUpsertRequest
from app.core.auth import get_current_user
from app.domain.profile import ProfileValidationError
from app.services.profile_service import ProfileService

router = APIRouter(prefix="/profile", tags=["profile"])


def get_profile_service(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> ProfileService:
    return ProfileService(session)


@router.get("", response_model=ProfileResponse)
async def get_profile(
    user: Annotated[UserModel, Depends(get_current_user)],
    service: Annotated[ProfileService, Depends(get_profile_service)],
) -> ProfileResponse:
    profile = await service.get_profile(user)
    if profile is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
    return profile


@router.put("", response_model=ProfileResponse)
async def upsert_profile(
    payload: ProfileUpsertRequest,
    user: Annotated[UserModel, Depends(get_current_user)],
    service: Annotated[ProfileService, Depends(get_profile_service)],
) -> ProfileResponse:
    try:
        return await service.upsert_profile(user, payload)
    except (ProfileValidationError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc
