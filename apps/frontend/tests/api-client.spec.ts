import { describe, expect, it } from "vitest";

import { ContractApiError, createApiClient } from "../src/api/apiClient";

describe("apiClient", () => {
  it("成功时解开 data 并注入 request id 与 bearer", async () => {
    const seen: string[] = [];
    const client = createApiClient({
      baseUrl: "https://api.example.test",
      getRequestId: () => "client-rid",
      getAccessToken: () => "token-1",
      fetch: async (input, init) => {
        const headers = new Headers(init?.headers);
        seen.push(String(input), headers.get("X-Request-ID") ?? "", headers.get("Authorization") ?? "");
        return new Response(
          JSON.stringify({
            ok: true,
            data: { status: "ok" },
            meta: { requestId: "client-rid" },
          }),
          { status: 200, headers: { "Content-Type": "application/json" } },
        );
      },
    });
    const result = await client.request<{ status: string }>("/health");
    expect(result.data).toEqual({ status: "ok" });
    expect(result.requestId).toBe("client-rid");
    expect(seen[0]).toBe("https://api.example.test/health");
    expect(seen[1]).toBe("client-rid");
    expect(seen[2]).toBe("Bearer token-1");
  });

  it("失败时返回合同 error", async () => {
    const client = createApiClient({
      baseUrl: "https://api.example.test",
      fetch: async () =>
        new Response(
          JSON.stringify({
            ok: false,
            error: {
              code: "VALIDATION_INVALID_INPUT",
              category: "validation",
              httpStatus: 422,
              message: "请求校验失败",
              details: { fields: [{ path: "body.name", message: "必填" }] },
            },
            meta: { requestId: "err-1" },
          }),
          { status: 422, headers: { "Content-Type": "application/json" } },
        ),
    });
    await expect(client.request("/__contract__/echo", { method: "POST" })).rejects.toMatchObject({
      requestId: "err-1",
      error: { code: "VALIDATION_INVALID_INPUT" },
    });
    await expect(client.request("/x")).rejects.toBeInstanceOf(ContractApiError);
  });
});
