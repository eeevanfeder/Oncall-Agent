from __future__ import annotations

import importlib
import sqlite3
from collections.abc import Iterator
from pathlib import Path

import pytest

from tests.conftest import REPO_ROOT

BACKEND_SRC = REPO_ROOT / "apps" / "backend" / "src"


def _iter_python_files(root: Path) -> Iterator[Path]:
    yield from root.rglob("*.py")


def test_no_src_super_ai_imports() -> None:
    offenders: list[str] = []
    for path in _iter_python_files(BACKEND_SRC):
        text = path.read_text(encoding="utf-8")
        if "from src.super_ai" in text or "import src.super_ai" in text:
            offenders.append(str(path.relative_to(REPO_ROOT)))
    assert offenders == []


def test_super_ai_import_does_not_open_sqlite(monkeypatch: pytest.MonkeyPatch) -> None:
    def forbidden(*_args: object, **_kwargs: object) -> None:
        raise AssertionError("import 期间不得连接 SQLite")

    monkeypatch.setattr(sqlite3, "connect", forbidden)
    import aiosqlite

    monkeypatch.setattr(aiosqlite, "connect", forbidden)

    from super_ai.app import create_app

    memory = importlib.import_module("super_ai.memory")
    sqlite = importlib.import_module("super_ai.memory.sqlite")
    extended = importlib.import_module("super_ai.memory.extended_sqlite")
    assert memory.database_url_from_config({}) == ""
    assert sqlite.__name__.endswith("sqlite")
    assert extended.__name__.endswith("extended_sqlite")
    create_app()


def test_health_endpoint() -> None:
    from super_ai.app import create_app, health_data

    assert health_data() == {"status": "ok"}
    app = create_app()
    paths: list[str] = []
    for route in app.routes:
        path = getattr(route, "path", None)
        if isinstance(path, str):
            paths.append(path)
    assert "/health" in paths
