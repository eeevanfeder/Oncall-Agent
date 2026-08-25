from __future__ import annotations

from typing import Any

from super_ai.contracts.catalog import error_catalog
from super_ai.http.models import ApiErrorBody, FailureEnvelope, RequestMeta, SuccessEnvelope


def lookup_error(code: str) -> dict[str, Any]:
    catalog = error_catalog()
    definition = catalog.get(code)
    if not isinstance(definition, dict):
        definition = catalog["SYSTEM_INTERNAL_ERROR"]
        code = "SYSTEM_INTERNAL_ERROR"
    return {
        "code": code,
        "category": definition["category"],
        "httpStatus": definition["httpStatus"],
        "message": definition["message"],
    }


def success(data: Any, request_id: str) -> dict[str, Any]:
    return SuccessEnvelope(data=data, meta=RequestMeta(requestId=request_id)).model_dump(
        mode="json"
    )


def failure(
    code: str,
    request_id: str,
    *,
    details: dict[str, Any] | None = None,
    message: str | None = None,
) -> dict[str, Any]:
    spec = lookup_error(code)
    error = ApiErrorBody(
        code=str(spec["code"]),
        category=str(spec["category"]),
        httpStatus=int(spec["httpStatus"]),
        message=message if message is not None else str(spec["message"]),
        details=details,
    )
    return FailureEnvelope(error=error, meta=RequestMeta(requestId=request_id)).model_dump(
        mode="json",
        exclude_none=True,
    )
