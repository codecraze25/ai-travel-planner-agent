from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.db.models import UserModel
from app.adapters.db.session import get_db_session
from app.api.schemas.email import (
    EmailDraftRequest,
    EmailExportResponse,
    EmailListResponse,
    EmailResponse,
    EmailUpdateRequest,
)
from app.core.auth import get_current_user
from app.services.email_service import EmailService, EmailServiceError

router = APIRouter(prefix="/trips/{trip_id}/emails", tags=["emails"])


def get_email_service(session: Annotated[AsyncSession, Depends(get_db_session)]) -> EmailService:
    return EmailService(session)


@router.get("", response_model=EmailListResponse)
async def list_emails(
    trip_id: uuid.UUID,
    user: Annotated[UserModel, Depends(get_current_user)],
    service: Annotated[EmailService, Depends(get_email_service)],
) -> EmailListResponse:
    items = await service.list_emails(trip_id, user)
    if items is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")
    return EmailListResponse(items=items)


@router.get("/latest", response_model=EmailResponse)
async def get_latest_email(
    trip_id: uuid.UUID,
    user: Annotated[UserModel, Depends(get_current_user)],
    service: Annotated[EmailService, Depends(get_email_service)],
) -> EmailResponse:
    email = await service.get_latest(trip_id, user)
    if email is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Email not found")
    return email


@router.post("/draft", response_model=EmailResponse, status_code=status.HTTP_201_CREATED)
async def draft_email(
    trip_id: uuid.UUID,
    payload: EmailDraftRequest,
    user: Annotated[UserModel, Depends(get_current_user)],
    service: Annotated[EmailService, Depends(get_email_service)],
) -> EmailResponse:
    email = await service.draft(trip_id, user, payload)
    if email is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")
    return email


@router.patch("/{email_id}", response_model=EmailResponse)
async def update_email(
    trip_id: uuid.UUID,
    email_id: uuid.UUID,
    payload: EmailUpdateRequest,
    user: Annotated[UserModel, Depends(get_current_user)],
    service: Annotated[EmailService, Depends(get_email_service)],
) -> EmailResponse:
    try:
        email = await service.update(trip_id, email_id, user, payload)
    except EmailServiceError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    if email is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Email not found")
    return email


@router.post("/{email_id}/approve", response_model=EmailResponse)
async def approve_email(
    trip_id: uuid.UUID,
    email_id: uuid.UUID,
    user: Annotated[UserModel, Depends(get_current_user)],
    service: Annotated[EmailService, Depends(get_email_service)],
) -> EmailResponse:
    try:
        email = await service.approve(trip_id, email_id, user)
    except EmailServiceError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    if email is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Email not found")
    return email


@router.post("/{email_id}/reject", response_model=EmailResponse)
async def reject_email(
    trip_id: uuid.UUID,
    email_id: uuid.UUID,
    user: Annotated[UserModel, Depends(get_current_user)],
    service: Annotated[EmailService, Depends(get_email_service)],
) -> EmailResponse:
    try:
        email = await service.reject(trip_id, email_id, user)
    except EmailServiceError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    if email is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Email not found")
    return email


@router.post("/{email_id}/export", response_model=EmailExportResponse)
async def export_email(
    trip_id: uuid.UUID,
    email_id: uuid.UUID,
    user: Annotated[UserModel, Depends(get_current_user)],
    service: Annotated[EmailService, Depends(get_email_service)],
) -> EmailExportResponse:
    try:
        result = await service.export(trip_id, email_id, user)
    except EmailServiceError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Email not found")
    return result
