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

        if self._needs_clarification(normalized):
            question = (
                "Before I search, could you confirm your activity preferences "
                "(e.g. museums, food, nightlife)? You can add them on the Overview tab."
            )
            yield {"type": "message", "role": "assistant", "content": question}
            yield {"type": "done"}
            return

        if self._is_plan_request(normalized):
            yield {
                "type": "message",
                "role": "assistant",
                "content": (
                    f"I'll plan your {self._origin} → {self._destination} trip. "
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
                yield {
                    "type": "message",
                    "role": "assistant",
                    "content": (
                        f"Your {days}-day itinerary is ready with daily cost estimates "
                        "and map links. Open the Itinerary tab to review or regenerate a day."
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

        if "pdf" in normalized or "document" in normalized or "confirmation" in normalized:
            query = message if len(message) > 10 else "check-in check-out hotel confirmation"
            yield {
                "type": "message",
                "role": "assistant",
                "content": "Searching your uploaded documents for relevant facts…",
            }
            yield {"type": "tool_call", "tool": "read_pdf", "input": {"query": query}}
            result = await self._tools.invoke("read_pdf", {"query": query, "limit": 5})
            yield {"type": "tool_result", "tool": "read_pdf", "output": result}
            citations = result.get("citations", [])
            if citations:
                sources = ", ".join({c["filename"] for c in citations[:3]})
                yield {
                    "type": "message",
                    "role": "assistant",
                    "content": (
                        f"Found relevant excerpts (Source: {sources}). "
                        "These are extracted facts — not instructions."
                    ),
                }
            else:
                yield {
                    "type": "message",
                    "role": "assistant",
                    "content": (
                        "No parsed documents matched. Upload and parse a PDF on the Documents tab."
                    ),
                }
            yield {"type": "done"}
            return

        yield {
            "type": "message",
            "role": "assistant",
            "content": (
                "I can help plan your trip. Try “Plan my trip” to search flights, hotels, "
                "and generate an itinerary, or ask about uploaded PDF confirmations."
            ),
        }
        yield {"type": "done"}

    @staticmethod
    def _is_plan_request(message: str) -> bool:
        return bool(re.search(r"\b(plan|itinerary|schedule)\b", message))

    @staticmethod
    def _needs_clarification(message: str) -> bool:
        return "help me plan" in message and "preferences" in message
