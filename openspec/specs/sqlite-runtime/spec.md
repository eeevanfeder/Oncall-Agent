# sqlite-runtime Specification

## Purpose

规定 SQLite 引擎与会话只能在显式生命周期中创建，并从本地 JSON 配置读取 URL，确保 import 与测试都不会碰到开发者本机数据库。

## Requirements

### Requirement: 数据库 URL 来自 JSON 深合并

运行时 MUST 从本地 JSON 深合并结果读取数据库 URL，MUST NOT 把操作系统环境变量当作项目配置来源。测试 MUST 注入临时配置，不得读取开发者 `var/memory.sqlite3`。

#### Scenario: 配置注入决定 URL

- **WHEN** 测试提供临时 `project.json`，其中 `database.url` 指向临时文件
- **THEN** 运行时使用该 URL，而不是仓库默认本机路径

### Requirement: import 不得打开数据库

导入 `super_ai.memory` 及其子模块 MUST NOT 创建 engine、打开 SQLite 连接或运行迁移。engine/session MUST 只在 FastAPI lifespan、依赖 provider 或显式初始化函数中创建。

#### Scenario: 导入 memory 无连接

- **WHEN** 测试导入 `super_ai.memory` 与 `super_ai.memory.sqlite`
- **THEN** 过程中没有打开 SQLite 连接，也没有执行迁移

### Requirement: 测试使用临时数据库

测试夹具 MUST 提供临时 SQLite 文件与 migration helper。测试 MUST NOT 依赖开发者本机 `apps/backend/var/memory.sqlite3`。

#### Scenario: 测试库与本机库隔离

- **WHEN** 运行持久化测试
- **THEN** 使用的数据库路径位于临时目录，而不是本机 var 路径
