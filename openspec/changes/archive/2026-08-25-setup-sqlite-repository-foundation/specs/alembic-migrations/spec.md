## Purpose

把 Alembic 定为 schema 变更的唯一权威，使空库可升级到与 SQLAlchemy metadata 一致的基础结构。

## ADDED Requirements

### Requirement: Alembic 是迁移唯一权威

schema 变更 MUST 通过 Alembic 迁移表达。仓库 MUST 包含迁移环境与首个基础迁移。实现 MUST NOT 用 `create_all` 作为生产建表路径。

#### Scenario: 空库 upgrade head

- **WHEN** 对全新空 SQLite 文件执行 `alembic upgrade head` 或等价 helper
- **THEN** 基础表存在，且 alembic 版本到达 head

### Requirement: metadata 与迁移一致

SQLAlchemy `Base.metadata` 中的 foundation 表 MUST 与 head 迁移创建的表一致。

#### Scenario: 表名对齐

- **WHEN** 比较升级后的数据库表与 metadata 表名
- **THEN** foundation 表集合一致（除 alembic 版本表外）
