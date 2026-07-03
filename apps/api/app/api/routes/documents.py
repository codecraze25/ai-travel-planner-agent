from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.db.models import UserModel
from app.adapters.db.session import get_db_session
from app.api.schemas.documents import (
    DocumentListResponse,
    DocumentResponse,
    DocumentSearchRequest,
    DocumentSearchResponse,
)
from app.core.auth import get_current_user
from app.services.document_service import DocumentService

router = APIRouter(prefix="/trips/{trip_id}/documents", tags=["documents"])


def get_document_service(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> DocumentService:
    return DocumentService(session)


@router.get("", response_model=DocumentListResponse)
async def list_documents(
    trip_id: uuid.UUID,
    user: Annotated[UserModel, Depends(get_current_user)],
    service: Annotated[DocumentService, Depends(get_document_service)],
) -> DocumentListResponse:
    items = await service.list_documents(trip_id, user)
    if items is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")
    return DocumentListResponse(items=items)


@router.post("", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    trip_id: uuid.UUID,
    user: Annotated[UserModel, Depends(get_current_user)],
    service: Annotated[DocumentService, Depends(get_document_service)],
    file: UploadFile = File(...),
) -> DocumentResponse:
    data = await file.read()
    try:
        result = await service.upload(
            trip_id,
            user,
            file.filename or "upload.pdf",
            file.content_type,
            data,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")
    return result


@router.post("/search", response_model=DocumentSearchResponse)
async def search_documents(
    trip_id: uuid.UUID,
    payload: DocumentSearchRequest,
    user: Annotated[UserModel, Depends(get_current_user)],
    service: Annotated[DocumentService, Depends(get_document_service)],
) -> DocumentSearchResponse:
    result = await service.search(trip_id, user, payload.query, payload.limit)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")
    return result


@router.post("/{document_id}/parse", response_model=DocumentResponse)
async def parse_document(
    trip_id: uuid.UUID,
    document_id: uuid.UUID,
    user: Annotated[UserModel, Depends(get_current_user)],
    service: Annotated[DocumentService, Depends(get_document_service)],
) -> DocumentResponse:
    result = await service.parse(trip_id, document_id, user)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return result


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    trip_id: uuid.UUID,
    document_id: uuid.UUID,
    user: Annotated[UserModel, Depends(get_current_user)],
    service: Annotated[DocumentService, Depends(get_document_service)],
) -> None:
    ok = await service.delete(trip_id, document_id, user)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
