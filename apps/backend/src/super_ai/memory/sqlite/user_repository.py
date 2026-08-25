from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from super_ai.auth.records import UserRecord
from super_ai.memory.sqlite.models import User
from super_ai.memory.timeutil import as_utc


def _to_record(row: User) -> UserRecord:
    return UserRecord(
        id=row.id,
        email=row.email,
        password_hash=row.password_hash,
        created_at=as_utc(row.created_at),
        updated_at=as_utc(row.updated_at),
    )


class SqliteUserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, record: UserRecord) -> None:
        self._session.add(
            User(
                id=record.id,
                email=record.email,
                password_hash=record.password_hash,
                created_at=as_utc(record.created_at),
                updated_at=as_utc(record.updated_at),
            )
        )
        await self._session.flush()

    async def get_by_id(self, user_id: str) -> UserRecord | None:
        row = await self._session.get(User, user_id)
        return None if row is None else _to_record(row)

    async def get_by_email(self, email: str) -> UserRecord | None:
        result = await self._session.execute(select(User).where(User.email == email))
        row = result.scalar_one_or_none()
        return None if row is None else _to_record(row)
