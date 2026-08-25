## MODIFIED Requirements

### Requirement: 工程指南固化技术栈与约束

仓库 MUST 提供根 `AGENTS.md`，并更新 `openspec/config.yaml` 的项目上下文。中文 README 与各 workspace README MUST 只说明已落地能力与验证方式。文档可以描述认证 HTTP API 与前端 auth 状态，MUST NOT 声称已实现完整登录页面、聊天、知识库、AIOps 或 MCP。所有 OpenSpec 文档 MUST 使用简体中文。

#### Scenario: 指南包含锁定技术栈

- **WHEN** 阅读 `AGENTS.md` 与 `openspec/config.yaml`
- **THEN** 其中记录提案要求的后端、前端、仓库工具链，以及 Agent/AI 延后实现的说明

#### Scenario: README 不夸大能力

- **WHEN** 阅读根 README 与各 workspace README
- **THEN** 可以提到认证 API / authClient，但不声称完整认证页面、聊天、知识库、AIOps 或 MCP 已实现
