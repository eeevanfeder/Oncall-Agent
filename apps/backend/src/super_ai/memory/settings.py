"""从本地 JSON 深合并结果读取数据库 URL，不读取操作系统环境变量。"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, cast


def database_url_from_config(merged: Mapping[str, Any]) -> str:
    """返回 `database.url`；缺失或空白时为空字符串。"""
    raw_database: object = merged.get("database")
    if not isinstance(raw_database, dict):
        return ""
    raw_url: object = cast(dict[Any, Any], raw_database).get("url", "")
    if raw_url is None:
        return ""
    if not isinstance(raw_url, str):
        msg = "database.url 必须是字符串"
        raise TypeError(msg)
    return raw_url.strip()
