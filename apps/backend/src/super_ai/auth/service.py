from __future__ import annotations

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from super_ai.auth.emails import normalize_email
from super_ai.auth.errors import AuthAppError
from super_ai.auth.passwords import dummy_password_hash, hash_password, verify_password
from super_ai.auth.records import AuthSessionRecord, UserRecord
from super_ai.auth.tokens import hash_access_token, new_access_token
from super_ai.memory.ids import new_id
from super_ai.memory.sqlite.session_repository import SqliteAuthSessionRepository
from super_ai.memory.sqlite.user_repository import SqliteUserRepository
from super_ai.memory.timeutil import utc_now


class AuthService:
    def __init__(self, session: AsyncSession) -> None:
        self._users = SqliteUserRepository(session)
        self._sessions = SqliteAuthSessionRepository(session)

    async def register(self, email: str, password: str) -> UserRecord:
        normalized = normalize_email(email)
        if await self._users.get_by_email(normalized) is not None:
            raise AuthAppError("BUSINESS_CONFLICT")
        now = utc_now()
        record = UserRecord(
            id=new_id(),
            email=normalized,
            password_hash=hash_password(password),
            created_at=now,
            updated_at=now,
        )
        try:
            await self._users.add(record)
        except IntegrityError as exc:
            raise AuthAppError("BUSINESS_CONFLICT") from exc
        return record

    async def login(self, email: str, password: str) -> tuple[str, UserRecord]:
        normalized = normalize_email(email)
        user = await self._users.get_by_email(normalized)
        password_hash = user.password_hash if user is not None else dummy_password_hash()
        valid = verify_password(password, password_hash)
        if user is None or not valid:
            raise AuthAppError("AUTH_INVALID_CREDENTIALS")
        raw = new_access_token()
        now = utc_now()
        await self._sessions.add(
            AuthSessionRecord(
                id=new_id(),
                user_id=user.id,
                token_hash=hash_access_token(raw),
                created_at=now,
                last_seen_at=now,
                revoked_at=None,
            )
        )
        return raw, user

    async def current_user(self, raw_token: str) -> UserRecord:
        stored = await self._sessions.get_active_by_token_hash(hash_access_token(raw_token))
        if stored is None:
            raise AuthAppError("AUTH_UNAUTHORIZED")
        user = await self._users.get_by_id(stored.user_id)
        if user is None:
            raise AuthAppError("AUTH_UNAUTHORIZED")
        await self._sessions.touch_last_seen(stored.id, stored.user_id, utc_now())
        return user

    async def logout(self, raw_token: str) -> None:
        stored = await self._sessions.get_active_by_token_hash(hash_access_token(raw_token))
        if stored is None:
            raise AuthAppError("AUTH_UNAUTHORIZED")
        await self._sessions.revoke(stored.id, stored.user_id, utc_now())
