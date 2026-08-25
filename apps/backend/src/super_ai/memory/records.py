"""领域可见的不可变持久化 record。不得把 ORM model 传出仓储边界。"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from types import MappingProxyType
from typing import Any


@dataclass(frozen=True, slots=True)
class FoundationRecord:
    id: str
    label: str
    attributes: Mapping[str, Any]
    created_at: datetime
    updated_at: datetime

    def __post_init__(self) -> None:
        object.__setattr__(self, "attributes", MappingProxyType(dict(self.attributes)))
