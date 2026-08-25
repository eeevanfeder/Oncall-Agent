export {
  FOUNDATION_CONTRACT_VERSION,
  type HealthData,
  type HealthStatus,
} from "./foundation";

export {
  isFailureEnvelope,
  isSuccessEnvelope,
  type ApiEnvelope,
  type ApiErrorBody,
  type FailureEnvelope,
  type RequestMeta,
  type SuccessEnvelope,
} from "./envelope";

export { ERROR_CATALOG, getErrorDefinition, type ErrorCategory, type ErrorCode, type ErrorDefinition } from "./errors";

export {
  SSE_EVENT_TYPES,
  type CompleteEvent,
  type ContentDeltaEvent,
  type ReasoningDeltaEvent,
  type ReferenceSourceEvent,
  type ReportEvent,
  type SseChannel,
  type SseErrorEvent,
  type SseEvent,
  type SseEventType,
  type TaskStatusEvent,
  type ToolCallEvent,
  type ToolCallPhase,
} from "./sse";

export { OPENAPI_PATHS } from "./openapi";

export type {
  AuthLoginRequest,
  AuthLoginResponse,
  AuthLogoutResponse,
  AuthRegisterRequest,
  AuthUser,
} from "./auth";
