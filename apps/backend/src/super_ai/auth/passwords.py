"""Argon2 哈希。导入本模块不连接数据库。"""

from __future__ import annotations

from pwdlib import PasswordHash

_hasher = PasswordHash.recommended()
_dummy_hash: str | None = None


def hash_password(password: str) -> str:
    return _hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return _hasher.verify(password, password_hash)


def dummy_password_hash() -> str:
    global _dummy_hash
    if _dummy_hash is None:
        _dummy_hash = hash_password("super-ai-dummy-password-not-a-user")
    return _dummy_hash
