from __future__ import annotations

import uuid

from starlette.requests import Request

HEADER = "X-Request-ID"
STATE_KEY = "request_id"


def resolve_request_id(incoming: str | None) -> str:
    if incoming is not None and incoming.strip() != "":
        return incoming.strip()
    return str(uuid.uuid4())


def request_id_of(request: Request) -> str:
    value = getattr(request.state, STATE_KEY, None)
    if isinstance(value, str) and value:
        return value
    generated = resolve_request_id(request.headers.get(HEADER))
    setattr(request.state, STATE_KEY, generated)
    return generated
