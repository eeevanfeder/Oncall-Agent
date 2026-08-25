## Context

P01 已归档。后端 `/health` 仍返回裸对象，合同包只有 foundation 类型。动机见 `proposal.md`。本提案把 HTTP/SSE/OpenAPI 收口到 `packages/api-contracts`，后端用 Pydantic 镜像形状，前端只消费合同导出。

## Goals / Non-Goals

**Goals:**

- 合同包导出 envelope、错误目录、SSE 判别联合与机器可读 OpenAPI。
- FastAPI 统一 helper / handler / request id，health 走成功 envelope。
- 前端 apiClient/sseClient 解包并对齐合同；跨 chunk 解析 SSE。
- 用 JSON 目录做跨语言形状测试，后端不 import TypeScript。

**Non-Goals:**

- 不实现登录、聊天流、AIOps、真实 MCP。
- 不把 OpenAPI 扩到未立项业务 path。
- 不引入第二套错误码或前端私有 event union。

## Decisions

### 决策：TypeScript 类型 + JSON 目录双导出

合同包同时提供：

- TypeScript 类型与 const（给前端与测试）
- `packages/api-contracts/catalog/*.json`（错误目录、SSE type、envelope 字段）
- `packages/api-contracts/openapi/openapi.json`（机器可读 HTTP 合同）

后端测试读取 JSON，对照 Pydantic `model_dump(mode="json")`。备选：从 OpenAPI 生成 Python。否决：本提案只要形状证明，不引入代码生成链。

### 决策：错误目录前缀稳定、业务可追加

预置：

- `AUTH_UNAUTHORIZED` 401、`AUTH_FORBIDDEN` 403
- `BUSINESS_NOT_FOUND` 404、`BUSINESS_CONFLICT` 409
- `VALIDATION_INVALID_INPUT` 422
- `SYSTEM_INTERNAL_ERROR` 500、`SYSTEM_UNAVAILABLE` 503

校验失败统一 `VALIDATION_INVALID_INPUT`，`details.fields` 为 `{path,message}[]`。后续只能追加 code，不能改已发布 code 的 category/status。

### 决策：Request ID

中间件读取 `X-Request-ID`，缺则生成 UUID4。写入 `request.state`、响应头与 envelope `meta.requestId`。不从 OS 环境变量读业务配置。

### 决策：SSE 帧格式

标准 SSE：`id:` / `event:` / `data:` JSON 一行，空行结束。`event` 等于合同 `type`。parser 以 `\n\n` 为帧边界，缓存未完成 chunk。`sseClient` 只 import 合同联合类型。

### 决策：health 走 helper

`create_app` 注册 exception handler 与 request-id 中间件。`/health` 调用 `success({"status":"ok"})`。增加仅测试用的校验路由（例如 `/__contract__/echo`）以覆盖 validation 路径，不写入 OpenAPI 公开合同。

### 决策：前端依赖 workspace 合同

`@super-ai/frontend` 依赖 `file:` workspace `@super-ai/api-contracts`。apiClient 接受 `getAccessToken` / `getRequestId` 钩子。

## Risks / Trade-offs

- [测试路由泄漏到生产] → 仅在测试通过依赖注入注册，或路径以 `/__contract__` 开头且不进 OpenAPI。
- [JSON 目录与 TS 漂移] → 合同包测试断言 TS const 与 JSON 一致。
- [health 破坏旧客户端] → 仓库尚无外部消费者；文档标明 BREAKING。

## Migration Plan

更新后端 health 测试与前端若有硬编码。无数据迁移。回滚即恢复裸 health 对象。
