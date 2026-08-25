/** @vitest-environment jsdom */

import { createPinia, setActivePinia } from "pinia";
import { beforeEach, describe, expect, it } from "vitest";

import { ContractApiError } from "../src/api/apiClient";
import { AUTH_TOKEN_STORAGE_KEY, createAuthClient } from "../src/api/authClient";
import { useAuthStore } from "../src/stores/auth";

const user = {
  id: "11111111-1111-4111-8111-111111111111",
  email: "user@example.com",
  createdAt: "2026-08-25T00:00:00.000Z",
};

function envelope<T>(data: T, status = 200): Response {
  return new Response(
    JSON.stringify({ ok: true, data, meta: { requestId: "rid-1" } }),
    { status, headers: { "Content-Type": "application/json" } },
  );
}

function failure(code: string, status: number): Response {
  return new Response(
    JSON.stringify({
      ok: false,
      error: { code, category: "auth", httpStatus: status, message: "denied" },
      meta: { requestId: "rid-err" },
    }),
    { status, headers: { "Content-Type": "application/json" } },
  );
}

describe("authClient 与 auth store", () => {
  beforeEach(() => {
    setActivePinia(createPinia());
    localStorage.clear();
  });

  it("登录只把 access token 写入 localStorage", async () => {
    const seen: string[] = [];
    const client = createAuthClient({
      baseUrl: "https://api.example.test",
      getAccessToken: () => localStorage.getItem(AUTH_TOKEN_STORAGE_KEY) ?? undefined,
      fetch: async (input, init) => {
        seen.push(`${init?.method ?? "GET"} ${String(input)}`);
        const body = JSON.parse(String(init?.body ?? "{}")) as { password?: string };
        expect(body.password).toBe("secret-pass-12");
        return envelope({ accessToken: "opaque-token", user });
      },
    });
    const store = useAuthStore();
    store.bindClient(client);
    await store.login({ email: "user@example.com", password: "secret-pass-12" });
    expect(localStorage.getItem(AUTH_TOKEN_STORAGE_KEY)).toBe("opaque-token");
    expect(JSON.stringify(localStorage)).not.toContain("secret-pass-12");
    expect(store.user?.email).toBe("user@example.com");
    expect(seen[0]).toContain("/auth/login");
  });

  it("initialize 在有 token 时调用 /auth/me", async () => {
    localStorage.setItem(AUTH_TOKEN_STORAGE_KEY, "stored-token");
    const seen: string[] = [];
    const client = createAuthClient({
      baseUrl: "https://api.example.test",
      getAccessToken: () => localStorage.getItem(AUTH_TOKEN_STORAGE_KEY) ?? undefined,
      fetch: async (input, init) => {
        const headers = new Headers(init?.headers);
        seen.push(`${String(input)} ${headers.get("Authorization") ?? ""}`);
        return envelope(user);
      },
    });
    const store = useAuthStore();
    store.bindClient(client);
    await store.initialize();
    expect(seen[0]).toBe("https://api.example.test/auth/me Bearer stored-token");
    expect(store.user).toEqual(user);
  });

  it("失效 me 与 logout 清理本地且不删除服务端业务数据", async () => {
    localStorage.setItem(AUTH_TOKEN_STORAGE_KEY, "dead-token");
    const seen: string[] = [];
    const client = createAuthClient({
      baseUrl: "https://api.example.test",
      getAccessToken: () => localStorage.getItem(AUTH_TOKEN_STORAGE_KEY) ?? undefined,
      fetch: async (input, init) => {
        seen.push(`${init?.method ?? "GET"} ${String(input)}`);
        if (String(input).endsWith("/auth/me")) {
          return failure("AUTH_UNAUTHORIZED", 401);
        }
        return envelope({});
      },
    });
    const store = useAuthStore();
    store.bindClient(client);
    await store.initialize();
    expect(localStorage.getItem(AUTH_TOKEN_STORAGE_KEY)).toBeNull();
    expect(store.user).toBeUndefined();

    localStorage.setItem(AUTH_TOKEN_STORAGE_KEY, "live-token");
    store.user = user;
    await store.logout();
    expect(localStorage.getItem(AUTH_TOKEN_STORAGE_KEY)).toBeNull();
    expect(store.user).toBeUndefined();
    expect(seen.some((item) => item.includes("/auth/logout"))).toBe(true);
    expect(seen.some((item) => /DELETE .*\/(users|auth)/.test(item))).toBe(false);
  });

  it("authClient 失败时抛出合同 error", async () => {
    const client = createAuthClient({
      baseUrl: "https://api.example.test",
      fetch: async () => failure("AUTH_INVALID_CREDENTIALS", 401),
    });
    await expect(client.login({ email: "a@b.c", password: "x" })).rejects.toBeInstanceOf(
      ContractApiError,
    );
  });
});
