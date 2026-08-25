from __future__ import annotations

import asyncio
from pathlib import Path

from super_ai.memory.ids import new_id
from super_ai.memory.records import FoundationRecord
from super_ai.memory.runtime import close_memory_runtime, create_memory_runtime
from super_ai.memory.sqlite.models import FoundationMeta
from super_ai.memory.sqlite.repository import SqliteFoundationRepository
from super_ai.memory.testing import create_temp_sqlite_url, upgrade_to_head
from super_ai.memory.timeutil import utc_now

MEMORY_ROOT = Path(__file__).resolve().parents[1] / "src" / "super_ai" / "memory"
FORBIDDEN_EXPORTS = {
    "AiopsRepository",
    "AuditRepository",
    "ChatRepository",
    "FeedbackRepository",
    "KnowledgeRepository",
    "McpRepository",
    "TaskRepository",
}
FORBIDDEN_MODULES = {
    "aiops",
    "audit",
    "chat",
    "feedback",
    "knowledge",
    "mcp",
    "task",
}


def _record(label: str, **attributes: object) -> FoundationRecord:
    now = utc_now()
    return FoundationRecord(
        id=new_id(),
        label=label,
        attributes=attributes,
        created_at=now,
        updated_at=now,
    )


async def test_repository_contract_returns_immutable_record(tmp_path: Path) -> None:
    url = create_temp_sqlite_url(tmp_path)
    upgrade_to_head(url)
    runtime = create_memory_runtime(url)
    written = _record("contract", note="foundation")
    try:
        async with runtime.session_factory() as session:
            repo = SqliteFoundationRepository(session)
            await repo.add(written)
            await session.commit()

        async with runtime.session_factory() as session:
            repo = SqliteFoundationRepository(session)
            loaded = await repo.get(written.id)

        assert loaded is not None
        assert isinstance(loaded, FoundationRecord)
        assert not isinstance(loaded, FoundationMeta)
        assert loaded.id == written.id
        assert loaded.label == "contract"
        assert loaded.attributes["note"] == "foundation"
        assert loaded.created_at.tzinfo is not None
    finally:
        await close_memory_runtime(runtime)


async def test_transaction_rollback_discards_write(tmp_path: Path) -> None:
    url = create_temp_sqlite_url(tmp_path)
    upgrade_to_head(url)
    runtime = create_memory_runtime(url)
    written = _record("rollback")
    try:
        async with runtime.session_factory() as session:
            repo = SqliteFoundationRepository(session)
            await repo.add(written)
            await session.rollback()

        async with runtime.session_factory() as session:
            repo = SqliteFoundationRepository(session)
            assert await repo.get(written.id) is None
    finally:
        await close_memory_runtime(runtime)


async def test_concurrent_async_sessions(tmp_path: Path) -> None:
    url = create_temp_sqlite_url(tmp_path)
    upgrade_to_head(url)
    runtime = create_memory_runtime(url)

    async def write(label: str) -> FoundationRecord:
        record = _record(label)
        async with runtime.session_factory() as session:
            repo = SqliteFoundationRepository(session)
            await repo.add(record)
            await session.commit()
        return record

    try:
        left, right = await asyncio.gather(write("left"), write("right"))
        async with runtime.session_factory() as session:
            repo = SqliteFoundationRepository(session)
            assert await repo.get(left.id) is not None
            assert await repo.get(right.id) is not None
    finally:
        await close_memory_runtime(runtime)


def test_memory_exports_have_no_domain_repositories() -> None:
    import super_ai.memory as memory
    import super_ai.memory.extended_sqlite as extended
    import super_ai.memory.sqlite as sqlite

    for module in (memory, sqlite, extended):
        leaked = FORBIDDEN_EXPORTS.intersection(dir(module))
        assert leaked == set()


def test_memory_package_has_no_domain_modules() -> None:
    stems = {path.stem for path in MEMORY_ROOT.rglob("*.py")}
    assert stems.isdisjoint(FORBIDDEN_MODULES)
