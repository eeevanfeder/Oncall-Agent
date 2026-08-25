"""FastAPI 应用工厂。导入本模块不得连接 SQLite、Milvus、LLM 或 MCP。"""

from __future__ import annotations

from collections.abc import AsyncGenerator, Mapping
from contextlib import asynccontextmanager
from typing import Any, cast

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from super_ai.auth.errors import AuthAppError
from super_ai.http.auth import auth_error_handler, login, logout, me, register
from super_ai.http.errors import failure, success
from super_ai.http.middleware import RequestIdMiddleware
from super_ai.http.models import EchoBody, HealthData
from super_ai.http.request_id import request_id_of
from super_ai.memory.runtime import close_memory_runtime, runtime_from_config
from super_ai.project_config import JsonObject, load_project_config


def health_data() -> dict[str, str]:
    return HealthData().model_dump(mode="json")


def _field_path(location: tuple[Any, ...]) -> str:
    return ".".join(str(part) for part in location)


async def validation_handler(request: Request, exc: Exception) -> JSONResponse:
    if not isinstance(exc, RequestValidationError):
        raise exc
    fields: list[dict[str, str]] = []
    for err in exc.errors():
        location = cast(tuple[Any, ...], err.get("loc", ()))
        fields.append({"path": _field_path(location), "message": str(err.get("msg", ""))})
    request_id = request_id_of(request)
    payload = failure(
        "VALIDATION_INVALID_INPUT",
        request_id,
        details={"fields": fields},
    )
    return JSONResponse(payload, status_code=422, headers={"X-Request-ID": request_id})


async def http_handler(request: Request, exc: Exception) -> JSONResponse:
    if not isinstance(exc, StarletteHTTPException):
        raise exc
    request_id = request_id_of(request)
    code = "BUSINESS_NOT_FOUND" if exc.status_code == 404 else "SYSTEM_INTERNAL_ERROR"
    payload = failure(code, request_id)
    status = int(cast(dict[str, Any], payload["error"])["httpStatus"])
    return JSONResponse(payload, status_code=status, headers={"X-Request-ID": request_id})


def health(request: Request) -> dict[str, Any]:
    return success(health_data(), request_id_of(request))


def echo(body: EchoBody, request: Request) -> dict[str, Any]:
    return success({"name": body.name}, request_id_of(request))


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    raw_config: object = getattr(app.state, "project_config", {})
    merged: JsonObject = {}
    if isinstance(raw_config, dict):
        for key, value in cast(dict[Any, Any], raw_config).items():
            merged[str(key)] = value
    runtime = runtime_from_config(merged)
    app.state.memory = runtime
    try:
        yield
    finally:
        if runtime is not None:
            await close_memory_runtime(runtime)


def create_app(*, project_config: Mapping[str, Any] | None = None) -> FastAPI:
    """默认不读取本机 JSON，也不打开数据库。显式传入配置后，lifespan 才可能创建 runtime。"""
    app = FastAPI(title="super-ai", version="0.2.0", lifespan=lifespan)
    app.state.project_config = dict(project_config) if project_config is not None else {}
    app.state.memory = None
    app.add_middleware(RequestIdMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://127.0.0.1:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_exception_handler(RequestValidationError, validation_handler)
    app.add_exception_handler(StarletteHTTPException, http_handler)
    app.add_exception_handler(AuthAppError, auth_error_handler)
    app.add_api_route("/health", health, methods=["GET"])
    app.add_api_route("/__contract__/echo", echo, methods=["POST"])
    app.add_api_route("/auth/register", register, methods=["POST"])
    app.add_api_route("/auth/login", login, methods=["POST"])
    app.add_api_route("/auth/logout", logout, methods=["POST"])
    app.add_api_route("/auth/me", me, methods=["GET"])
    return app


def create_app_from_local_config() -> FastAPI:
    """显式初始化路径：读取本地 JSON 深合并结果后再创建应用。"""
    return create_app(project_config=load_project_config())

