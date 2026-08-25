"""持久化边界。导入本包不得打开数据库或运行迁移。"""

from super_ai.memory.ids import new_id
from super_ai.memory.protocols import FoundationRepository
from super_ai.memory.records import FoundationRecord
from super_ai.memory.runtime import (
    MemoryRuntime,
    close_memory_runtime,
    create_memory_runtime,
    get_session,
    runtime_from_config,
)
from super_ai.memory.settings import database_url_from_config
from super_ai.memory.timeutil import as_utc, utc_now

__all__ = [
    "FoundationRecord",
    "FoundationRepository",
    "MemoryRuntime",
    "as_utc",
    "close_memory_runtime",
    "create_memory_runtime",
    "database_url_from_config",
    "get_session",
    "new_id",
    "runtime_from_config",
    "utc_now",
]
