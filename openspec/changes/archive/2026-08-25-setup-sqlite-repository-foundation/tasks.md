## 1. 运行时与配置

- [x] 1.1 增加 `database.url` 模板字段与 `database_url_from_config`，并用临时配置测试注入
- [x] 1.2 实现显式 async engine/session factory 与 FastAPI lifespan/provider；用测试证明 `import super_ai.memory` 不打开数据库

## 2. Alembic 与基础表

- [x] 2.1 建立 Base、`foundation_meta` 模型、alembic 环境与首个迁移
- [x] 2.2 实现测试用 `upgrade_to_head` helper，覆盖空库升级以及 metadata 与迁移一致

## 3. Repository 边界

- [x] 3.1 定义不可变 record 与 Repository Protocol，SQLite 实现放在 `memory.sqlite`，并预留 `extended_sqlite`
- [x] 3.2 用测试覆盖 Repository 合同、事务回滚与并发 async session，且不实现领域 CRUD

## 4. 指南与验收

- [x] 4.1 更新 `AGENTS.md`：引擎生命周期、Alembic 权威、Protocol/record、UTC/ID/JSON/事务、测试隔离
- [x] 4.2 运行 `alembic upgrade head`、backend pytest/Ruff/Pyright、`openspec validate --all`、`git diff --check` 后验证并归档
