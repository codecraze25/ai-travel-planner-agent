from __future__ import annotations

import uuid

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from app.core.logging import get_logger, set_correlation_id

logger = get_logger(__name__)

CORRELATION_HEADER = "X-Correlation-ID"


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        correlation_id = request.headers.get(CORRELATION_HEADER) or str(uuid.uuid4())
        set_correlation_id(correlation_id)
        request.state.correlation_id = correlation_id

        response = await call_next(request)
        response.headers[CORRELATION_HEADER] = correlation_id
        set_correlation_id(None)
        return response
