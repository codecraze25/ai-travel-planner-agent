from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.domain.email import EmailStatus, EmailTemplate


class EmailDraftRequest(BaseModel):
    template: EmailTemplate = EmailTemplate.ITINERARY_SUMMARY
    recipients: str | None = Field(default=None, max_length=1024)


class EmailUpdateRequest(BaseModel):
    recipients: str | None = Field(default=None, max_length=1024)
    subject: str | None = Field(default=None, max_length=512)
    body_text: str | None = None
    body_html: str | None = None


class EmailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    trip_id: uuid.UUID
    template: EmailTemplate
    status: EmailStatus
    recipients: str
    subject: str
    body_text: str
    body_html: str
    approved_at: datetime | None = None
    sent_at: datetime | None = None
    provider_message_id: str | None = None
    created_at: datetime
    updated_at: datetime


class EmailListResponse(BaseModel):
    items: list[EmailResponse]


class EmailExportResponse(BaseModel):
    email: EmailResponse
    eml: str
    filename: str


class EmailSendResponse(BaseModel):
    email: EmailResponse
    provider: str
    message_id: str
    mock: bool
