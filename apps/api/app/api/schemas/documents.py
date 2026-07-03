from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.domain.documents import DocumentStatus


class ExtractedFieldsResponse(BaseModel):
    dates: list[str] = Field(default_factory=list)
    times: list[str] = Field(default_factory=list)
    locations: list[str] = Field(default_factory=list)
    reservation_numbers: list[str] = Field(default_factory=list)
    passenger_names: list[str] = Field(default_factory=list)
    confirmation_codes: list[str] = Field(default_factory=list)
    check_in: str | None = None
    check_out: str | None = None
    policy_rules: list[str] = Field(default_factory=list)


class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    trip_id: UUID
    filename: str
    mime_type: str
    size_bytes: int
    status: DocumentStatus
    extracted_fields: ExtractedFieldsResponse | None = None
    error_message: str | None = None
    injection_flagged: bool = False
    created_at: datetime


class DocumentListResponse(BaseModel):
    items: list[DocumentResponse]


class DocumentSearchRequest(BaseModel):
    query: str = Field(min_length=1)
    limit: int = Field(default=5, ge=1, le=20)


class DocumentCitation(BaseModel):
    document_id: UUID
    filename: str
    chunk_index: int
    content: str
    score: float


class DocumentSearchResponse(BaseModel):
    citations: list[DocumentCitation]
    facts_note: str = (
        "Citations are extracted facts from uploaded documents. "
        "Recommendations are separate from these facts."
    )
