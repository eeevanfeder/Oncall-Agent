from __future__ import annotations

import logging
import sqlite3
from collections.abc import Iterator
from pathlib import Path
from typing import Any, cast

import pytest
from starlette.testclient import TestClient

from super_ai.app import create_app
from super_ai.memory.testing import create_temp_sqlite_url, upgrade_to_head

PASSWORD = "secret-pass-12"


def _sqlite_path(url: str) -> Path:
    return Path(url.removeprefix("sqlite+aiosqlite:///"))


def _rows(url: str, sql: str, args: tuple[object, ...] = ()) -> list[dict[str, Any]]:
    connection = sqlite3.connect(_sqlite_path(url))
    connection.row_factory = sqlite3.Row
    try:
        return [dict(row) for row in connection.execute(sql, args)]
    finally:
        connection.close()


@pytest.fixture
def auth_env(tmp_path: Path) -> Iterator[tuple[Any, Any, str]]:
    url = create_temp_sqlite_url(tmp_path)
    upgrade_to_head(url)
    app = create_app(project_config={"database": {"url": url}})
    client: Any = TestClient(app)
    with client:
        yield client, app, url


def _json(
    client: Any, method: str, path: str, **kwargs: Any
) -> tuple[int, dict[str, Any], dict[str, str]]:
    response: Any = getattr(client, method)(path, **kwargs)
    headers = {str(key): str(value) for key, value in response.headers.items()}
    payload = cast(dict[str, Any], response.json())
    return int(response.status_code), payload, headers


def test_auth_tables_exist_after_upgrade(tmp_path: Path) -> None:
    url = create_temp_sqlite_url(tmp_path)
    upgrade_to_head(url)
    table_sql = "SELECT name FROM sqlite_master WHERE type='table'"
    tables = {row["name"] for row in _rows(url, table_sql)}
    assert {"users", "auth_sessions"} <= tables
    user_cols = {row["name"] for row in _rows(url, "PRAGMA table_info(users)")}
    session_cols = {row["name"] for row in _rows(url, "PRAGMA table_info(auth_sessions)")}
    assert {"id", "email", "password_hash", "created_at", "updated_at"} <= user_cols
    session_required = {"id", "user_id", "token_hash", "created_at", "last_seen_at", "revoked_at"}
    assert session_required <= session_cols


def test_register_normalizes_email_and_returns_user(auth_env: tuple[Any, Any, str]) -> None:
    client, _app, _url = auth_env
    status, payload, headers = _json(
        client,
        "post",
        "/auth/register",
        json={"email": "  User@Example.COM ", "password": PASSWORD},
    )
    assert status == 200
    assert payload["ok"] is True
    assert payload["data"]["email"] == "user@example.com"
    assert payload["data"]["id"]
    assert payload["data"]["createdAt"]
    assert "password" not in payload["data"]
    assert "accessToken" not in payload["data"]
    assert headers["x-request-id"] == payload["meta"]["requestId"]


def test_duplicate_email_returns_conflict(auth_env: tuple[Any, Any, str]) -> None:
    client, _app, _url = auth_env
    _json(client, "post", "/auth/register", json={"email": "dup@example.com", "password": PASSWORD})
    status, payload, _headers = _json(
        client,
        "post",
        "/auth/register",
        json={"email": "DUP@example.com", "password": PASSWORD},
    )
    assert status == 409
    assert payload["ok"] is False
    assert payload["error"]["code"] == "BUSINESS_CONFLICT"


def test_login_success_and_wrong_credentials(auth_env: tuple[Any, Any, str]) -> None:
    client, _app, _url = auth_env
    _json(
        client,
        "post",
        "/auth/register",
        json={"email": "login@example.com", "password": PASSWORD},
    )
    ok_status, ok_payload, _ok_headers = _json(
        client,
        "post",
        "/auth/login",
        json={"email": "login@example.com", "password": PASSWORD},
    )
    assert ok_status == 200
    assert ok_payload["data"]["accessToken"]
    assert ok_payload["data"]["user"]["email"] == "login@example.com"

    missing_status, missing_payload, _h1 = _json(
        client,
        "post",
        "/auth/login",
        json={"email": "nobody@example.com", "password": PASSWORD},
    )
    wrong_status, wrong_payload, _h2 = _json(
        client,
        "post",
        "/auth/login",
        json={"email": "login@example.com", "password": "wrong-password"},
    )
    assert missing_status == 401
    assert wrong_status == 401
    assert missing_payload["error"]["code"] == "AUTH_INVALID_CREDENTIALS"
    assert wrong_payload["error"]["code"] == "AUTH_INVALID_CREDENTIALS"


