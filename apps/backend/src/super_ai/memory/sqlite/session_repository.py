from __future__ import annotations

from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from super_ai.auth.records import AuthSessionRecord
from super_ai.memory.sqlite.models import AuthSession
from super_ai.memory.timeutil import as_utc


def _to_record(row: AuthSession) -> AuthSessionRecord:
    return AuthSessionRecord(
        id=row.id,
        user_id=row.user_id,
        token_hash=row.token_hash,
        created_at=as_utc(row.created_at),
        last_seen_at=as_utc(row.last_seen_at),
        revoked_at=None if row.revoked_at is None else as_utc(row.revoked_at),
    )


class SqliteAuthSessionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, record: AuthSessionRecord) -> None:
        self._session.add(
            AuthSession(
                id=record.id,
                user_id=record.user_id,
                token_hash=record.token_hash,
                created_at=as_utc(record.created_at),
                last_seen_at=as_utc(record.last_seen_at),
                revoked_at=None if record.revoked_at is None else as_utc(record.revoked_at),
            )
        )
        await self._session.flush()

    async def get_active_by_token_hash(self, token_hash: str) -> AuthSessionRecord | None:
        result = await self._session.execute(
            select(AuthSession).where(
                AuthSession.token_hash == token_hash,
                AuthSession.revoked_at.is_(None),
            )
        )
        row = result.scalar_one_or_none()
        return None if row is None else _to_record(row)

    async def touch_last_seen(self, session_id: str, user_id: str, seen_at: datetime) -> None:
        await self._session.execute(
            update(AuthSession)
            .where(
                AuthSession.id == session_id,
                AuthSession.user_id == user_id,
                AuthSession.revoked_at.is_(None),
            )
            .values(last_seen_at=as_utc(seen_at))
        )
        await self._session.flush()

    async def revoke(self, session_id: str, user_id: str, revoked_at: datetime) -> None:
        await self._session.execute(
            update(AuthSession)
            .where(AuthSession.id == session_id, AuthSession.user_id == user_id)
            .values(revoked_at=as_utc(revoked_at))
        )
        await self._session.flush()
