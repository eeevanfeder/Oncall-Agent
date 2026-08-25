## Purpose

建立可替换的 Repository 边界：领域只依赖 Protocol 与不可变 record，SQLite 实现可被未来 PostgreSQL 替换，且本提案不实现后续领域 CRUD。

## ADDED Requirements

### Requirement: 领域只依赖 Protocol 与 record

持久化访问 MUST 通过 Repository Protocol。方法参数与返回值 MUST 是不可变 record，MUST NOT 是 ORM model。SQLite 实现 MUST 位于 `super_ai.memory.sqlite`，扩展点位于 `super_ai.memory.extended_sqlite`。

#### Scenario: Repository 合同不暴露 ORM

- **WHEN** 通过 Protocol 写入并读取一条 foundation record
- **THEN** 得到的是不可变 record，类型不是 ORM 类实例

### Requirement: 统一序列化、时间、ID 与事务

foundation MUST 统一 JSON 字段序列化、UTC 时间、ID 生成和事务边界。可查询或需关联的数据 MUST 使用规范化列/表，MUST NOT 把后续业务状态塞进无结构大 JSON。

#### Scenario: 事务回滚丢弃未提交写入

- **WHEN** 在事务中写入 foundation record 后回滚
- **THEN** 再次读取不到该 record

#### Scenario: 并发 async session 互不阻塞到失败

- **WHEN** 两个 async session 同时写入不同 foundation record
- **THEN** 两次写入都能成功提交

### Requirement: 不实现后续领域 CRUD

本提案 MUST NOT 实现认证、Chat、知识、任务、MCP、AIOps、反馈或审计的领域表 CRUD。只提供 persistence foundation 与可证明的 Repository 合同。

#### Scenario: 无领域仓储

- **WHEN** 检查 `super_ai.memory` 导出
- **THEN** 不存在用户/会话/知识等领域 repository 实现
