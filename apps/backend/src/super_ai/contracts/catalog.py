"""从合同包 JSON 读取错误目录与字段约定。"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, cast

JsonObject = dict[str, Any]


def contracts_root() -> Path:
    return Path(__file__).resolve().parents[5] / "packages" / "api-contracts"


def load_json(relative: str) -> Any:
    path = contracts_root() / relative
    raw: Any = json.loads(path.read_text(encoding="utf-8"))
    return raw


def error_catalog() -> JsonObject:
    data = load_json("catalog/errors.json")
    return cast(JsonObject, data)


def envelope_fields() -> JsonObject:
    return cast(JsonObject, load_json("catalog/envelope-fields.json"))


def sse_types() -> list[str]:
    values = load_json("catalog/sse-types.json")
    return cast(list[str], values)
