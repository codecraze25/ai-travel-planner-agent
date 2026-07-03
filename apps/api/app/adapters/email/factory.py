from __future__ import annotations

from app.adapters.email.base import EmailProvider
from app.adapters.email.gmail import GmailEmailProvider
from app.adapters.email.mock import MockEmailProvider
from app.core.config import get_settings


def get_email_provider() -> EmailProvider:
    settings = get_settings()
    if settings.use_mock_email:
        return MockEmailProvider()
    return GmailEmailProvider(settings)
