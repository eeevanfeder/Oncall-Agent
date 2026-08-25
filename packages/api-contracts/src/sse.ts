import type { ApiErrorBody } from "./envelope";

export type SseChannel = "chat" | "aiops";

export type SseEventType =
  | "content.delta"
  | "reasoning.delta"
  | "tool.call"
  | "reference.source"
  | "task.status"
  | "report"
  | "complete"
  | "error";

export type ToolCallPhase = "started" | "delta" | "completed" | "failed";

export type SseBase<T extends SseEventType> = {
  id: string;
  type: T;
  channel: SseChannel;
  timestamp: string;
};

export type ContentDeltaEvent = SseBase<"content.delta"> & {
  text: string;
};

export type ReasoningDeltaEvent = SseBase<"reasoning.delta"> & {
  text: string;
};

export type ToolCallEvent = SseBase<"tool.call"> & {
  toolCallId: string;
  phase: ToolCallPhase;
  name?: string;
  argumentsDelta?: string;
  result?: unknown;
  error?: ApiErrorBody;
};

export type ReferenceSourceEvent = SseBase<"reference.source"> & {
  sourceId: string;
  title?: string;
  uri?: string;
};

export type TaskStatusEvent = SseBase<"task.status"> & {
  taskId: string;
  status: string;
};

export type ReportEvent = SseBase<"report"> & {
  title?: string;
  body: string;
};

export type CompleteEvent = SseBase<"complete"> & {
  reason?: string;
};

export type SseErrorEvent = SseBase<"error"> & {
  error: ApiErrorBody;
};

export type SseEvent =
  | ContentDeltaEvent
  | ReasoningDeltaEvent
  | ToolCallEvent
  | ReferenceSourceEvent
  | TaskStatusEvent
  | ReportEvent
  | CompleteEvent
  | SseErrorEvent;

export const SSE_EVENT_TYPES: readonly SseEventType[] = [
  "content.delta",
  "reasoning.delta",
  "tool.call",
  "reference.source",
  "task.status",
  "report",
  "complete",
  "error",
] as const;