def test_password_hash_is_not_plaintext_and_not_logged(
    auth_env: tuple[Any, Any, str], caplog: pytest.LogCaptureFixture
) -> None:
    client, _app, url = auth_env
    with caplog.at_level(logging.DEBUG):
        status, payload, _headers = _json(
            client,
            "post",
            "/auth/register",
            json={"email": "hash@example.com", "password": PASSWORD},
        )
    assert status == 200
    rows = _rows(url, "SELECT email, password_hash FROM users")
    assert len(rows) == 1
    stored = str(rows[0]["password_hash"])
    assert stored != PASSWORD
    assert stored.startswith("$argon2")
    dumped = str(payload)
    assert PASSWORD not in dumped
    assert PASSWORD not in caplog.text


def test_database_does_not_store_raw_token(auth_env: tuple[Any, Any, str]) -> None:
    client, _app, url = auth_env
    _json(
        client,
        "post",
        "/auth/register",
        json={"email": "token@example.com", "password": PASSWORD},
    )
    _status, payload, _headers = _json(
        client,
        "post",
        "/auth/login",
        json={"email": "token@example.com", "password": PASSWORD},
    )
    raw = str(payload["data"]["accessToken"])
    sessions = _rows(url, "SELECT * FROM auth_sessions")
    assert len(sessions) == 1
    blob = " ".join(str(value) for value in sessions[0].values())
    assert raw not in blob
    token_hash = str(sessions[0]["token_hash"])
    assert len(token_hash) == 64
    assert token_hash != raw


def test_me_updates_last_seen_and_logout_revokes(auth_env: tuple[Any, Any, str]) -> None:
    client, _app, url = auth_env
    _json(
        client,
        "post",
        "/auth/register",
        json={"email": "seen@example.com", "password": PASSWORD},
    )
    _login_status, login_payload, _h = _json(
        client,
        "post",
        "/auth/login",
        json={"email": "seen@example.com", "password": PASSWORD},
    )
    token = str(login_payload["data"]["accessToken"])
    before = _rows(url, "SELECT last_seen_at, revoked_at FROM auth_sessions")[0]
    me_status, me_payload, _me_headers = _json(
        client,
        "get",
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me_status == 200
    assert me_payload["data"]["email"] == "seen@example.com"
    after_me = _rows(url, "SELECT last_seen_at, revoked_at FROM auth_sessions")[0]
    assert str(after_me["last_seen_at"]) >= str(before["last_seen_at"])
    assert after_me["revoked_at"] is None

    out_status, out_payload, _out_h = _json(
        client,
        "post",
        "/auth/logout",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert out_status == 200
    assert out_payload["ok"] is True
    revoked = _rows(url, "SELECT revoked_at FROM auth_sessions")[0]
    assert revoked["revoked_at"] is not None

    denied_status, denied_payload, _denied_h = _json(
        client,
        "get",
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert denied_status == 401
    assert denied_payload["error"]["code"] == "AUTH_UNAUTHORIZED"


def test_me_without_token_is_unauthorized(auth_env: tuple[Any, Any, str]) -> None:
    client, _app, _url = auth_env
    status, payload, _headers = _json(client, "get", "/auth/me")
    assert status == 401
    assert payload["ok"] is False
    assert payload["error"]["code"] == "AUTH_UNAUTHORIZED"
    assert payload["meta"]["requestId"]


def test_cors_allows_local_frontend(auth_env: tuple[Any, Any, str]) -> None:
    client, _app, _url = auth_env
    response: Any = client.options(
        "/auth/login",
        headers={
            "Origin": "http://127.0.0.1:5173",
            "Access-Control-Request-Method": "POST",
        },
    )
    assert response.headers.get("access-control-allow-origin") == "http://127.0.0.1:5173"
