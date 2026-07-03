from __future__ import annotations

from pydantic import BaseModel, Field


class AgentChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)


class AgentActionResponse(BaseModel):
    id: str
    tool_name: str
    success: bool
    error_message: str | None = None
    created_at: str
