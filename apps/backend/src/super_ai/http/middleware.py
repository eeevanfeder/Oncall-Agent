from __future__ import annotations

from collections.abc import Awaitable, Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from super_ai.http.request_id import HEADER, STATE_KEY, resolve_request_id


class RequestIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        request_id = resolve_request_id(request.headers.get(HEADER))
        setattr(request.state, STATE_KEY, request_id)
        response = await call_next(request)
        response.headers[HEADER] = request_id
        return response
