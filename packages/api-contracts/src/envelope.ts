export type RequestMeta = {
  requestId: string;
};

export type SuccessEnvelope<T> = {
  ok: true;
  data: T;
  meta: RequestMeta;
};

export type ApiErrorBody = {
  code: string;
  category: "auth" | "business" | "validation" | "system";
  httpStatus: number;
  message: string;
  details?: Record<string, unknown>;
};

export type FailureEnvelope = {
  ok: false;
  error: ApiErrorBody;
  meta: RequestMeta;
};

export type ApiEnvelope<T> = SuccessEnvelope<T> | FailureEnvelope;

export function isSuccessEnvelope<T>(value: unknown): value is SuccessEnvelope<T> {
  return typeof value === "object" && value !== null && (value as SuccessEnvelope<T>).ok === true;
}

export function isFailureEnvelope(value: unknown): value is FailureEnvelope {
  return typeof value === "object" && value !== null && (value as FailureEnvelope).ok === false;
}
