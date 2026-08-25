## Purpose

规定用户与会话如何安全落库：密码只存 Argon2 哈希，token 只存 SHA-256，会话可撤销且可更新 lastSeen。

## ADDED Requirements

### Requirement: 用户邮箱唯一且密码只存哈希

邮箱 MUST 做规范化（去空白并小写）后唯一保存。密码 MUST 用 `pwdlib[argon2]` 哈希后入库，MUST NOT 保存或写入日志明文密码。

#### Scenario: 哈希不是明文

- **WHEN** 用户以密码 `secret-pass` 注册成功
- **THEN** `users.password_hash` 是 Argon2 哈希，且不等于明文，响应与日志不得出现该明文密码

### Requirement: 会话只保存 token hash

登录 MUST 生成高熵 opaque bearer token。客户端 MUST 获得 raw token；SQLite MUST 只保存 64 位十六进制 SHA-256 token hash。本版本 MUST NOT 实现未声明的自动过期。

#### Scenario: 数据库无 raw token

- **WHEN** 登录成功并检查 `auth_sessions`
- **THEN** 表中存在对应 `token_hash`，且任何列都不等于 raw token

### Requirement: lastSeen 与撤销

活跃会话 MUST 记录 `createdAt` 与 `lastSeenAt`。访问当前用户 MUST 更新 `lastSeenAt`。登出 MUST 写入 `revokedAt`，使该 token 立即失效。仓储 MUST 按用户/会话归属访问，不得用 ORM model 作为领域输入。

#### Scenario: me 更新 lastSeen

- **WHEN** 登录后调用 `GET /auth/me`
- **THEN** 该会话的 `lastSeenAt` 不早于登录时的值，且随后可被更新

#### Scenario: 登出撤销会话

- **WHEN** 对有效 token 执行登出
- **THEN** 该会话 `revokedAt` 非空，且不能再通过该 token 读取当前用户
