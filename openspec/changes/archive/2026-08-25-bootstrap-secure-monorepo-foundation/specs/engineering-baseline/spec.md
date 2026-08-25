## Purpose

把技术栈、导入边界、基础设施职责和文档验收规则写成可验证基线，使后续提案不能绕过第一天确立的工程约束。

## ADDED Requirements

### Requirement: 工程指南固化技术栈与约束

仓库 MUST 提供根 `AGENTS.md`，并更新 `openspec/config.yaml` 的项目上下文，明确锁定后端、Agent/AI、前端与仓库工具链，同时声明 Agent/AI 能力由后续提案实现。中文 README 与各 workspace README MUST 只说明骨架与验证方式，MUST NOT 声称未实现的产品功能。所有 OpenSpec 文档 MUST 使用简体中文。

#### Scenario: 指南包含锁定技术栈

- **WHEN** 阅读 `AGENTS.md` 与 `openspec/config.yaml`
- **THEN** 其中记录提案要求的后端、前端、仓库工具链，以及 Agent/AI 延后实现的说明

#### Scenario: README 不夸大能力

- **WHEN** 阅读根 README 与各 workspace README
- **THEN** 内容仅描述骨架与如何验证，不声称认证、聊天、知识库、AIOps 或 MCP 已实现

### Requirement: 后端导入与依赖注入边界

后端代码 MUST 只使用 `from super_ai...` 导入包内模块，MUST NOT 使用 `from src.super_ai` 或等价路径。模块 import 期间 MUST NOT 连接 SQLite、Milvus、LLM 或 MCP。需要外部系统的能力 MUST 通过显式依赖注入或受控生命周期创建，而不是在 import 时隐式连接。

#### Scenario: 禁止错误包导入

- **WHEN** 运行 import-safety 测试或静态检查
- **THEN** 仓库中不存在 `src.super_ai` 导入，且 `super_ai` 可作为包导入

#### Scenario: import 保持无连接

- **WHEN** 导入 `super_ai` 包及其应用工厂
- **THEN** 不创建 SQLite、Milvus、LLM 或 MCP 连接

### Requirement: 基础设施只锁定主机与 Compose 边界

`infra/` MUST 存在并说明：Compose 最终只托管 etcd、MinIO、Milvus、Attu、Alertmanager；后端、前端、官方 CLS MCP Server MUST 在主机运行。本提案 MUST NOT 创建 `app.Dockerfile`、`project.compose.json` 或把应用作为 Compose 服务。

#### Scenario: 边界说明存在且无应用容器文件

- **WHEN** 检查 `infra/` 与仓库根目录
- **THEN** 存在边界说明，且不存在 `app.Dockerfile` 或 `project.compose.json`

### Requirement: 租户、凭据与真实 MCP 规则被记录

`AGENTS.md` MUST 记录：配置与凭据只来自本地 JSON 深合并；不得把密钥写入仓库；tenant 相关约定在后续提案细化前不得假装已实现多租户；真实 MCP 不得在本提案接入。文档 MUST 声明桌面前端为当前验收目标。

#### Scenario: 工程规则可被后续提案引用

- **WHEN** 后续提案阅读 `AGENTS.md`
- **THEN** 能找到目录、构建命令、Python 导入/依赖注入、配置/凭据、tenant、真实 MCP、OpenSpec 简中与桌面前端验收规则
