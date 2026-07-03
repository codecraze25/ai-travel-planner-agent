"""Email draft templates and export helpers."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from email.message import EmailMessage
from enum import StrEnum


class EmailStatus(StrEnum):
    DRAFT = "draft"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPORTED = "exported"


class EmailTemplate(StrEnum):
    ITINERARY_SUMMARY = "itinerary_summary"
    FAMILY_SHARE = "family_share"


@dataclass(frozen=True)
class EmailDraftContent:
    subject: str
    body_text: str
    body_html: str


def build_email_draft(
    *,
    template: EmailTemplate,
    origin: str,
    destination: str,
    start_date: date,
    end_date: date,
    travelers: int,
    itinerary_summary: str,
    recipient: str,
) -> EmailDraftContent:
    dates = f"{start_date.isoformat()} – {end_date.isoformat()}"
    trip_line = f"{origin} to {destination} ({dates}, {travelers} traveler(s))"

    if template == EmailTemplate.FAMILY_SHARE:
        subject = f"Trip plans: {destination}"
        body_text = (
            f"Hi,\n\nSharing my travel plans for {trip_line}.\n\n"
            f"{itinerary_summary}\n\n"
            "Let me know if you have questions!\n"
        )
        body_html = (
            f"<p>Hi,</p><p>Sharing my travel plans for <strong>{trip_line}</strong>.</p>"
            f"<pre>{itinerary_summary}</pre>"
            "<p>Let me know if you have questions!</p>"
        )
    else:
        subject = f"Itinerary: {origin} to {destination}"
        body_text = (
            f"Trip itinerary for {trip_line}.\n\n"
            f"{itinerary_summary}\n\n"
            "This is a draft for your review. Nothing has been sent or booked.\n"
        )
        body_html = (
            f"<p>Trip itinerary for <strong>{trip_line}</strong>.</p>"
            f"<pre>{itinerary_summary}</pre>"
            "<p><em>This is a draft for your review. Nothing has been sent or booked.</em></p>"
        )

    return EmailDraftContent(subject=subject, body_text=body_text, body_html=body_html)


def format_itinerary_summary(items: list[dict[str, object]]) -> str:
    if not items:
        return "No itinerary items yet. Generate an itinerary first."
    lines: list[str] = []
    current_day: int | None = None
    for item in items:
        day = int(str(item["day_number"]))
        if day != current_day:
            current_day = day
            lines.append(f"\nDay {day}:")
        block = str(item.get("time_block", ""))
        title = str(item.get("title", ""))
        cost = float(str(item.get("est_cost_usd", 0) or 0))
        lines.append(f"  - {block}: {title} (${cost:.0f})")
    return "\n".join(lines).strip()


def build_eml(
    *,
    from_addr: str,
    to_addr: str,
    subject: str,
    body_text: str,
    body_html: str,
) -> str:
    msg = EmailMessage()
    msg["From"] = from_addr
    msg["To"] = to_addr
    msg["Subject"] = subject
    msg.set_content(body_text)
    msg.add_alternative(body_html, subtype="html")
    return msg.as_string()
