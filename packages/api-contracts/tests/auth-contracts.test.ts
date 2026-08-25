import { readFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { describe, expect, it } from "vitest";

import {
  ERROR_CATALOG,
  OPENAPI_PATHS,
  getErrorDefinition,
  type AuthLoginRequest,
  type AuthLoginResponse,
  type AuthRegisterRequest,
  type AuthUser,
} from "../src/index";

const root = dirname(fileURLToPath(new URL("../package.json", import.meta.url)));

function readJson(relpath: string): unknown {
  return JSON.parse(readFileSync(resolve(root, relpath), "utf8"));
}

describe("认证合同", () => {
  it("登记 AUTH_INVALID_CREDENTIALS 为 401", () => {
    const catalog = readJson("catalog/errors.json") as typeof ERROR_CATALOG;
    expect(ERROR_CATALOG.AUTH_INVALID_CREDENTIALS).toEqual({
      category: "auth",
      httpStatus: 401,
      message: "邮箱或密码不正确",
    });
    expect(catalog.AUTH_INVALID_CREDENTIALS).toEqual(ERROR_CATALOG.AUTH_INVALID_CREDENTIALS);
    expect(getErrorDefinition("AUTH_UNAUTHORIZED").httpStatus).toBe(401);
  });

  it("OpenAPI 含认证 path、DTO 与 bearer", () => {
    const document = readJson("openapi/openapi.json") as {
      paths: Record<string, { post?: { security?: unknown[] }; get?: { security?: unknown[] } }>;
      components: { securitySchemes?: { bearerAuth?: { type: string; scheme: string } } };
    };
    expect(Object.keys(document.paths).sort()).toEqual(
      ["/auth/login", "/auth/logout", "/auth/me", "/auth/register", "/health"].sort(),
    );
    expect([...OPENAPI_PATHS].sort()).toEqual(
      ["/auth/login", "/auth/logout", "/auth/me", "/auth/register", "/health"].sort(),
    );
    expect(document.components.securitySchemes?.bearerAuth).toEqual({
      type: "http",
      scheme: "bearer",
    });
    expect(document.paths["/auth/me"]?.get?.security).toEqual([{ bearerAuth: [] }]);
    expect(document.paths["/auth/logout"]?.post?.security).toEqual([{ bearerAuth: [] }]);
  });

  it("Auth DTO 形状可用", () => {
    const register: AuthRegisterRequest = { email: "User@Example.com", password: "secret-pass" };
    const login: AuthLoginRequest = { email: "user@example.com", password: "secret-pass" };
    const user: AuthUser = {
      id: "11111111-1111-4111-8111-111111111111",
      email: "user@example.com",
      createdAt: "2026-08-25T00:00:00.000Z",
    };
    const session: AuthLoginResponse = { accessToken: "opaque-token", user };
    expect(register.email).toContain("@");
    expect(login.password.length).toBeGreaterThan(0);
    expect(session.user.email).toBe(user.email);
    expect(session.accessToken).toBe("opaque-token");
  });
});
