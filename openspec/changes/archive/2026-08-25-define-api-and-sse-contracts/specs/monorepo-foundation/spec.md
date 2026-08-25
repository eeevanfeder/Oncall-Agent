## MODIFIED Requirements

### Requirement: 后端最小可运行健康检查

后端 MUST 提供不在模块 import 期间连接外部系统的应用工厂，并暴露只读 `/health` 接口。应用工厂被导入时 MUST 成功，且不连接 SQLite、Milvus、LLM 或 MCP。`/health` 的 JSON 响应 MUST 使用成功 envelope，`data` MUST 为 `{status:"ok"}`。

#### Scenario: 导入应用工厂

- **WHEN** 测试导入后端应用工厂模块
- **THEN** 导入成功，且过程中没有打开 SQLite、Milvus、LLM 或 MCP 连接

#### Scenario: 健康检查响应

- **WHEN** 对应用工厂创建的应用请求 `/health`
- **THEN** 响应表示服务可用，且不触发外部系统连接

#### Scenario: 健康检查使用成功 envelope

- **WHEN** 请求 `/health`
- **THEN** 响应为 `{ok:true,data:{status:"ok"},meta:{requestId}}`
