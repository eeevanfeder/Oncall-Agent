"""认证 HTTP 路由与依赖。"""

from __future__ import annotations

from typing import Any

from fastapi import Depends, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator
from sqlalchemy.ext.asyncio import AsyncSession

from super_ai.auth.errors import AuthAppError
from super_ai.auth.records import UserRecord
from super_ai.auth.service import AuthService
from super_ai.http.errors import failure, lookup_error, success
from super_ai.http.request_id import request_id_of
from super_ai.memory.runtime import get_session
from super_ai.memory.timeutil import as_utc


class AuthCredentials(BaseModel):
    email: str = Field(min_length=3)
    password: str = Field(min_length=8)

    @field_validator("email")
    @classmethod
    def email_must_look_valid(cls, value: str) -> str:
        cleaned = value.strip()
        if "@" not in cleaned or cleaned.startswith("@") or cleaned.endswith("@"):
            raise ValueError("邮箱格式无效")
        return cleaned


def _iso(value: object) -> str:
    from datetime import datetime

    if not isinstance(value, datetime):
        return str(value)
    return as_utc(value).isoformat().replace("+00:00", "Z")


def user_payload(record: UserRecord) -> dict[str, str]:
    return {
        "id": record.id,
        "email": record.email,
        "createdAt": _iso(record.created_at),
    }


def bearer_token(request: Request) -> str:
    header = request.headers.get("Authorization", "")
    if not header.startswith("Bearer "):
        raise AuthAppError("AUTH_UNAUTHORIZED")
    token = header[7:].strip()
    if token == "":
        raise AuthAppError("AUTH_UNAUTHORIZED")
    return token


SESSION_DEP = Depends(get_session)


async def register(
    body: AuthCredentials,
    request: Request,
    session: AsyncSession = SESSION_DEP,
) -> dict[str, Any]:
    service = AuthService(session)
    user = await service.register(body.email, body.password)
    await session.commit()
    return success(user_payload(user), request_id_of(request))


async def login(
    body: AuthCredentials,
    request: Request,
    session: AsyncSession = SESSION_DEP,
) -> dict[str, Any]:
    service = AuthService(session)
    token, user = await service.login(body.email, body.password)
    await session.commit()
    return success(
        {"accessToken": token, "user": user_payload(user)},
        request_id_of(request),
    )


async def logout(
    request: Request,
    session: AsyncSession = SESSION_DEP,
) -> dict[str, Any]:
    service = AuthService(session)
    token = bearer_token(request)
    await service.current_user(token)
    await service.logout(token)
    await session.commit()
    return success({}, request_id_of(request))


async def me(
    request: Request,
    session: AsyncSession = SESSION_DEP,
) -> dict[str, Any]:
    user = await AuthService(session).current_user(bearer_token(request))
    await session.commit()
    return success(user_payload(user), request_id_of(request))


async def auth_error_handler(request: Request, exc: Exception) -> JSONResponse:
    if not isinstance(exc, AuthAppError):
        raise exc
    request_id = request_id_of(request)
    payload = failure(exc.code, request_id)
    status = int(lookup_error(exc.code)["httpStatus"])
    return JSONResponse(payload, status_code=status, headers={"X-Request-ID": request_id})
