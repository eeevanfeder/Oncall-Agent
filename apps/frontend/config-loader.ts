import { readFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

export type JsonObject = Record<string, unknown>;

export type PublicFrontendConfig = {
  title: string;
  apiBaseUrl: string;
  analyticsPublicKey: string;
};

const frontendRoot = dirname(fileURLToPath(import.meta.url));
const defaultConfigDir = resolve(frontendRoot, "../../config");

function isRecord(value: unknown): value is JsonObject {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

export function deepMerge(base: JsonObject, override: JsonObject): JsonObject {
  const merged: JsonObject = { ...base };
  for (const [key, value] of Object.entries(override)) {
    const existing = merged[key];
    if (isRecord(existing) && isRecord(value)) {
      merged[key] = deepMerge(existing, value);
    } else {
      merged[key] = value;
    }
  }
  return merged;
}

function readObject(path: string): JsonObject {
  try {
    const raw: unknown = JSON.parse(readFileSync(path, "utf8"));
    return isRecord(raw) ? raw : {};
  } catch {
    return {};
  }
}

export function loadMergedConfig(configDir: string = defaultConfigDir): JsonObject {
  return deepMerge(
    readObject(resolve(configDir, "project.json")),
    readObject(resolve(configDir, "user.project.json")),
  );
}

export function extractPublicFrontendConfig(merged: JsonObject): PublicFrontendConfig {
  const frontend = isRecord(merged.frontend) ? merged.frontend : {};
  const analytics = isRecord(frontend.analytics) ? frontend.analytics : {};
  return {
    title: typeof frontend.title === "string" ? frontend.title : "",
    apiBaseUrl: typeof frontend.apiBaseUrl === "string" ? frontend.apiBaseUrl : "",
    analyticsPublicKey: typeof analytics.publicKey === "string" ? analytics.publicKey : "",
  };
}
