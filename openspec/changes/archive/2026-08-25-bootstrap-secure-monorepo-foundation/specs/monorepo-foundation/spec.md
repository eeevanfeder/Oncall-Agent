## Purpose

为全新仓库提供最终单仓目录、包边界和最小可运行骨架，使后续提案能在固定布局上叠加产品功能，而本提案本身不交付认证、聊天、知识库、AIOps 或 MCP。

## ADDED Requirements

### Requirement: 最终单仓目录存在且可被验证

仓库 MUST 建立并保持以下顶层目录：`apps/backend`、`apps/frontend`、`packages/api-contracts`、`config`、`infra`、`scripts`、`openspec`、`docs`。后端可导入包 MUST 位于 `apps/backend/src/super_ai`。最小测试 MUST 断言这些目录与包入口存在。

#### Scenario: 目录骨架验收

- **WHEN** 运行基础目录与包布局测试
- **THEN** 上述顶层目录全部存在，且后端包入口位于 `apps/backend/src/super_ai`

### Requirement: 后端最小可运行健康检查

后端 MUST 提供不在模块 import 期间连接外部系统的应用工厂，并暴露只读 `/health` 接口。应用工厂被导入时 MUST 成功，且不连接 SQLite、Milvus、LLM 或 MCP。

#### Scenario: 导入应用工厂

- **WHEN** 测试导入后端应用工厂模块
- **THEN** 导入成功，且过程中没有打开 SQLite、Milvus、LLM 或 MCP 连接

#### Scenario: 健康检查响应

- **WHEN** 对应用工厂创建的应用请求 `/health`
- **THEN** 响应表示服务可用，且不触发外部系统连接

### Requirement: 前端最小桌面 Web 骨架

前端 MUST 提供可 typecheck、可测试、可构建的桌面 Web 骨架。验收目标 MUST 是桌面浏览器，而不是原生移动应用。

#### Scenario: 前端质量命令通过

- **WHEN** 运行前端 typecheck、test 与 build
- **THEN** 三项命令均成功退出，且产物面向桌面 Web

### Requirement: 共享合约最小入口

`packages/api-contracts` MUST 提供可 typecheck 与可测试的 typed entrypoint，并只包含本提案所需的最小 foundation 类型。它 MUST NOT 声明未实现的产品 API。

#### Scenario: 合约包可验证

- **WHEN** 运行 contracts 的 typecheck 与 test
- **THEN** 两项命令成功，且导出仅包含 foundation 类型

### Requirement: 工作区脚本与质量门禁

根仓库 MUST 使用 npm workspaces 聚合 contracts、frontend 与 docs 脚本。生成 package/pyproject 后 MUST 先执行根 `npm install` 与 backend `uv sync`。归档前 MUST 至少通过：`openspec validate --all`；后端 `uv run ruff check .`、`uv run pyright`、`uv run pytest`；contracts typecheck/test；frontend typecheck/test/build；`git diff --check`。

#### Scenario: 生成清单后安装依赖

- **WHEN** 根 package.json 与 backend pyproject 已生成
- **THEN** 先完成根 `npm install` 与 backend `uv sync`，再运行后续门禁

#### Scenario: 全部门禁通过

- **WHEN** 实现完成并运行规定验收命令
- **THEN** 所列命令全部成功，且 `git diff --check` 无空白错误
