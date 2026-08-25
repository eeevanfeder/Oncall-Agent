from __future__ import annotations

from datetime import datetime
from typing import Protocol

from super_ai.auth.records import AuthSessionRecord, UserRecord


class UserRepository(Protocol):
    async def add(self, record: UserRecord) -> None:
        """写入用户。只 flush。"""

    async def get_by_id(self, user_id: str) -> UserRecord | None: ...

    async def get_by_email(self, email: str) -> UserRecord | None: ...


class AuthSessionRepository(Protocol):
    async def add(self, record: AuthSessionRecord) -> None:
        """写入会话。只 flush。"""

    async def get_active_by_token_hash(self, token_hash: str) -> AuthSessionRecord | None: ...

    async def touch_last_seen(self, session_id: str, user_id: str, seen_at: datetime) -> None:
        """仅更新属于该用户的会话 lastSeen。"""

    async def revoke(self, session_id: str, user_id: str, revoked_at: datetime) -> None:
        """仅撤销属于该用户的会话。"""
