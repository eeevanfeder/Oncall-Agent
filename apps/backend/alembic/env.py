"""Alembic 环境。schema 变更只通过迁移脚本表达，不在此 create_all。"""

from __future__ import annotations

import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy import create_engine, pool
from sqlalchemy.engine import Connection, make_url

_SRC = Path(__file__).resolve().parents[1] / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from super_ai.memory.sqlite.models import Base  # noqa: E402

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def _sync_url(url: str) -> str:
    if url.startswith("sqlite+aiosqlite://"):
        return "sqlite://" + url.removeprefix("sqlite+aiosqlite://")
    return url


def _ensure_sqlite_parent(url: str) -> None:
    parsed = make_url(url)
    database = parsed.database
    if parsed.get_backend_name() != "sqlite" or not database or database == ":memory:":
        return
    Path(database).expanduser().resolve().parent.mkdir(parents=True, exist_ok=True)


def run_migrations_offline() -> None:
    configured = config.get_main_option("sqlalchemy.url")
    if configured is None:
        msg = "sqlalchemy.url 未配置"
        raise RuntimeError(msg)
    url = _sync_url(configured)
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_as_batch=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        render_as_batch=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    configured = config.get_main_option("sqlalchemy.url")
    if configured is None:
        msg = "sqlalchemy.url 未配置"
        raise RuntimeError(msg)
    url = _sync_url(configured)
    _ensure_sqlite_parent(url)
    connectable = create_engine(url, poolclass=pool.NullPool)
    with connectable.connect() as connection:
        do_run_migrations(connection)
    connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
