"""Agent tool implementations — call services with guardrail checks."""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.db.models import UserModel
from app.adapters.db.repositories import AgentActionRepository
from app.api.schemas.travel import FlightSearchRequest, HotelSearchRequest
from app.domain.guardrails import is_tool_allowed
from app.services.document_service import DocumentService
from app.services.itinerary_service import ItineraryService
from app.services.travel_service import TravelService


class AgentTools:
    def __init__(
        self,
        session: AsyncSession,
        trip_id: uuid.UUID,
        user: UserModel,
        correlation_id: str | None = None,
        *,
        user_approved: bool = False,
    ) -> None:
        self._session = session
        self._trip_id = trip_id
        self._user = user
        self._correlation_id = correlation_id
        self._user_approved = user_approved
        self._actions = AgentActionRepository(session)
        self._travel = TravelService(session)
        self._documents = DocumentService(session)
        self._itinerary = ItineraryService(session)

    async def invoke(self, tool_name: str, args: dict[str, Any] | None = None) -> dict[str, Any]:
        args = args or {}
        allowed, reason = is_tool_allowed(tool_name, user_approved=self._user_approved)
        if not allowed:
            await self._log(tool_name, args, None, success=False, error=reason)
            return {"error": reason, "blocked": True}

        try:
            result = await self._dispatch(tool_name, args)
            await self._log(tool_name, args, result, success=True)
            return result
        except Exception as exc:  # noqa: BLE001 — tool errors surfaced to agent
            await self._log(tool_name, args, None, success=False, error=str(exc))
            return {"error": str(exc)}

    async def _dispatch(self, tool_name: str, args: dict[str, Any]) -> dict[str, Any]:
        if tool_name == "search_flights":
            flight_resp = await self._travel.search_flights(
                self._trip_id,
                self._user,
                FlightSearchRequest(**{k: v for k, v in args.items() if k != "trip_id"}),
            )
            if flight_resp is None:
                return {"error": "Trip not found"}
            return {
                "count": len(flight_resp.items),
                "tradeoffs": flight_resp.tradeoffs.model_dump(),
                "items": [f.model_dump() for f in flight_resp.items[:3]],
            }

        if tool_name == "search_hotels":
            hotel_resp = await self._travel.search_hotels(
                self._trip_id,
                self._user,
                HotelSearchRequest(**{k: v for k, v in args.items() if k != "trip_id"}),
            )
            if hotel_resp is None:
                return {"error": "Trip not found"}
            return {
                "count": len(hotel_resp.items),
                "items": [h.model_dump() for h in hotel_resp.items[:3]],
            }

        if tool_name == "read_pdf":
            query = str(args.get("query", ""))
            limit = int(args.get("limit", 5))
            doc_resp = await self._documents.search(self._trip_id, self._user, query, limit=limit)
            if doc_resp is None:
                return {"error": "Trip not found"}
            return doc_resp.model_dump()

        if tool_name == "calculate_budget":
            budget_resp = await self._travel.get_budget(self._trip_id, self._user)
            if budget_resp is None:
                return {"error": "Trip not found"}
            return budget_resp.model_dump()

        if tool_name == "generate_itinerary":
            regenerate_day = args.get("regenerate_day")
            itinerary_resp = await self._itinerary.generate(
                self._trip_id,
                self._user,
                regenerate_day=int(regenerate_day) if regenerate_day is not None else None,
            )
            if itinerary_resp is None:
                return {"error": "Trip not found"}
            return itinerary_resp.model_dump(mode="json")

        if tool_name == "send_email":
            return {"error": "Email drafting is available in Phase 5."}

        return {"error": f"Unknown tool: {tool_name}"}

    async def _log(
        self,
        tool_name: str,
        input_json: dict[str, Any] | None,
        output_json: dict[str, Any] | None,
        *,
        success: bool,
        error: str | None = None,
    ) -> None:
        await self._actions.log(
            trip_id=self._trip_id,
            user_id=self._user.id,
            tool_name=tool_name,
            input_json=input_json,
            output_json=output_json,
            success=success,
            error_message=error,
            correlation_id=self._correlation_id,
        )
