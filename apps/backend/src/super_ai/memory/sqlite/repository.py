"""SQLite FoundationRepository。事务由调用方 session 提交或回滚。"""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from super_ai.memory.records import FoundationRecord
from super_ai.memory.serialization import dump_json_object, load_json_object
from super_ai.memory.sqlite.models import FoundationMeta
from super_ai.memory.timeutil import as_utc


class SqliteFoundationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, record: FoundationRecord) -> None:
        row = FoundationMeta(
            id=record.id,
            label=record.label,
            attributes=dump_json_object(record.attributes),
            created_at=as_utc(record.created_at),
            updated_at=as_utc(record.updated_at),
        )
        self._session.add(row)
        await self._session.flush()

    async def get(self, record_id: str) -> FoundationRecord | None:
        row = await self._session.get(FoundationMeta, record_id)
        if row is None:
            return None
        return FoundationRecord(
            id=row.id,
            label=row.label,
            attributes=load_json_object(row.attributes),
            created_at=as_utc(row.created_at),
            updated_at=as_utc(row.updated_at),
        )
