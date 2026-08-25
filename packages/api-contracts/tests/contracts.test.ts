import { readFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { describe, expect, it } from "vitest";

import {
  ERROR_CATALOG,
  OPENAPI_PATHS,
  SSE_EVENT_TYPES,
  getErrorDefinition,
  isFailureEnvelope,
  isSuccessEnvelope,
  type ApiErrorBody,
  type FailureEnvelope,
  type HealthData,
  type SseEvent,
  type SuccessEnvelope,
  type ToolCallEvent,
} from "../src/index";

const root = dirname(fileURLToPath(new URL("../package.json", import.meta.url)));

function readJson(relpath: string): unknown {
  return JSON.parse(readFileSync(resolve(root, relpath), "utf8"));
}

const errorCatalog = readJson("catalog/errors.json") as typeof ERROR_CATALOG;
const sseTypes = readJson("catalog/sse-types.json") as string[];

function sampleError(code: keyof typeof ERROR_CATALOG, withDetails: boolean): ApiErrorBody {
  const def = getErrorDefinition(code);
  const body: ApiErrorBody = {
    code,
    category: def.category,
    httpStatus: def.httpStatus,
    message: def.message,
  };
  if (withDetails) {
    return { ...body, details: { fields: [{ path: "body.name", message: "必填" }] } };
  }
  return body;
}

describe("四类 envelope", () => {
  it("成功 health envelope", () => {
    const envelope: SuccessEnvelope<HealthData> = {
      ok: true,
      data: { status: "ok" },
      meta: { requestId: "req-health" },
    };
    expect(isSuccessEnvelope(envelope)).toBe(true);
    expect(envelope.data.status).toBe("ok");
    expect(envelope.meta.requestId).toBe("req-health");
  });

  it("成功通用 data envelope", () => {
    const envelope: SuccessEnvelope<{ name: string }> = {
      ok: true,
      data: { name: "demo" },
      meta: { requestId: "req-ok" },
    };
    expect(isSuccessEnvelope(envelope)).toBe(true);
    expect("error" in envelope).toBe(false);
  });

  it("失败 envelope 含 details", () => {
    const envelope: FailureEnvelope = {
      ok: false,
      error: sampleError("VALIDATION_INVALID_INPUT", true),
      meta: { requestId: "req-val" },
    };
    expect(isFailureEnvelope(envelope)).toBe(true);
    expect(envelope.error.details).toBeDefined();
  });

  it("失败 envelope 省略 details", () => {
    const envelope: FailureEnvelope = {
      ok: false,
      error: sampleError("SYSTEM_INTERNAL_ERROR", false),
      meta: { requestId: "req-sys" },
    };
    expect(isFailureEnvelope(envelope)).toBe(true);
    expect(envelope.error.details).toBeUndefined();
    expect(envelope.error.code).toBe("SYSTEM_INTERNAL_ERROR");
  });
});

describe("错误目录与 SSE", () => {
  it("TS 目录与 JSON 一致且含四类前缀", () => {
    expect(ERROR_CATALOG).toEqual(errorCatalog);
    const codes = Object.keys(ERROR_CATALOG);
    expect(codes.some((code) => code.startsWith("AUTH_"))).toBe(true);
    expect(codes.some((code) => code.startsWith("BUSINESS_"))).toBe(true);
    expect(codes.some((code) => code.startsWith("VALIDATION_"))).toBe(true);
    expect(codes.some((code) => code.startsWith("SYSTEM_"))).toBe(true);
  });

  it("SSE 目录恰好八种 type", () => {
    expect([...SSE_EVENT_TYPES]).toEqual(sseTypes);
    expect(SSE_EVENT_TYPES).toHaveLength(8);
  });

  it("tool.call 四阶段与错误复用", () => {
    const shared: ApiErrorBody = sampleError("BUSINESS_NOT_FOUND", false);
    const phases: ToolCallEvent["phase"][] = ["started", "delta", "completed", "failed"];
    const events: ToolCallEvent[] = phases.map((phase) => {
      const base: ToolCallEvent = {
        id: `evt-${phase}`,
        type: "tool.call",
        channel: "chat",
        timestamp: "2026-08-25T00:00:00.000Z",
        toolCallId: "call-1",
        phase,
      };
      if (phase === "failed") {
        return { ...base, error: shared };
      }
      return base;
    });
    expect(new Set(events.map((event) => event.phase)).size).toBe(4);
    const failed = events.find((event) => event.phase === "failed");
    expect(failed?.error).toEqual(shared);
  });

  it("SSE error 复用 HTTP error 结构", () => {
    const error = sampleError("AUTH_UNAUTHORIZED", true);
    const event: SseEvent = {
      id: "evt-err",
      type: "error",
      channel: "aiops",
      timestamp: "2026-08-25T00:00:00.000Z",
      error,
    };
    expect(event.type).toBe("error");
    if (event.type === "error") {
      expect(Object.keys(event.error).sort()).toEqual(
        ["category", "code", "details", "httpStatus", "message"].sort(),
      );
    }
  });
});

describe("OpenAPI", () => {
  it("覆盖 health 与认证 path", () => {
    const document = readJson("openapi/openapi.json") as { paths: Record<string, unknown> };
    expect(Object.keys(document.paths).sort()).toEqual(
      ["/auth/login", "/auth/logout", "/auth/me", "/auth/register", "/health"].sort(),
    );
    expect([...OPENAPI_PATHS].sort()).toEqual(Object.keys(document.paths).sort());
  });
});

