"""Agent tool guardrails enforced in code (not prompt-only)."""

from __future__ import annotations

MVP_BLOCKED_TOOLS = frozenset({"book_hotel"})


def can_book_hotel(*, mvp_mode: bool = True) -> bool:
    """Hotel booking is hard-disabled in MVP."""
    return not mvp_mode


def can_send_email(*, user_approved: bool) -> bool:
    """Email send requires explicit user approval."""
    return user_approved


def is_tool_allowed(
    tool_name: str,
    *,
    user_approved: bool = False,
    mvp_mode: bool = True,
) -> tuple[bool, str | None]:
    """Return (allowed, denial_reason)."""
    if mvp_mode and tool_name in MVP_BLOCKED_TOOLS:
        return False, f"{tool_name} is disabled in MVP. Use external booking links instead."
    if tool_name == "send_email" and not can_send_email(user_approved=user_approved):
        return False, "send_email requires explicit user approval."
    if tool_name == "book_hotel" and not can_book_hotel(mvp_mode=mvp_mode):
        return False, "book_hotel is disabled in MVP."
    return True, None
