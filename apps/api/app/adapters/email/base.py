"""Email provider interface."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class OutboundEmail:
    from_addr: str
    to_addr: str
    subject: str
    body_text: str
    body_html: str


@dataclass(frozen=True)
class SendResult:
    provider: str
    message_id: str
    mock: bool


class EmailProvider(Protocol):
    async def send(self, message: OutboundEmail) -> SendResult: ...
