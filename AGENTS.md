# Super AI 工程指南

本文件固化目录、构建命令与第一天边界。后续提案必须遵守，不得绕过。

## 目录

- `apps/backend`：Python 后端，包位于 `src/super_ai`
- `apps/frontend`：Vue 桌面 Web
- `packages/api-contracts`：HTTP envelope、错误码、OpenAPI 与 SSE 事件的单一事实来源
- `config`：只提交 `project.template.json` 与 `user.project.template.json`
- `infra`：Compose 边界说明，不托管应用
- `scripts`：本机辅助脚本
- `openspec`：spec-driven 变更
- `docs`：VitePress 文档骨架

## 技术栈

### 后端

Python >=3.10、FastAPI、Pydantic v2、uv、hatchling、src layout、SQLAlchemy 2 async、aiosqlite、Alembic、pytest、pytest-asyncio、Ruff、strict Pyright。

pytest 使用 `asyncio_mode=auto`。Ruff：`line-length=100`、`target-version=py310`、规则 `B/E/F/I/UP`。

### Agent / AI（后续提案实现）

LangChain 1.x `create_agent`、LangGraph、langchain-openai、langchain-mcp-adapters、MCP、pymilvus 3、rank-bm25、pypdf、langchain-text-splitters、httpx。本仓库骨架不安装、不运行这些能力。

### 前端

Vue 3.5、Vite 6、TypeScript 5.6 strict（`exactOptionalPropertyTypes`、`noUncheckedIndexedAccess`、`isolatedModules`、ES2022 / Bundler resolution）、Pinia 3、Vue Router 4、Vitest 2、marked、DOMPurify、lucide-vue-next。

当前验收目标是**桌面 Web**，不是原生移动应用。

### 仓库

npm workspaces、OpenSpec spec-driven workflow、VitePress 文档、Conventional Commits。所有 OpenSpec 文档使用简体中文。

## 构建与验证命令

根目录：

```bash
npm install
npm run contracts:typecheck
npm run contracts:test
npm run frontend:typecheck
npm run frontend:test
npm run frontend:build
```

后端：

```bash
cd apps/backend
uv sync
uv run ruff check .
uv run pyright
uv run pytest
```

另外：`openspec validate --all`、`git diff --check`。

数据库迁移（在 `apps/backend`）：

```bash
mkdir -p var
uv run alembic upgrade head
```

测试必须使用临时 SQLite 与 `upgrade_to_head`，不得依赖本机 `var/memory.sqlite3`。

## HTTP / SSE 合同

- `packages/api-contracts` 是 HTTP 响应、错误码、OpenAPI path 与 SSE event 的唯一来源
- 成功 envelope：`{ok:true,data,meta:{requestId}}`；失败 envelope：`{ok:false,error,meta:{requestId}}`
- 后续功能只能扩展合同，不能自造临时 payload 或平行 event union
- **先补合同再加 endpoint**：先改 catalog / OpenAPI / TypeScript 类型，再实现后端 path
- 前端 `apiClient` / `sseClient` 必须 import 合同包；后端 Pydantic 形状由合同测试对齐
- `X-Request-ID` 透传或生成，并写入响应头与 `meta.requestId`

## Python 导入与依赖注入

- 只允许 `from super_ai...`
- 禁止 `from src.super_ai` 或 `import src.super_ai`
- 模块 import 期间不得连接 SQLite、Milvus、LLM 或 MCP
- 外部系统必须通过显式依赖注入或受控生命周期创建
- `import super_ai.memory` 及其子模块不得打开数据库或运行迁移

## 持久化

- 数据库 URL 只从本地 JSON 深合并的 `database.url` 读取，不把 OS 环境变量当作项目配置
- SQLAlchemy 2 async + aiosqlite；engine/session 只在 FastAPI lifespan、依赖 provider 或显式 `create_memory_runtime` 中创建
- `create_app()` 默认不读本机 JSON、不建库；本机启动使用 `create_app_from_local_config()`
- Alembic 是 schema 变更的唯一权威，禁止用 `create_all` 作为生产建表路径
- 领域服务只依赖 Repository Protocol 与不可变 record，不得接收 ORM model
- SQLite 实现位于 `super_ai.memory.sqlite`，扩展点位于 `super_ai.memory.extended_sqlite`；为未来 PostgreSQL 预留替换边界
- 统一 JSON 对象序列化、UTC 时间、ID 生成；仓储方法只 flush，由调用方提交或回滚
- 可查询或需关联的数据必须建规范化列/表，禁止把后续业务状态塞进无结构大 JSON
- 认证已提供用户/会话仓储与 HTTP API；不实现 Chat、知识、任务、MCP、AIOps、反馈或审计 CRUD，也不实现完整登录页面

## 配置与凭据

- 应用只读取本地 JSON 深合并结果：`project.json` 为基座，`user.project.json` 递归覆盖
- 不把操作系统环境变量当作项目配置
- 只提交空模板；本机 `config/project.json` 与 `config/user.project.json` 必须被忽略，不得 stage
- 可用 `scripts/copy-local-config.sh` 从模板复制空本机配置供 build
- 测试必须注入临时配置，不依赖开发者真实值
- 前端不得 import 完整 JSON；构建只能注入 `frontend.title`、`frontend.apiBaseUrl` 与明确 public 的 analytics key
- LLM、CLS、MCP、MinIO secret 永远不能进入浏览器 bundle
- 通用加载在 foundation 实现；LLM typed validation / provider 留给后续提案

## Tenant

当前没有多租户实现。后续提案细化 tenant 模型前，不得假装已隔离租户数据。

## 真实 MCP

本提案不接入真实 MCP。官方 CLS MCP Server 将来在主机运行，不进入 Compose。

## 基础设施

Compose 最终只托管 etcd、MinIO、Milvus、Attu、Alertmanager。后端、前端、官方 CLS MCP Server 在主机运行。不要添加应用容器文件。
