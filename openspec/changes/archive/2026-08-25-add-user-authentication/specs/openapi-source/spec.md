## MODIFIED Requirements

### Requirement: 当前只覆盖 foundation health

OpenAPI MUST 登记 foundation health 以及本提案的认证 path：`POST /auth/register`、`POST /auth/login`、`POST /auth/logout`、`GET /auth/me`。文档 MUST 描述 Auth DTO、请求/响应 schema，以及 bearer security scheme。health 成功响应仍为成功 envelope，data 为 `{status:"ok"}`。

#### Scenario: 无额外业务 path

- **WHEN** 列出 OpenAPI paths
- **THEN** 包含 health 与上述认证 path，不含聊天、知识库或其它未立项 path

#### Scenario: 合同含 bearer 与 401

- **WHEN** 读取认证 path 的安全与错误描述
- **THEN** 受保护路径引用 bearer scheme，并登记 401 错误
