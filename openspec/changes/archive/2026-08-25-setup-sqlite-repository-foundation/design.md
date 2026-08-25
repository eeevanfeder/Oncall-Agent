## Context

P01/P02 已归档。后端已锁定 SQLAlchemy 2 async、aiosqlite、Alembic 依赖，但没有 engine、迁移或 Repository。动机见 `proposal.md`。

## Goals / Non-Goals

**Goals:**

- 显式创建 async engine/session；import `super_ai.memory` 无副作用。
- Alembic 管理首个 `foundation_meta` 表，并与 metadata 对齐。
- Protocol + frozen record；SQLite 实现可替换。
- 测试只用临时库与 helper。

**Non-Goals:**

- 不实现认证/Chat/知识/任务/MCP/AIOps/反馈/审计 CRUD。
- 不引入 PostgreSQL 驱动或第二套迁移工具。
- 不让 `/health` 依赖数据库。

## Decisions

### 决策：包布局

```
super_ai/memory/           # Protocol、record、runtime API
super_ai/memory/sqlite/    # ORM 与 SQLite repository
super_ai/memory/extended_sqlite/  # 预留扩展，不放领域 CRUD
apps/backend/alembic/      # 迁移环境（Alembic 权威）
```

备选：把 alembic 藏进包内。否决：`alembic upgrade head` 在 backend 根更符合惯例。

### 决策：配置键

模板增加 `database.url`，默认空字符串。本机可写成 `sqlite+aiosqlite:///./var/memory.sqlite3`（文件被忽略）。运行时 `database_url_from_config(merged)` 解析；测试传入临时 `sqlite+aiosqlite:///<tmp>`。

### 决策：生命周期

`create_memory_runtime(url)` / `close_memory_runtime` 是显式 API。FastAPI `lifespan` 仅在配置了非空 URL 时创建 runtime 并挂到 `app.state`，`/health` 不访问它。依赖 provider `get_session` 只在 runtime 存在时提供 session。

### 决策：foundation 表

首迁创建 `foundation_meta`：`id`（UUID 字符串）、`created_at`/`updated_at`（UTC aware）、`label`（可查询列）、`attributes`（JSON，仅非查询附属信息）。这是 persistence 自检表，不是业务聚合。

### 决策：迁移 helper

测试调用 `upgrade_to_head(url)`，内部用 Alembic `Config` + `command.upgrade`。`env.py` 把 `sqlite+aiosqlite` 转成同步 `sqlite` 连接跑 DDL，避免在 pytest-asyncio 的运行中 loop 里调用 `asyncio.run`。禁止测试 `create_all` 代替 upgrade。

### 决策：并发与回滚

SQLite 用独立连接的两个 session 写入不同行证明 async session 可用。回滚测试在同一 session `begin()` 后 `rollback()`。

## Risks / Trade-offs

- [SQLite 写并发弱] → 测试只要求两次提交成功，不要求高吞吐。
- [空 URL 时 lifespan 不建库] → `/health` 仍可用；文档说明本机需复制配置。
- [JSON 列被滥用] → AGENTS 写明可查询字段必须规范化。

## Migration Plan

全新 foundation。开发者执行 `alembic upgrade head`。测试自建临时库。无数据回填。
