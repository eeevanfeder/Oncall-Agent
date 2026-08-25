# auth-api Specification

## Purpose

规定注册、登录、登出与当前用户查询的 HTTP 行为，使客户端只面对统一 envelope 与稳定错误码。

## Requirements

### Requirement: 认证 HTTP 路径使用统一 envelope

系统 MUST 提供 `POST /auth/register`、`POST /auth/login`、`POST /auth/logout` 与 `GET /auth/me`。成功与失败响应 MUST 使用合同 envelope，并透传或生成 `X-Request-ID`/`meta.requestId`。

#### Scenario: 注册成功返回用户

- **WHEN** 使用尚未占用的规范化邮箱与合法密码调用 `POST /auth/register`
- **THEN** 响应为成功 envelope，`data` 含用户 `id`、规范化 `email` 与 `createdAt`，不含密码或 token

#### Scenario: 登录成功返回 bearer 与用户

- **WHEN** 使用正确邮箱与密码调用 `POST /auth/login`
- **THEN** 成功 envelope 的 `data` 含 `accessToken` 与用户对象

#### Scenario: 当前用户与登出

- **WHEN** 使用有效 bearer 调用 `GET /auth/me` 再调用 `POST /auth/logout`
- **THEN** `/auth/me` 返回对应用户；登出后同一 token 再访问 `/auth/me` 得到 `AUTH_UNAUTHORIZED`

### Requirement: 登录失败不得枚举账号

用户不存在与密码错误 MUST 返回同一个 `AUTH_INVALID_CREDENTIALS`。未知账号 MUST 仍执行 dummy Argon2 校验。缺失、非法或已撤销的 bearer MUST 返回已登记的 `AUTH_UNAUTHORIZED`。

#### Scenario: 错误登录统一错误码

- **WHEN** 使用不存在的邮箱或错误密码登录
- **THEN** 两次失败 envelope 的 `error.code` 都是 `AUTH_INVALID_CREDENTIALS`

#### Scenario: 无 token 访问 me

- **WHEN** 不带 Authorization 调用 `GET /auth/me`
- **THEN** 失败 envelope 使用 `AUTH_UNAUTHORIZED`

### Requirement: 重复邮箱与校验错误使用目录码

重复邮箱 MUST 返回 `BUSINESS_CONFLICT`。非法邮箱或密码校验失败 MUST 返回 `VALIDATION_INVALID_INPUT`，并在 `details` 中提供字段路径。

#### Scenario: 重复邮箱冲突

- **WHEN** 使用同一规范化邮箱再次注册
- **THEN** 失败 envelope 的 `error.code` 为 `BUSINESS_CONFLICT`

### Requirement: CORS 允许本机前端

后端 MUST 允许来源 `http://127.0.0.1:5173` 访问认证与其它 JSON API。

#### Scenario: 预检或带 Origin 的请求

- **WHEN** 请求带 `Origin: http://127.0.0.1:5173`
- **THEN** 响应包含允许该来源的 CORS 头
