"""统一 ID 生成。"""

from __future__ import annotations

import uuid


def new_id() -> str:
    """生成 36 字符 UUID4 字符串。"""
    return str(uuid.uuid4())
