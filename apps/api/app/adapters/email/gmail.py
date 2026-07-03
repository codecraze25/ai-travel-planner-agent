"""Gmail API provider scaffold — requires OAuth credentials (post-MVP wiring)."""

from __future__ import annotations

from app.adapters.email.base import OutboundEmail, SendResult
from app.core.config import Settings


class GmailNotConfiguredError(RuntimeError):
    """Raised when Gmail OAuth is not configured."""


class GmailEmailProvider:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def send(self, message: OutboundEmail) -> SendResult:
        del message
        if not self._settings.google_client_id or not self._settings.google_client_secret:
            raise GmailNotConfiguredError(
                "Gmail OAuth is not configured. Set GOOGLE_CLIENT_ID and "
                "GOOGLE_CLIENT_SECRET, or use USE_MOCK_EMAIL=true."
            )
        # Full Gmail API send is deferred until OAuth consent flow is implemented.
        raise GmailNotConfiguredError(
            "Gmail OAuth consent flow is not enabled yet. Use USE_MOCK_EMAIL=true "
            "or download the .eml export."
        )
