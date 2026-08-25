from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from super_ai.auth.errors import AuthAppError
from super_ai.auth.passwords import dummy_password_hash, verify_password
from super_ai.auth.service import AuthService
from super_ai.memory.runtime import close_memory_runtime, create_memory_runtime
from super_ai.memory.testing import create_temp_sqlite_url, upgrade_to_head


async def test_unknown_email_still_runs_argon2(tmp_path: Path, monkeypatch: Any) -> None:
    url = create_temp_sqlite_url(tmp_path)
    upgrade_to_head(url)
    runtime = create_memory_runtime(url)
    calls = {"verify": 0}

    def tracking_verify(password: str, password_hash: str) -> bool:
        calls["verify"] += 1
        return verify_password(password, password_hash)

    monkeypatch.setattr("super_ai.auth.service.verify_password", tracking_verify)
    try:
        async with runtime.session_factory() as session:
            service = AuthService(session)
            dummy = dummy_password_hash()
            with pytest.raises(AuthAppError) as raised:
                await service.login("missing@example.com", "any-password")
            assert raised.value.code == "AUTH_INVALID_CREDENTIALS"
            assert calls["verify"] == 1
            assert dummy.startswith("$argon2")
    finally:
        await close_memory_runtime(runtime)
