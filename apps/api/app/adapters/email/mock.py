"""Mock email provider — records sends without SMTP (local/CI default)."""

from __future__ import annotations

import uuid

from app.adapters.email.base import OutboundEmail, SendResult
from app.core.logging import get_logger

logger = get_logger(__name__)


class MockEmailProvider:
    async def send(self, message: OutboundEmail) -> SendResult:
        message_id = f"mock-{uuid.uuid4()}"
        logger.info(
            "mock_email_sent",
            message_id=message_id,
            to=message.to_addr,
            subject=message.subject,
        )
        return SendResult(provider="mock", message_id=message_id, mock=True)
