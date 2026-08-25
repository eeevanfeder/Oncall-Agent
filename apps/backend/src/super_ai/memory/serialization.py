"""统一 JSON 对象字段的序列化约定。"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, cast


def dump_json_object(value: Mapping[str, Any] | None) -> dict[str, Any]:
    if value is None:
        return {}
    return dict(value)


def load_json_object(value: object) -> dict[str, Any]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        msg = "JSON 字段必须是对象"
        raise TypeError(msg)
    loaded: dict[str, Any] = {}
    for key, item in cast(dict[Any, Any], value).items():
        loaded[str(key)] = item
    return loaded
