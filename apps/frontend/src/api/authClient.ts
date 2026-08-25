import {
  type AuthLoginRequest,
  type AuthLoginResponse,
  type AuthLogoutResponse,
  type AuthRegisterRequest,
  type AuthUser,
} from "@super-ai/api-contracts";

import { createApiClient, type ApiClientOptions } from "./apiClient";

export const AUTH_TOKEN_STORAGE_KEY = "super-ai.accessToken";

function jsonInit(method: string, body: unknown): RequestInit {
  return {
    method,
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  };
}

export function createAuthClient(options: ApiClientOptions) {
  const api = createApiClient(options);
  return {
    register(body: AuthRegisterRequest) {
      return api.request<AuthUser>("/auth/register", jsonInit("POST", body));
    },
    login(body: AuthLoginRequest) {
      return api.request<AuthLoginResponse>("/auth/login", jsonInit("POST", body));
    },
    logout() {
      return api.request<AuthLogoutResponse>("/auth/logout", { method: "POST" });
    },
    me() {
      return api.request<AuthUser>("/auth/me");
    },
  };
}

export type AuthClient = ReturnType<typeof createAuthClient>;
