import type { SseEvent } from "@super-ai/api-contracts";

export type SseParser = {
  push: (chunk: string) => SseEvent[];
};

function parseFrame(raw: string): SseEvent | undefined {
  const lines = raw.replace(/\r\n/g, "\n").split("\n");
  const dataLines: string[] = [];
  for (const line of lines) {
    if (line.startsWith("data:")) {
      dataLines.push(line.slice(5).trimStart());
    }
  }
  if (dataLines.length === 0) {
    return undefined;
  }
  const parsed: unknown = JSON.parse(dataLines.join("\n"));
  return parsed as SseEvent;
}

export function createSseParser(): SseParser {
  let buffer = "";
  return {
    push(chunk: string): SseEvent[] {
      buffer += chunk;
      const events: SseEvent[] = [];
      const normalized = buffer.replace(/\r\n/g, "\n");
      const parts = normalized.split("\n\n");
      buffer = parts.pop() ?? "";
      for (const frame of parts) {
        const event = parseFrame(frame);
        if (event !== undefined) {
          events.push(event);
        }
      }
      return events;
    },
  };
}

export function createSseClient(options: { parser?: SseParser } = {}) {
  const parser = options.parser ?? createSseParser();
  return {
    ingest(chunk: string): SseEvent[] {
      return parser.push(chunk);
    },
  };
}
