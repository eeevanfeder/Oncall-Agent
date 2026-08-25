import { readFileSync, readdirSync, statSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { describe, expect, it } from "vitest";

import { SSE_EVENT_TYPES, type SseEvent } from "@super-ai/api-contracts";

import { createSseParser } from "../src/api/sseClient";

const frontendRoot = dirname(fileURLToPath(new URL("../package.json", import.meta.url)));

function walk(root: string): string[] {
  const files: string[] = [];
  for (const name of readdirSync(root)) {
    const full = join(root, name);
    if (statSync(full).isDirectory()) {
      files.push(...walk(full));
    } else {
      files.push(full);
    }
  }
  return files;
}

function frame(event: SseEvent): string {
  return `id: ${event.id}\nevent: ${event.type}\ndata: ${JSON.stringify(event)}\n\n`;
}

describe("sseClient parser", () => {
  it("跨 chunk 还原完整事件", () => {
    const event: SseEvent = {
      id: "1",
      type: "content.delta",
      channel: "chat",
      timestamp: "2026-08-25T00:00:00.000Z",
      text: "你好",
    };
    const raw = frame(event);
    const mid = Math.floor(raw.length / 2);
    const parser = createSseParser();
    expect(parser.push(raw.slice(0, mid))).toEqual([]);
    expect(parser.push(raw.slice(mid))).toEqual([event]);
  });

  it("覆盖合同全部事件 type", () => {
    expect(SSE_EVENT_TYPES).toHaveLength(8);
  });

  it("前端不得定义私有 SSE event union", () => {
    const srcRoot = resolve(frontendRoot, "src");
    const offenders: string[] = [];
    for (const file of walk(srcRoot)) {
      if (!file.endsWith(".ts") && !file.endsWith(".vue")) {
        continue;
      }
      const text = readFileSync(file, "utf8");
      const definesUnion =
        /export type\s+\w*Sse\w*\s*=/.test(text) && !file.includes(`${join("api", "sseClient")}`);
      const copiesCatalog = text.includes('"content.delta"') && text.includes('"tool.call"');
      if (definesUnion || copiesCatalog) {
        offenders.push(file);
      }
    }
    expect(offenders).toEqual([]);
  });
});
