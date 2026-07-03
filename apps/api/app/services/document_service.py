from __future__ import annotations

import uuid
from dataclasses import asdict

from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.db.models import DocumentChunkModel, DocumentModel, UserModel
from app.adapters.db.repositories import DocumentRepository, TripRepository
from app.adapters.embeddings import cosine_similarity, embed_text
from app.adapters.pdf.parser import extract_text_from_pdf
from app.adapters.storage import s3
from app.api.schemas.documents import (
    DocumentCitation,
    DocumentResponse,
    DocumentSearchResponse,
    ExtractedFieldsResponse,
)
from app.domain.documents import (
    DocumentStatus,
    chunk_text,
    contains_injection_attempt,
    extract_structured_fields,
    sanitize_document_text,
    validate_upload,
)


class DocumentService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._docs = DocumentRepository(session)
        self._trips = TripRepository(session)

    async def upload(
        self,
        trip_id: uuid.UUID,
        user: UserModel,
        filename: str,
        content_type: str | None,
        data: bytes,
    ) -> DocumentResponse | None:
        trip = await self._trips.get_for_user(trip_id, user.id)
        if trip is None:
            return None

        validate_upload(filename, content_type, len(data))
        document_id = uuid.uuid4()
        s3_key = f"trips/{trip_id}/documents/{document_id}/{filename}"
        s3.put_object(s3_key, data, content_type or "application/pdf")

        document = DocumentModel(
            id=document_id,
            trip_id=trip_id,
            user_id=user.id,
            filename=filename,
            s3_key=s3_key,
            mime_type=content_type or "application/pdf",
            size_bytes=len(data),
            status=DocumentStatus.UPLOADED,
        )
        await self._docs.create(document)
        await self._session.commit()
        return _to_response(document)

    async def list_documents(
        self, trip_id: uuid.UUID, user: UserModel
    ) -> list[DocumentResponse] | None:
        trip = await self._trips.get_for_user(trip_id, user.id)
        if trip is None:
            return None
        docs = await self._docs.list_for_trip(trip_id)
        return [_to_response(d) for d in docs]

    async def parse(
        self, trip_id: uuid.UUID, document_id: uuid.UUID, user: UserModel
    ) -> DocumentResponse | None:
        trip = await self._trips.get_for_user(trip_id, user.id)
        if trip is None:
            return None
        document = await self._docs.get_for_trip(document_id, trip_id)
        if document is None:
            return None

        document.status = DocumentStatus.PARSING
        document.error_message = None
        await self._session.flush()

        try:
            data = s3.get_object_bytes(document.s3_key)
            raw_text = extract_text_from_pdf(data)
            injection = contains_injection_attempt(raw_text)
            document.injection_flagged = injection
            safe_text = sanitize_document_text(raw_text)
            fields = extract_structured_fields(safe_text)
            document.extracted_fields = asdict(fields)

            chunks = chunk_text(safe_text)
            chunk_models = [
                DocumentChunkModel(
                    chunk_index=idx,
                    content=chunk,
                    embedding=embed_text(chunk),
                )
                for idx, chunk in enumerate(chunks)
            ]
            await self._docs.replace_chunks(document.id, chunk_models)
            document.status = DocumentStatus.READY
        except Exception as exc:  # noqa: BLE001 — surface parse failures to user
            document.status = DocumentStatus.FAILED
            document.error_message = str(exc)

        await self._session.commit()
        refreshed = await self._docs.get_for_trip(document_id, trip_id)
        assert refreshed is not None
        return _to_response(refreshed)

    async def delete(self, trip_id: uuid.UUID, document_id: uuid.UUID, user: UserModel) -> bool:
        trip = await self._trips.get_for_user(trip_id, user.id)
        if trip is None:
            return False
        document = await self._docs.get_for_trip(document_id, trip_id)
        if document is None:
            return False
        s3.delete_object(document.s3_key)
        await self._docs.delete(document)
        await self._session.commit()
        return True

    async def search(
        self, trip_id: uuid.UUID, user: UserModel, query: str, limit: int = 5
    ) -> DocumentSearchResponse | None:
        trip = await self._trips.get_for_user(trip_id, user.id)
        if trip is None:
            return None

        query_vec = embed_text(query)
        chunks = await self._docs.list_chunks_for_trip(trip_id)
        scored: list[tuple[float, DocumentChunkModel]] = []
        for chunk in chunks:
            if not chunk.embedding:
                continue
            score = cosine_similarity(query_vec, list(chunk.embedding))
            scored.append((score, chunk))
        scored.sort(key=lambda item: item[0], reverse=True)

        citations = [
            DocumentCitation(
                document_id=chunk.document_id,
                filename=chunk.document.filename,
                chunk_index=chunk.chunk_index,
                content=chunk.content,
                score=round(score, 4),
            )
            for score, chunk in scored[:limit]
        ]
        return DocumentSearchResponse(citations=citations)


def _to_response(document: DocumentModel) -> DocumentResponse:
    fields = None
    if document.extracted_fields:
        fields = ExtractedFieldsResponse.model_validate(document.extracted_fields)
    return DocumentResponse(
        id=document.id,
        trip_id=document.trip_id,
        filename=document.filename,
        mime_type=document.mime_type,
        size_bytes=document.size_bytes,
        status=document.status,
        extracted_fields=fields,
        error_message=document.error_message,
        injection_flagged=document.injection_flagged,
        created_at=document.created_at,
    )
