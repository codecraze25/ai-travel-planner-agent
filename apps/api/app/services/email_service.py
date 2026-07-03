from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.db.models import EmailModel, UserModel
from app.adapters.db.repositories import (
    AuditLogRepository,
    EmailRepository,
    ItineraryRepository,
    TripRepository,
)
from app.api.schemas.email import (
    EmailDraftRequest,
    EmailExportResponse,
    EmailResponse,
    EmailUpdateRequest,
)
from app.domain.email import (
    EmailStatus,
    build_email_draft,
    build_eml,
    format_itinerary_summary,
)
from app.domain.guardrails import can_send_email


class EmailServiceError(ValueError):
    """Domain/service error for email operations."""


def _to_response(email: EmailModel) -> EmailResponse:
    return EmailResponse(
        id=email.id,
        trip_id=email.trip_id,
        template=email.template,
        status=email.status,
        recipients=email.recipients,
        subject=email.subject,
        body_text=email.body_text,
        body_html=email.body_html,
        approved_at=email.approved_at,
        created_at=email.created_at or datetime.now(UTC),
        updated_at=email.updated_at or datetime.now(UTC),
    )


class EmailService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._trips = TripRepository(session)
        self._emails = EmailRepository(session)
        self._itineraries = ItineraryRepository(session)
        self._audit = AuditLogRepository(session)

    async def list_emails(self, trip_id: uuid.UUID, user: UserModel) -> list[EmailResponse] | None:
        trip = await self._trips.get_for_user(trip_id, user.id)
        if trip is None:
            return None
        emails = await self._emails.list_for_trip(trip_id)
        return [_to_response(e) for e in emails]

    async def get_latest(self, trip_id: uuid.UUID, user: UserModel) -> EmailResponse | None:
        trip = await self._trips.get_for_user(trip_id, user.id)
        if trip is None:
            return None
        email = await self._emails.get_latest_for_trip(trip_id)
        if email is None:
            return None
        return _to_response(email)

    async def draft(
        self, trip_id: uuid.UUID, user: UserModel, payload: EmailDraftRequest
    ) -> EmailResponse | None:
        trip = await self._trips.get_for_user(trip_id, user.id)
        if trip is None:
            return None

        itinerary = await self._itineraries.get_latest_for_trip(trip_id)
        items = []
        if itinerary is not None:
            items = [
                {
                    "day_number": i.day_number,
                    "time_block": i.time_block,
                    "title": i.title,
                    "est_cost_usd": i.est_cost_usd,
                }
                for i in sorted(itinerary.items, key=lambda x: (x.day_number, x.sort_order))
            ]
        summary = format_itinerary_summary(items)
        recipients = payload.recipients or user.email
        content = build_email_draft(
            template=payload.template,
            origin=trip.origin,
            destination=trip.destination,
            start_date=trip.start_date,
            end_date=trip.end_date,
            travelers=trip.travelers,
            itinerary_summary=summary,
            recipient=recipients,
        )

        now = datetime.now(UTC)
        email = EmailModel(
            trip_id=trip_id,
            user_id=user.id,
            template=payload.template,
            status=EmailStatus.DRAFT,
            recipients=recipients,
            subject=content.subject,
            body_text=content.body_text,
            body_html=content.body_html,
            created_at=now,
            updated_at=now,
        )
        await self._emails.create(email)
        await self._audit.log(
            trip_id=trip_id,
            user_id=user.id,
            action="email.draft",
            details={"email_id": str(email.id), "template": payload.template.value},
        )
        response = _to_response(email)
        await self._session.commit()
        return response

    async def update(
        self,
        trip_id: uuid.UUID,
        email_id: uuid.UUID,
        user: UserModel,
        payload: EmailUpdateRequest,
    ) -> EmailResponse | None:
        trip = await self._trips.get_for_user(trip_id, user.id)
        if trip is None:
            return None
        email = await self._emails.get_for_trip(email_id, trip_id)
        if email is None:
            return None
        if email.status not in {EmailStatus.DRAFT, EmailStatus.REJECTED}:
            raise EmailServiceError("Only draft or rejected emails can be edited.")

        if payload.recipients is not None:
            email.recipients = payload.recipients
        if payload.subject is not None:
            email.subject = payload.subject
        if payload.body_text is not None:
            email.body_text = payload.body_text
        if payload.body_html is not None:
            email.body_html = payload.body_html
        email.status = EmailStatus.DRAFT
        email.approved_at = None
        email.updated_at = datetime.now(UTC)

        await self._emails.save(email)
        await self._audit.log(
            trip_id=trip_id,
            user_id=user.id,
            action="email.update",
            details={"email_id": str(email.id)},
        )
        response = _to_response(email)
        await self._session.commit()
        return response

    async def approve(
        self, trip_id: uuid.UUID, email_id: uuid.UUID, user: UserModel
    ) -> EmailResponse | None:
        trip = await self._trips.get_for_user(trip_id, user.id)
        if trip is None:
            return None
        email = await self._emails.get_for_trip(email_id, trip_id)
        if email is None:
            return None
        if email.status != EmailStatus.DRAFT:
            raise EmailServiceError("Only draft emails can be approved.")

        now = datetime.now(UTC)
        email.status = EmailStatus.APPROVED
        email.approved_at = now
        email.updated_at = now
        await self._emails.save(email)
        await self._audit.log(
            trip_id=trip_id,
            user_id=user.id,
            action="email.approve",
            details={"email_id": str(email.id)},
        )
        response = _to_response(email)
        await self._session.commit()
        return response

    async def reject(
        self, trip_id: uuid.UUID, email_id: uuid.UUID, user: UserModel
    ) -> EmailResponse | None:
        trip = await self._trips.get_for_user(trip_id, user.id)
        if trip is None:
            return None
        email = await self._emails.get_for_trip(email_id, trip_id)
        if email is None:
            return None
        if email.status not in {EmailStatus.DRAFT, EmailStatus.APPROVED}:
            raise EmailServiceError("Only draft or approved emails can be rejected.")

        email.status = EmailStatus.REJECTED
        email.approved_at = None
        email.updated_at = datetime.now(UTC)
        await self._emails.save(email)
        await self._audit.log(
            trip_id=trip_id,
            user_id=user.id,
            action="email.reject",
            details={"email_id": str(email.id)},
        )
        response = _to_response(email)
        await self._session.commit()
        return response

    async def export(
        self, trip_id: uuid.UUID, email_id: uuid.UUID, user: UserModel
    ) -> EmailExportResponse | None:
        """MVP send path: export .eml only after approval (guardrail)."""
        trip = await self._trips.get_for_user(trip_id, user.id)
        if trip is None:
            return None
        email = await self._emails.get_for_trip(email_id, trip_id)
        if email is None:
            return None

        user_approved = email.status in {EmailStatus.APPROVED, EmailStatus.EXPORTED}
        if not can_send_email(user_approved=user_approved):
            raise EmailServiceError("Export/send requires explicit user approval.")

        eml = build_eml(
            from_addr=user.email,
            to_addr=email.recipients,
            subject=email.subject,
            body_text=email.body_text,
            body_html=email.body_html,
        )
        email.status = EmailStatus.EXPORTED
        email.updated_at = datetime.now(UTC)
        await self._emails.save(email)
        await self._audit.log(
            trip_id=trip_id,
            user_id=user.id,
            action="email.export",
            details={"email_id": str(email.id), "note": "MVP export only — no SMTP send"},
        )
        response = EmailExportResponse(
            email=_to_response(email),
            eml=eml,
            filename=f"trip-{trip_id}-email-{email_id}.eml",
        )
        await self._session.commit()
        return response
