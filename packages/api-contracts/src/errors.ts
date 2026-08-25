export type ErrorCategory = "auth" | "business" | "validation" | "system";

export type ErrorDefinition = {
  category: ErrorCategory;
  httpStatus: number;
  message: string;
};

export const ERROR_CATALOG = {
  AUTH_UNAUTHORIZED: { category: "auth", httpStatus: 401, message: "未认证" },
  AUTH_INVALID_CREDENTIALS: { category: "auth", httpStatus: 401, message: "邮箱或密码不正确" },
  AUTH_FORBIDDEN: { category: "auth", httpStatus: 403, message: "无权限" },
  BUSINESS_NOT_FOUND: { category: "business", httpStatus: 404, message: "资源不存在" },
  BUSINESS_CONFLICT: { category: "business", httpStatus: 409, message: "资源冲突" },
  VALIDATION_INVALID_INPUT: { category: "validation", httpStatus: 422, message: "请求校验失败" },
  SYSTEM_INTERNAL_ERROR: { category: "system", httpStatus: 500, message: "服务内部错误" },
  SYSTEM_UNAVAILABLE: { category: "system", httpStatus: 503, message: "服务暂不可用" },
} as const;

export type ErrorCode = keyof typeof ERROR_CATALOG;

export function getErrorDefinition(code: ErrorCode): ErrorDefinition {
  return ERROR_CATALOG[code];
}
