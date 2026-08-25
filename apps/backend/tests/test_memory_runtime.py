from __future__ import annotations

import importlib
import json
import os
from pathlib import Path
from typing import Any

import aiosqlite
import pytest
from starlette.testclient import TestClient

from super_ai.app import create_app
from super_ai.memory.settings import database_url_from_config
from super_ai.memory.testing import (
    DEVELOPER_SQLITE,
    create_temp_sqlite_url,
    upgrade_to_head,
)
from super_ai.project_config import load_project_config


def test_database_url_from_temp_json_not_developer_db(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    isolated = tmp_path / "isolated.sqlite3"
    url = f"sqlite+aiosqlite:///{isolated.resolve()}"
    project_path = tmp_path / "project.json"
    user_path = tmp_path / "user.project.json"
    project_path.write_text(json.dumps({"database": {"url": url}}), encoding="utf-8")
    user_path.write_text("{}", encoding="utf-8")
    monkeypatch.setenv("DATABASE_URL", f"sqlite+aiosqlite:///{DEVELOPER_SQLITE}")
    monkeypatch.setenv("SUPER_AI_DATABASE_URL", "sqlite+aiosqlite:///./var/memory.sqlite3")

    loaded = load_project_config(project_path=project_path, user_path=user_path)
    resolved = database_url_from_config(loaded)

    assert resolved == url
    assert str(DEVELOPER_SQLITE) not in resolved
    assert "var/memory.sqlite3" not in resolved
    assert os.environ["DATABASE_URL"].endswith("memory.sqlite3")


def test_missing_database_url_is_empty() -> None:
    assert database_url_from_config({}) == ""
    assert database_url_from_config({"database": {}}) == ""
    assert database_url_from_config({"database": {"url": "  "}}) == ""


def test_temp_helper_rejects_developer_db() -> None:
    from super_ai.memory.testing import assert_not_developer_db

    with pytest.raises(ValueError, match="var/memory.sqlite3"):
        assert_not_developer_db(f"sqlite+aiosqlite:///{DEVELOPER_SQLITE}")


def test_lifespan_uses_injected_url(tmp_path: Path) -> None:
    url = create_temp_sqlite_url(tmp_path)
    upgrade_to_head(url)
    app = create_app(project_config={"database": {"url": url}})
    client: Any = TestClient(app)
    with client:
        assert client.app.state.memory is not None
        response: Any = client.get("/health")
        assert response.status_code == 200
        assert response.json()["data"] == {"status": "ok"}


def test_create_app_without_config_does_not_attach_runtime() -> None:
    app = create_app()
    client: Any = TestClient(app)
    with client:
        assert client.app.state.memory is None
        response: Any = client.get("/health")
        assert response.status_code == 200


def test_memory_import_does_not_open_sqlite(monkeypatch: pytest.MonkeyPatch) -> None:
    def forbidden(*_args: object, **_kwargs: object) -> None:
        raise AssertionError("import 期间不得连接 SQLite")

    import sqlite3

    monkeypatch.setattr(sqlite3, "connect", forbidden)
    monkeypatch.setattr(aiosqlite, "connect", forbidden)

    import super_ai.memory

    sqlite = importlib.import_module("super_ai.memory.sqlite")
    extended = importlib.import_module("super_ai.memory.extended_sqlite")
    testing = importlib.import_module("super_ai.memory.testing")
    assert super_ai.memory.FoundationRecord.__name__ == "FoundationRecord"
    assert sqlite.__name__.endswith("sqlite")
    assert extended.__name__.endswith("extended_sqlite")
    assert testing.create_temp_sqlite_url
    create_app()
    create_app(project_config={"database": {"url": "sqlite+aiosqlite:///should-not-open.db"}})
