"""显式创建 async engine / session。模块导入不得打开数据库。"""

from __future__ import annotations

from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Any

from fastapi import Request
from sqlalchemy import event
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from super_ai.memory.settings import database_url_from_config


@dataclass(frozen=True, slots=True)
class MemoryRuntime:
    engine: AsyncEngine
    session_factory: async_sessionmaker[AsyncSession]


def _enable_sqlite_pragmas(dbapi_connection: Any, _connection_record: Any) -> None:
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.close()


def create_memory_runtime(url: str) -> MemoryRuntime:
    cleaned = url.strip()
    if not cleaned:
        msg = "database url 不能为空"
        raise ValueError(msg)
    engine = create_async_engine(cleaned, echo=False)
    if cleaned.startswith("sqlite"):
        event.listen(engine.sync_engine, "connect", _enable_sqlite_pragmas)
    factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    return MemoryRuntime(engine=engine, session_factory=factory)


async def close_memory_runtime(runtime: MemoryRuntime) -> None:
    await runtime.engine.dispose()


def runtime_from_config(merged: dict[str, Any]) -> MemoryRuntime | None:
    url = database_url_from_config(merged)
    if not url:
        return None
    return create_memory_runtime(url)


async def get_session(request: Request) -> AsyncIterator[AsyncSession]:
    """FastAPI 依赖：仅在 lifespan 已挂载 runtime 时提供 session。"""
    runtime = getattr(request.app.state, "memory", None)
    if not isinstance(runtime, MemoryRuntime):
        msg = "memory runtime 未初始化；请在 lifespan 或显式初始化路径中创建"
        raise RuntimeError(msg)
    async with runtime.session_factory() as session:
        yield session
