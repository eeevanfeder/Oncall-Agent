import { type AuthLoginRequest, type AuthUser } from "@super-ai/api-contracts";
import { defineStore } from "pinia";
import { ref } from "vue";

import { AUTH_TOKEN_STORAGE_KEY, type AuthClient } from "../api/authClient";

export const useAuthStore = defineStore("auth", () => {
  const user = ref<AuthUser | undefined>();
  let client: AuthClient | undefined;

  function bindClient(next: AuthClient): void {
    client = next;
  }

  function requireClient(): AuthClient {
    if (client === undefined) {
      throw new Error("authClient 未绑定");
    }
    return client;
  }

  function persistToken(token: string | undefined): void {
    if (token === undefined || token === "") {
      localStorage.removeItem(AUTH_TOKEN_STORAGE_KEY);
      return;
    }
    localStorage.setItem(AUTH_TOKEN_STORAGE_KEY, token);
  }

  function clearLocalAuth(): void {
    persistToken(undefined);
    user.value = undefined;
  }

  async function initialize(): Promise<void> {
    const token = localStorage.getItem(AUTH_TOKEN_STORAGE_KEY);
    if (token === null || token === "") {
      return;
    }
    try {
      const result = await requireClient().me();
      user.value = result.data;
    } catch {
      clearLocalAuth();
    }
  }

  async function login(body: AuthLoginRequest): Promise<void> {
    const result = await requireClient().login(body);
    persistToken(result.data.accessToken);
    user.value = result.data.user;
  }

  async function logout(): Promise<void> {
    try {
      await requireClient().logout();
    } finally {
      clearLocalAuth();
    }
  }

  return { user, bindClient, initialize, login, logout, clearLocalAuth };
});
