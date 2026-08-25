from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class UserRecord:
    id: str
    email: str
    password_hash: str
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True, slots=True)
class AuthSessionRecord:
    id: str
    user_id: str
    token_hash: str
    created_at: datetime
    last_seen_at: datetime
    revoked_at: datetime | None
