from __future__ import annotations

from pathlib import Path

from alembic.autogenerate import compare_metadata
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory
from sqlalchemy import inspect, text
from sqlalchemy.engine import Connection

from super_ai.memory.runtime import close_memory_runtime, create_memory_runtime
from super_ai.memory.sqlite.models import Base
from super_ai.memory.testing import alembic_config, create_temp_sqlite_url, upgrade_to_head


async def test_fresh_database_upgrade_reaches_head(tmp_path: Path) -> None:
    url = create_temp_sqlite_url(tmp_path)
    db_path = tmp_path / "test.sqlite3"
    assert not db_path.exists()
    assert "var/memory.sqlite3" not in url

    upgrade_to_head(url)
    assert db_path.is_file()

    script = ScriptDirectory.from_config(alembic_config(url))
    head = script.get_current_head()
    runtime = create_memory_runtime(url)
    try:
        async with runtime.engine.connect() as connection:
            tables = await connection.run_sync(lambda sync: inspect(sync).get_table_names())
            version = await connection.scalar(text("SELECT version_num FROM alembic_version"))
        assert "foundation_meta" in tables
        assert "alembic_version" in tables
        assert version == head
        assert head == "20260825_0002"
    finally:
        await close_memory_runtime(runtime)


async def test_metadata_matches_migrations(tmp_path: Path) -> None:
    url = create_temp_sqlite_url(tmp_path)
    upgrade_to_head(url)
    runtime = create_memory_runtime(url)
    try:

        def _diff(sync_conn: Connection) -> list[object]:
            context = MigrationContext.configure(sync_conn)
            return list(compare_metadata(context, Base.metadata))

        async with runtime.engine.connect() as connection:
            diffs = await connection.run_sync(_diff)
            tables = await connection.run_sync(lambda sync: set(inspect(sync).get_table_names()))
        assert diffs == []
        assert tables - {"alembic_version"} == set(Base.metadata.tables)
    finally:
        await close_memory_runtime(runtime)
