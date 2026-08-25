from __future__ import annotations

from typing import Any, cast

from starlette.testclient import TestClient

from super_ai.app import create_app
from super_ai.contracts.catalog import envelope_fields, error_catalog, sse_types
from super_ai.http.errors import failure, lookup_error, success
from super_ai.http.models import ApiErrorBody, SseErrorEvent, ToolCallEvent


def _request(method: str, path: str, **kwargs: Any) -> tuple[int, dict[str, Any], dict[str, str]]:
    client: Any = TestClient(create_app())
    response: Any = getattr(client, method)(path, **kwargs)
    headers = {str(key): str(value) for key, value in response.headers.items()}
    payload = cast(dict[str, Any], response.json())
    return int(response.status_code), payload, headers


def test_health_success_envelope() -> None:
    status, payload, headers = _request("get", "/health")
    assert status == 200
    assert payload["ok"] is True
    assert payload["data"] == {"status": "ok"}
    assert payload["meta"]["requestId"]
    assert headers["x-request-id"] == payload["meta"]["requestId"]


def test_request_id_passthrough() -> None:
    status, payload, headers = _request("get", "/health", headers={"X-Request-ID": "fixed-id-1"})
    assert status == 200
    assert payload["meta"]["requestId"] == "fixed-id-1"
    assert headers["x-request-id"] == "fixed-id-1"


def test_validation_error_field_paths() -> None:
    status, payload, _headers = _request("post", "/__contract__/echo", json={})
    assert status == 422
    assert payload["ok"] is False
    assert payload["error"]["code"] == "VALIDATION_INVALID_INPUT"
    fields = payload["error"]["details"]["fields"]
    paths = [item["path"] for item in fields]
    assert any("name" in path for path in paths)


def test_four_envelope_shapes_match_catalog() -> None:
    fields = envelope_fields()
    ok_health = success({"status": "ok"}, "r1")
    ok_generic = success({"name": "n"}, "r2")
    bad_details = failure("VALIDATION_INVALID_INPUT", "r3", details={"fields": []})
    bad_plain = failure("SYSTEM_INTERNAL_ERROR", "r4")
    for body in (ok_health, ok_generic):
        assert list(body.keys()) == fields["success"]
        assert list(body["meta"].keys()) == fields["meta"]
    assert list(bad_details.keys()) == fields["failure"]
    assert list(bad_plain.keys()) == fields["failure"]
    assert "details" in bad_details["error"]
    assert "details" not in bad_plain["error"]
    for key in fields["errorRequired"]:
        assert key in bad_plain["error"]


def test_backend_error_catalog_matches_contract_json() -> None:
    catalog = error_catalog()
    spec = lookup_error("AUTH_UNAUTHORIZED")
    assert spec["httpStatus"] == catalog["AUTH_UNAUTHORIZED"]["httpStatus"]
    dumped = failure("AUTH_UNAUTHORIZED", "r5")
    assert dumped["error"]["category"] == "auth"


def test_sse_models_cover_tool_lifecycle_and_error_reuse() -> None:
    types = sse_types()
    assert types == [
        "content.delta",
        "reasoning.delta",
        "tool.call",
        "reference.source",
        "task.status",
        "report",
        "complete",
        "error",
    ]
    err = ApiErrorBody(**lookup_error("BUSINESS_NOT_FOUND"))
    phases = ["started", "delta", "completed", "failed"]
    events = [
        ToolCallEvent(
            id=f"id-{phase}",
            channel="chat",
            timestamp="2026-08-25T00:00:00Z",
            toolCallId="t1",
            phase=phase,
            error=err if phase == "failed" else None,
        ).model_dump(mode="json", exclude_none=True)
        for phase in phases
    ]
    assert {event["phase"] for event in events} == set(phases)
    sse_error = SseErrorEvent(
        id="e1",
        channel="aiops",
        timestamp="2026-08-25T00:00:00Z",
        error=err,
    ).model_dump(mode="json", exclude_none=True)
    required = {"code", "category", "httpStatus", "message"}
    assert required <= set(sse_error["error"].keys())
    assert required <= set(events[-1]["error"].keys())
    assert sse_error["error"]["code"] == events[-1]["error"]["code"]
    assert sse_error["type"] == "error"
