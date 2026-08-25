import {
  isFailureEnvelope,
  isSuccessEnvelope,
  type ApiErrorBody,
  type FailureEnvelope,
  type SuccessEnvelope,
} from "@super-ai/api-contracts";

export type ApiClientOptions = {
  baseUrl: string;
  fetch?: typeof fetch;
  getAccessToken?: () => string | undefined;
  getRequestId?: () => string | undefined;
};

export class ContractApiError extends Error {
  readonly error: ApiErrorBody;
  readonly requestId: string;

  constructor(error: ApiErrorBody, requestId: string) {
    super(error.message);
    this.name = "ContractApiError";
    this.error = error;
    this.requestId = requestId;
  }
}

function joinUrl(baseUrl: string, path: string): string {
  return `${baseUrl.replace(/\/$/, "")}${path.startsWith("/") ? path : `/${path}`}`;
}

export function createApiClient(options: ApiClientOptions) {
  const fetchImpl = options.fetch ?? fetch;

  return {
    async request<T>(path: string, init: RequestInit = {}): Promise<{ data: T; requestId: string }> {
      const headers = new Headers(init.headers);
      const requestId = options.getRequestId?.();
      if (requestId !== undefined && requestId !== "") {
        headers.set("X-Request-ID", requestId);
      }
      const token = options.getAccessToken?.();
      if (token !== undefined && token !== "") {
        headers.set("Authorization", `Bearer ${token}`);
      }
      const response = await fetchImpl(joinUrl(options.baseUrl, path), { ...init, headers });
      const body: unknown = await response.json();
      if (isSuccessEnvelope<T>(body)) {
        const success = body as SuccessEnvelope<T>;
        return { data: success.data, requestId: success.meta.requestId };
      }
      if (isFailureEnvelope(body)) {
        const failure = body as FailureEnvelope;
        throw new ContractApiError(failure.error, failure.meta.requestId);
      }
      throw new Error("响应不是合同 envelope");
    },
  };
}
