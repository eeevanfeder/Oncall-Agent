## MODIFIED Requirements

### Requirement: 前端 apiClient 解 envelope

前端 MUST 提供 typed `apiClient`，能解析成功与失败 envelope，并把 `data` 或 `error` 交给调用方。它 MUST 提供注入 request id 与 bearer 的扩展点。认证调用 MUST 通过可复用 `authClient` 走同一 client，不得另造 envelope。

#### Scenario: 成功时返回 data

- **WHEN** apiClient 收到成功 envelope
- **THEN** 调用方得到类型化 `data`，并能读到 `requestId`

#### Scenario: 失败时抛出或返回合同 error

- **WHEN** apiClient 收到失败 envelope
- **THEN** 调用方得到合同中的 `error` 结构，而不是临时字段

#### Scenario: authClient 复用合同类型

- **WHEN** 前端发起注册或登录
- **THEN** 请求/响应类型来自 `@super-ai/api-contracts`，并由 apiClient 解 envelope
