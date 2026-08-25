## Why

桌面 Web 需要可恢复的登录会话，才能继续做 Chat 与其它受保护能力。P02 已有 envelope/错误目录，P03 已有可替换 SQLite 边界，但还没有用户、会话和 bearer 认证。

## What Changes

- 新增 `users`、`auth_sessions` Alembic 迁移、owner-safe Repository、AuthService 与 FastAPI 依赖。
- 邮箱规范化且唯一；密码用 `pwdlib[argon2]` 哈希，永不保存或记录明文。
- 登录发放高熵 opaque bearer token；客户端持有 raw token，SQLite 只存 64 位 SHA-256 hash。session 记录 `createdAt`/`lastSeenAt`/`revokedAt`，登出可撤销；本版本不虚构自动过期。
- 用户不存在与密码错误都返回 `AUTH_INVALID_CREDENTIALS`；未知账号也执行 dummy Argon2，避免明显枚举/时序差异。
- API：`POST /auth/register`、`POST /auth/login`、`POST /auth/logout`、`GET /auth/me`，全部使用统一 envelope/error/requestId。
- 合同增加 Auth DTO、请求/响应、bearer security scheme 与 401 错误；CORS 允许本机前端 `127.0.0.1:5173`。
- 前端实现可复用 `authClient`/auth state：token 是唯一允许写入 localStorage 的认证凭据；`initialize` 调用 `/auth/me`；失效与 logout 只清理本地受保护 store，不得删除服务端业务数据。完整页面留给 P08。

## Capabilities

### New Capabilities

- `auth-api`：注册/登录/登出/当前用户、错误归一、CORS。
- `auth-sessions`：规范化用户、Argon2、token hash、lastSeen、撤销。
- `frontend-auth-state`：authClient、本地 token、恢复与清理。

### Modified Capabilities

- `openapi-source`：OpenAPI 增补认证 path 与 bearer。
- `repository-boundary`：允许认证仓储，其它领域 CRUD 仍禁止。
- `contract-clients`：增加真实 authClient，bearer 不再只是预留。
- `engineering-baseline`：文档可描述已实现的认证 API，但不得夸大未做的页面或其它产品能力。

## Impact

- `packages/api-contracts`、`apps/backend`（迁移、auth 域、路由、CORS）、`apps/frontend`（authClient/store）。
- 更新 `AGENTS.md`：认证已落地，完整页面仍属后续提案。
- 不实现 Chat/知识/任务/MCP/AIOps/反馈/审计，不实现登录页面。
