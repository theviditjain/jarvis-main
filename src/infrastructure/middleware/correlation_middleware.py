"""
Correlation ID Middleware.

Injects a unique correlation ID into every request for distributed tracing.
The ID is propagated in the ``X-Correlation-ID`` response header and
bound to all log entries for the duration of the request.
"""

from __future__ import annotations

import uuid

import structlog
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = structlog.get_logger(__name__)


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """
    Adds ``X-Correlation-ID`` to every request and response.

    If the client sends a ``X-Correlation-ID`` header, it is reused.
    Otherwise a new UUID4 is generated for each request.
    """

    HEADER_NAME = "X-Correlation-ID"

    async def dispatch(self, request: Request, call_next) -> Response:
        correlation_id = request.headers.get(self.HEADER_NAME) or str(uuid.uuid4())
        request.state.correlation_id = correlation_id

        structlog.contextvars.bind_contextvars(correlation_id=correlation_id)

        response = await call_next(request)
        response.headers[self.HEADER_NAME] = correlation_id

        structlog.contextvars.unbind_contextvars("correlation_id")
        return response
