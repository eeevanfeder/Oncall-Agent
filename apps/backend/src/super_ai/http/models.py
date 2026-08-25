from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class RequestMeta(BaseModel):
    requestId: str


class ApiErrorBody(BaseModel):
    code: str
    category: str
    httpStatus: int
    message: str
    details: dict[str, Any] | None = None


class SuccessEnvelope(BaseModel):
    ok: bool = True
    data: Any
    meta: RequestMeta


class FailureEnvelope(BaseModel):
    ok: bool = False
    error: ApiErrorBody
    meta: RequestMeta


class HealthData(BaseModel):
    status: str = "ok"


class EchoBody(BaseModel):
    name: str = Field(min_length=1)


class SseEventBase(BaseModel):
    id: str
    type: str
    channel: str
    timestamp: str


class ToolCallEvent(SseEventBase):
    type: str = "tool.call"
    toolCallId: str
    phase: str
    name: str | None = None
    argumentsDelta: str | None = None
    result: Any | None = None
    error: ApiErrorBody | None = None


class SseErrorEvent(SseEventBase):
    type: str = "error"
    error: ApiErrorBody
