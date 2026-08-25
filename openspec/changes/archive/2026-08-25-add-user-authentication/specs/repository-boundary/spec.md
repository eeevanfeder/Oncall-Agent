## MODIFIED Requirements

### Requirement: 不实现后续领域 CRUD

除认证所需的用户与会话仓储外，本阶段 MUST NOT 实现 Chat、知识、任务、MCP、AIOps、反馈或审计的领域表 CRUD。认证仓储 MUST 继续只暴露 Protocol 与不可变 record。

#### Scenario: 无领域仓储

- **WHEN** 检查 `super_ai.memory` 导出与模块
- **THEN** 不存在聊天/知识/任务/MCP/AIOps/反馈/审计 repository 实现；可以存在用户与会话仓储
