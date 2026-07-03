"""Agent state machine runner (mirrors LangGraph design in ARCHITECTURE.md §4.1)."""

from __future__ import annotations

import re
from collections.abc import AsyncIterator
from typing import Any

from app.agent.tools import AgentTools


class AgentRunner:
    """Deterministic mock agent for local dev and CI eval harness."""

    def __init__(self, tools: AgentTools, *, destination: str, origin: str) -> None:
        self._tools = tools
        self._destination = destination
        self._origin = origin

    async def run(self, message: str) -> AsyncIterator[dict[str, Any]]:
        normalized = message.strip().lower()

        if self._is_plan_request(normalized):
            yield {
                "type": "message",
                "role": "assistant",
                "content": (
                    f"Planning {self._origin} to {self._destination}. "
                    "Searching flights and hotels, then building your itinerary."
                ),
            }

            steps: list[tuple[str, dict[str, Any]]] = [
                ("search_flights", {}),
                ("search_hotels", {}),
                ("calculate_budget", {}),
            ]
            for tool_name, tool_args in steps:
                yield {"type": "tool_call", "tool": tool_name, "input": tool_args}
                result = await self._tools.invoke(tool_name, tool_args)
                yield {"type": "tool_result", "tool": tool_name, "output": result}

            yield {"type": "tool_call", "tool": "generate_itinerary", "input": {}}
            itinerary = await self._tools.invoke("generate_itinerary", {})
            yield {"type": "tool_result", "tool": "generate_itinerary", "output": itinerary}

            if "error" not in itinerary:
                days = len({item["day_number"] for item in itinerary.get("items", [])})
                yield {"type": "itinerary", "data": itinerary}

                yield {"type": "tool_call", "tool": "draft_email", "input": {}}
                draft = await self._tools.invoke("draft_email", {})
                yield {"type": "tool_result", "tool": "draft_email", "output": draft}

                if "error" not in draft:
                    yield {"type": "email_draft", "data": draft}
                    yield {
                        "type": "message",
                        "role": "assistant",
                        "content": (
                            f"Done — {days}-day plan is ready with flights, hotels, and an "
                            "email draft. Review the options above. Approve the email when "
                            "you are ready; nothing is sent without your approval."
                        ),
                    }
                else:
                    yield {
                        "type": "message",
                        "role": "assistant",
                        "content": (
                            f"Your {days}-day itinerary is ready. "
                            f"Email draft failed: {draft['error']}"
                        ),
                    }
            else:
                yield {
                    "type": "message",
                    "role": "assistant",
                    "content": f"I couldn't generate the itinerary: {itinerary['error']}",
                }

            yield {"type": "done"}
            return

        if "approve" in normalized and "email" in normalized:
            yield {
                "type": "message",
                "role": "assistant",
                "content": "Use the Approve button on the email card above to confirm.",
            }
            yield {"type": "done"}
            return

        if "email" in normalized or "draft" in normalized:
            yield {
                "type": "message",
                "role": "assistant",
                "content": "Drafting an itinerary email for your review…",
            }
            yield {"type": "tool_call", "tool": "draft_email", "input": {}}
            draft = await self._tools.invoke("draft_email", {})
            yield {"type": "tool_result", "tool": "draft_email", "output": draft}
            if "error" not in draft:
                yield {"type": "email_draft", "data": draft}
                yield {
                    "type": "message",
                    "role": "assistant",
                    "content": (
                        "Email draft ready above. Approve it before send or download — "
                        "I will not send without your approval."
                    ),
                }
            else:
                yield {
                    "type": "message",
                    "role": "assistant",
                    "content": f"Could not draft email: {draft['error']}",
                }
            yield {"type": "done"}
            return

        yield {
            "type": "message",
            "role": "assistant",
            "content": (
                "Tell me your trip in one sentence — for example: "
                '"Plan San Francisco to Tokyo 2026-10-10 to 2026-10-15 for 2 travelers $4000". '
                "I'll search flights and hotels and build the itinerary here in chat."
            ),
        }
        yield {"type": "done"}

    @staticmethod
    def _is_plan_request(message: str) -> bool:
        return bool(
            re.search(
                r"\b(plan|itinerary|schedule|book|trip|flight|hotel)\b",
                message,
            )
        )
