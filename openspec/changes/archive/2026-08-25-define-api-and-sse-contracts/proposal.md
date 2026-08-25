## Why

骨架已经能跑 `/health`，但 HTTP 与 SSE 还没有单一合同。若不现在锁定 envelope、错误码、OpenAPI 组织和 SSE 判别联合，后续聊天与 AIOps 会各自发明 payload，前后端无法对齐，也难以做安全默认消息。

## What Changes

- 让 `packages/api-contracts` 成为 HTTP 响应、错误码、OpenAPI path 与 SSE event 的单一事实来源。
- 定义成功 / 失败 envelope，以及 `AUTH_*`、`BUSINESS_*`、`VALIDATION_*`、`SYSTEM_*` 稳定错误目录。
- FastAPI 增加统一 success/error helper、校验与异常处理和 `X-Request-ID` 透传或生成。
- **BREAKING**：`/health` 改为成功 envelope，data 仍为 `{status:"ok"}`。
- 定义判别联合 SSE 事件与 tool.call 生命周期；SSE error 复用 HTTP 错误结构。
- 建立机器可读 OpenAPI 组织方式，当前只覆盖 foundation/health。
- 前端 typed `apiClient` / `sseClient`：解 envelope、request id / bearer 扩展点、跨 chunk SSE frame；禁止私有 event union。
- 合同测试证明后端 Pydantic 序列化形状与 TypeScript 合同一致。后端不直接导入 TypeScript。

## Capabilities

### New Capabilities

- `http-envelope`：成功/失败 envelope、错误目录、request id 与校验错误字段路径。
- `sse-events`：SSE 公共字段、全事件目录、tool 生命周期与错误复用。
- `openapi-source`：机器可读 OpenAPI 组织与 health 合同；后续提案必须先补合同再加 endpoint。
- `contract-clients`：前端 apiClient/sseClient 与禁止临时 payload 的约束。

### Modified Capabilities

- `monorepo-foundation`：`/health` 必须返回成功 envelope，而不是裸 `{status:"ok"}`。

## Impact

- 影响 `packages/api-contracts`、后端应用工厂/异常处理、前端 transport、合同测试与 `AGENTS.md`。
- 不实现认证、聊天、知识库、AIOps、MCP 运行时；只预留 bearer 与 SSE channel。
- 后续功能只能扩展合同，不能自造临时 payload。
