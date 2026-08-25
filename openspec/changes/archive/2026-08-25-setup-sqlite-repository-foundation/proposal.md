## Why

认证、Chat、知识、任务、MCP、AIOps、反馈和审计都需要同一套可替换、可测试的持久化边界。若现在不把 SQLite 引擎生命周期、Alembic 权威和 Repository 协议立住，后续领域会在 import 时连库、直接依赖 ORM，并难以换成 PostgreSQL。

## What Changes

- 用 SQLAlchemy 2 async + aiosqlite 建立 persistence foundation；数据库 URL 只从本地 JSON 深合并配置读取。
- 以 Alembic 为 schema 迁移唯一权威：Base、async engine/session factory、迁移环境与首个基础迁移。
- engine/session 只在 FastAPI lifespan、依赖 provider 或显式初始化路径创建；`import super_ai.memory` 不得打开数据库或跑迁移。
- 领域服务依赖 Repository Protocol 与不可变 record，不得接收 ORM model。SQLite 实现放在 `super_ai.memory.sqlite` / `extended_sqlite`，为 PostgreSQL 预留替换边界。
- 统一 JSON 字段序列化、UTC 时间、ID 生成与事务约定；禁止把后续可查询业务状态塞进无结构大 JSON。
- 提供测试用临时 SQLite 与 migration helper；测试不得依赖本机 `var/memory.sqlite3`。
- 不实现后续领域 CRUD（认证、Chat、知识等）。

## Capabilities

### New Capabilities

- `sqlite-runtime`：配置注入、engine/session 生命周期、import-safety、测试库隔离。
- `alembic-migrations`：Alembic 权威、首个基础迁移、metadata 与迁移一致。
- `repository-boundary`：Protocol/record、SQLite 实现位置、事务与序列化约定、禁止领域 CRUD。

### Modified Capabilities

- 无需求变更到既有 HTTP 合同。工程指南补充持久化规则，不改 `engineering-baseline` 的既有 requirement 语义。

## Impact

- 影响 `apps/backend` 的 `super_ai.memory`、Alembic 目录、配置模板中的 `database.url`、FastAPI lifespan 与测试夹具。
- 不新增产品 endpoint，不实现领域表 CRUD。
- 本机 `apps/backend/var/*.sqlite3` 继续被忽略。
