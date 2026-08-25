## Context

P02/P03 已归档。后端有 envelope、临时 SQLite helper 与 foundation 表，没有用户。前端 `apiClient` 已预留 bearer，但没有 auth 状态。动机见 `proposal.md`。

## Goals / Non-Goals

**Goals:**

- 合同先于 endpoint：错误码、Auth DTO、OpenAPI path、bearer scheme。
- 可测试的 AuthService + owner-safe Repository；import 仍不连库。
- 前端可复用 authClient/store，完整页面不做。

**Non-Goals:**

- 不做登录/注册页面（P08）。
- 不做 refresh token、自动过期、OAuth、邮箱验证、多因素。
- 不做 Chat/知识/任务/MCP/AIOps/反馈/审计 CRUD。
- 不做多租户隔离。

## Decisions

### 决策：合同形状

- 注册请求 `{email,password}`，成功 `AuthUser`。
- 登录请求 `{email,password}`，成功 `{accessToken,user}`。
- 登出成功 `{}`；`/auth/me` 成功 `AuthUser`。
- 新增 `AUTH_INVALID_CREDENTIALS`（401）。重复邮箱用已有 `BUSINESS_CONFLICT`。
- `AuthUser` 字段：`id`、`email`、`createdAt`（UTC ISO）。

备选：注册同时发 token。否决：登录是发放会话的唯一入口，恢复只依赖已存 token。

### 决策：表结构

`users(id,email unique,password_hash,created_at,updated_at)`  
`auth_sessions(id,user_id,token_hash unique,created_at,last_seen_at,revoked_at nullable)`  
规范化列，不把会话状态塞进 JSON。

### 决策：安全与时序

`PasswordHash.recommended()`（Argon2）。未知账号对固定 dummy hash 做 `verify`，再统一抛 `AUTH_INVALID_CREDENTIALS`。token 用 `secrets.token_urlsafe(32)`，入库 `sha256.hexdigest()`（64 字符）。本版本不设 `expires_at`。

### 决策：包布局

领域在 `super_ai.auth`（record/protocol/service/passwords/tokens）。SQLite 实现放 `super_ai.memory.sqlite`。FastAPI 依赖读 `Authorization: Bearer`，更新 lastSeen 后由路由提交事务。

### 决策：应用与 CORS

`create_app` 继续默认不连库；认证测试注入临时 `database.url`。CORS 允许 `http://127.0.0.1:5173`。

### 决策：前端存储

`localStorage` 键只存 access token。Pinia auth store：`initialize` → `/auth/me`；401 或 logout 清 token 与 user，不调用删除用户 API。

## Risks / Trade-offs

- [Dummy Argon2 不能完美抹平时序] → 仍强制走哈希校验，避免明显短路。
- [无过期] → 登出即撤销；后续提案再加策略，本版不假装已过期。
- [CORS 只放行本机 Vite] → 满足桌面 Web 本机开发，不开放任意 Origin。

## Migration Plan

新增 Alembic 修订接在 foundation head 之后。测试用 `upgrade_to_head`。开发者执行 `alembic upgrade head`。无数据回填。
