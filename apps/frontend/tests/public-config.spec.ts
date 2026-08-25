import { mkdtempSync, readFileSync, readdirSync, statSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { build } from "vite";
import { describe, expect, it } from "vitest";

import {
  extractPublicFrontendConfig,
  loadMergedConfig,
  type JsonObject,
} from "../config-loader";

const frontendRoot = dirname(fileURLToPath(new URL("../package.json", import.meta.url)));

const SENTINELS = {
  llm: "SENTINEL_LLM_SECRET_9f3a",
  cls: "SENTINEL_CLS_SECRET_2c1b",
  mcp: "SENTINEL_MCP_SECRET_7d4e",
  minio: "SENTINEL_MINIO_SECRET_5a8c",
};

function writeTempConfig(): string {
  const dir = mkdtempSync(join(tmpdir(), "super-ai-config-"));
  const project: JsonObject = {
    frontend: {
      title: "Public Title",
      apiBaseUrl: "https://api.example.test",
      analytics: { publicKey: "pk_public_only" },
    },
    llm: { apiKey: SENTINELS.llm, password: SENTINELS.llm },
    cls: { secret: SENTINELS.cls },
    mcp: { token: SENTINELS.mcp, secret: SENTINELS.mcp },
    minio: { secretKey: SENTINELS.minio, password: SENTINELS.minio },
  };
  writeFileSync(join(dir, "project.json"), JSON.stringify(project));
  writeFileSync(join(dir, "user.project.json"), "{}");
  return dir;
}

function walkFiles(root: string): string[] {
  const files: string[] = [];
  for (const name of readdirSync(root)) {
    const full = join(root, name);
    if (statSync(full).isDirectory()) {
      files.push(...walkFiles(full));
    } else {
      files.push(full);
    }
  }
  return files;
}

describe("public frontend config allowlist", () => {
  it("只暴露 allowlist 字段", () => {
    const dir = writeTempConfig();
    const publicConfig = extractPublicFrontendConfig(loadMergedConfig(dir));
    expect(publicConfig).toEqual({
      title: "Public Title",
      apiBaseUrl: "https://api.example.test",
      analyticsPublicKey: "pk_public_only",
    });
    expect(JSON.stringify(publicConfig)).not.toContain(SENTINELS.llm);
  });

  it("src 运行时代码不得 import 完整 JSON", () => {
    const srcRoot = resolve(frontendRoot, "src");
    const offenders: string[] = [];
    for (const file of walkFiles(srcRoot)) {
      if (!file.endsWith(".ts") && !file.endsWith(".vue")) {
        continue;
      }
      const text = readFileSync(file, "utf8");
      if (
        text.includes("project.json") ||
        text.includes("user.project.json") ||
        /from\s+['"][^'"]+\.json['"]/.test(text) ||
        /import\s+['"][^'"]+\.json['"]/.test(text)
      ) {
        offenders.push(file);
      }
    }
    expect(offenders).toEqual([]);
  });

  it("build 产物不含 LLM/CLS/MCP/MinIO sentinel", async () => {
    const dir = writeTempConfig();
    const publicConfig = extractPublicFrontendConfig(loadMergedConfig(dir));
    const outDir = mkdtempSync(join(tmpdir(), "super-ai-dist-"));

    await build({
      configFile: false,
      root: frontendRoot,
      plugins: [(await import("@vitejs/plugin-vue")).default()],
      define: {
        __SUPER_AI_PUBLIC_CONFIG__: JSON.stringify(publicConfig),
      },
      build: {
        outDir,
        emptyOutDir: true,
      },
    });

    const bundle = walkFiles(outDir)
      .map((file) => readFileSync(file, "utf8"))
      .join("\n");
    expect(bundle).toContain("Public Title");
    expect(bundle).not.toContain(SENTINELS.llm);
    expect(bundle).not.toContain(SENTINELS.cls);
    expect(bundle).not.toContain(SENTINELS.mcp);
    expect(bundle).not.toContain(SENTINELS.minio);
  });
});
