"""测试用临时 SQLite 与 Alembic helper。导入本模块不得打开数据库。"""

from __future__ import annotations

from pathlib import Path

from alembic import command
from alembic.config import Config

BACKEND_ROOT = Path(__file__).resolve().parents[3]
DEVELOPER_SQLITE = (BACKEND_ROOT / "var" / "memory.sqlite3").resolve()
ALEMBIC_INI = BACKEND_ROOT / "alembic.ini"


def sqlite_async_url(path: Path) -> str:
    return f"sqlite+aiosqlite:///{path.resolve()}"


def assert_not_developer_db(url: str, path: Path | None = None) -> None:
    banned = DEVELOPER_SQLITE
    if path is not None and path.resolve() == banned:
        msg = "测试不得使用开发者本机 var/memory.sqlite3"
        raise ValueError(msg)
    if str(banned) in url.replace("\\", "/"):
        msg = "测试不得使用开发者本机 var/memory.sqlite3"
        raise ValueError(msg)


def create_temp_sqlite_url(directory: Path) -> str:
    path = directory / "test.sqlite3"
    url = sqlite_async_url(path)
    assert_not_developer_db(url, path)
    return url


def alembic_config(url: str | None = None) -> Config:
    config = Config(str(ALEMBIC_INI))
    config.set_main_option("script_location", str(BACKEND_ROOT / "alembic"))
    config.set_main_option("prepend_sys_path", str(BACKEND_ROOT / "src"))
    config.set_main_option("path_separator", "os")
    if url is not None:
        assert_not_developer_db(url)
        config.set_main_option("sqlalchemy.url", url)
    return config


def upgrade_to_head(url: str) -> None:
    """对指定 URL 执行 alembic upgrade head。禁止指向本机 var/memory.sqlite3。"""
    command.upgrade(alembic_config(url), "head")
