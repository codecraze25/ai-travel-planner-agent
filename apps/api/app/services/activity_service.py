from __future__ import annotations

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.db.models import UserModel
from app.adapters.db.repositories import (
    AgentActionRepository,
    AuditLogRepository,
    TripRepository,
)
from app.api.schemas.activity import ActivityItem, ActivityListResponse


class ActivityService:
    def __init__(self, session: AsyncSession) -> None:
        self._trips = TripRepository(session)
        self._actions = AgentActionRepository(session)
        self._audit = AuditLogRepository(session)

    async def list_activity(
        self, trip_id: uuid.UUID, user: UserModel
    ) -> ActivityListResponse | None:
        trip = await self._trips.get_for_user(trip_id, user.id)
        if trip is None:
            return None

        items: list[ActivityItem] = []
        for action in await self._actions.list_for_trip(trip_id):
            items.append(
                ActivityItem(
                    id=str(action.id),
                    kind="agent_action",
                    action=action.tool_name,
                    success=action.success,
                    details=action.input_json,
                    error_message=action.error_message,
                    created_at=action.created_at,
                )
            )
        for entry in await self._audit.list_for_trip(trip_id):
            items.append(
                ActivityItem(
                    id=str(entry.id),
                    kind="audit",
                    action=entry.action,
                    success=True,
                    details=entry.details,
                    created_at=entry.created_at,
                )
            )

        items.sort(key=lambda i: i.created_at, reverse=True)
        return ActivityListResponse(items=items)
