"""Repository Protocol。领域服务只依赖本协议与不可变 record。"""

from __future__ import annotations

from typing import Protocol

from super_ai.memory.records import FoundationRecord


class FoundationRepository(Protocol):
    async def add(self, record: FoundationRecord) -> None:
        """写入一条 foundation record。只 flush，不提交事务。"""

    async def get(self, record_id: str) -> FoundationRecord | None:
        """按 id 读取；不存在时返回 None。"""
