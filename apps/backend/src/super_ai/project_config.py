"""通用项目 JSON 配置加载：project.json 为基座，user.project.json 递归深合并。"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, cast

JsonObject = dict[str, Any]


def default_config_dir() -> Path:
    """仓库根目录下的 config/。不读取操作系统环境变量。"""
    return Path(__file__).resolve().parents[4] / "config"


def _as_object(value: Any) -> JsonObject:
    if not isinstance(value, dict):
        return {}
    result: JsonObject = {}
    for key, item in cast(dict[Any, Any], value).items():
        result[str(key)] = item
    return result


def deep_merge(base: JsonObject, override: JsonObject) -> JsonObject:
    merged: JsonObject = dict(base)
    for key, value in override.items():
        existing: Any = merged.get(key)
        current: Any = value
        if isinstance(existing, dict) and isinstance(current, dict):
            merged[key] = deep_merge(_as_object(existing), _as_object(current))
        else:
            merged[key] = value
    return merged


def _read_object(path: Path) -> JsonObject:
    if not path.is_file():
        return {}
    raw: Any = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        msg = f"配置文件必须是 JSON 对象: {path}"
        raise ValueError(msg)
    return _as_object(raw)


def load_project_config(
    *,
    project_path: Path | None = None,
    user_path: Path | None = None,
    config_dir: Path | None = None,
) -> JsonObject:
    """加载本地 JSON 深合并结果。测试必须传入临时路径，不得依赖本机真实文件。"""
    directory = config_dir if config_dir is not None else default_config_dir()
    resolved_project = project_path if project_path is not None else directory / "project.json"
    resolved_user = user_path if user_path is not None else directory / "user.project.json"
    return deep_merge(_read_object(resolved_project), _read_object(resolved_user))
