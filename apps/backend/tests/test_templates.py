import json
from typing import cast

from tests.conftest import REPO_ROOT

SECRET_KEYS = {"key", "secret", "password", "apikey", "token", "secretkey", "accesskey"}


def _collect_secret_values(node: object, found: list[str]) -> None:
    if isinstance(node, dict):
        items = cast(dict[object, object], node)
        for key_obj, value in items.items():
            key = str(key_obj)
            normalized = key.replace("_", "").replace("-", "").lower()
            if any(token in normalized for token in SECRET_KEYS):
                if isinstance(value, str):
                    if value != "":
                        found.append(f"{key}={value}")
                elif value not in ({}, [], None):
                    found.append(f"{key}={value!r}")
            _collect_secret_values(value, found)
    elif isinstance(node, list):
        values = cast(list[object], node)
        for item in values:
            _collect_secret_values(item, found)


def test_committed_templates_have_empty_secrets() -> None:
    for name in ("project.template.json", "user.project.template.json"):
        path = REPO_ROOT / "config" / name
        data: object = json.loads(path.read_text(encoding="utf-8"))
        found: list[str] = []
        _collect_secret_values(data, found)
        assert found == [], f"{name} 含有非空密钥字段: {found}"
