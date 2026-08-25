## Why

这是全新仓库的第一份提案。必须先锁定技术栈、目录骨架、工程边界和质量基线，否则后续认证、聊天、知识库、AIOps、MCP 等能力会在不安全的配置模型和错误的包布局上叠加。现在就要把可提交模板、忽略规则、配置深合并和前端 public allowlist 立住，避免密钥进入 Git 或浏览器 bundle。

## What Changes

- 建立最终单仓目录：`apps/backend`、`apps/frontend`、`packages/api-contracts`、`config`、`infra`、`scripts`、`openspec`、`docs`。
- 锁定全栈技术选型与质量命令（后端 uv/Ruff/Pyright/pytest，前端 Vue/Vite/TS/Vitest，contracts typecheck/test，根 npm workspaces）。
- 后端包放在 `apps/backend/src/super_ai`，仅允许 `from super_ai...`；模块 import 期间不得连接 SQLite、Milvus、LLM 或 MCP。
- 提供最小可运行骨架：后端 `/health` app factory、前端桌面 Web 骨架、contracts 最小 foundation 类型。
- 从第一天采用安全配置边界：只提交空模板 JSON；本地 `project.json` / `user.project.json` 与 `.env*` 必须被忽略；后端深合并加载；前端只注入 allowlist 字段。
- 应用只读取本地 JSON 深合并结果，不把 OS 环境变量当作项目配置。
- 基础设施只锁定 Compose 边界并创建目录/说明：Compose 仅托管 etcd、MinIO、Milvus、Attu、Alertmanager；应用与官方 CLS MCP Server 在主机运行。不创建 `app.Dockerfile`、`project.compose.json` 或应用 Compose 服务。
- 固化 `AGENTS.md`、中文 README、OpenSpec `spec-driven` 上下文。不实现认证、聊天、知识库、AIOps、MCP 等产品功能。
- 不为历史清理设计 `git filter-repo` 或 force push。

## Capabilities

### New Capabilities

- `monorepo-foundation`：单仓目录、包布局、workspaces、最小可运行骨架与质量门禁。
- `secure-config`：模板与忽略规则、JSON 深合并、前端 public-config allowlist、测试注入。
- `engineering-baseline`：技术栈与工程约束、import-safety、基础设施边界、文档与验收规则。

### Modified Capabilities

- 无。仓库尚无主 specs。

## Impact

- 影响整个仓库布局、根与各 workspace 的 package/pyproject、`.gitignore`、`openspec/config.yaml`、`AGENTS.md`、README 与 `infra/` 说明。
- 新增最小依赖：后端 FastAPI/Pydantic/pytest/Ruff/Pyright 等；前端 Vue/Vite/TypeScript/Pinia/Vue Router/Vitest；根 npm workspaces 与 VitePress。
- 不引入认证、聊天、知识库、AIOps、MCP 运行时，也不把 Agent/AI 依赖装进本提案的可运行骨架。
- 不影响远程 Git 历史；禁止设计破坏性历史改写步骤。
