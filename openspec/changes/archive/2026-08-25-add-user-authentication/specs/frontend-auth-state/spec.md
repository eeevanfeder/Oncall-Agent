## Purpose

规定前端可复用的认证客户端与状态：只把 access token 存入 localStorage，启动时恢复会话，失效时只清理本地受保护状态。

## ADDED Requirements

### Requirement: authClient 与 token 存储

前端 MUST 提供可复用 `authClient`，类型从合同包导入。access token MUST 是唯一允许写入 localStorage 的认证凭据；密码、用户对象与其它 secret MUST NOT 写入 localStorage。

#### Scenario: 登录只持久化 token

- **WHEN** auth 状态完成登录
- **THEN** localStorage 仅保存 access token，不含密码

### Requirement: 启动恢复调用 /auth/me

`initialize` MUST 在本地存在 token 时调用 `GET /auth/me` 恢复当前用户。token 无效 MUST 清除本地受保护 store。

#### Scenario: 有效 token 恢复用户

- **WHEN** localStorage 已有 token 且 `/auth/me` 成功
- **THEN** auth 状态持有对应用户

#### Scenario: 失效 token 清理本地

- **WHEN** `/auth/me` 返回未认证错误
- **THEN** 本地 token 与受保护 auth 状态被清除

### Requirement: logout 只清理本地不得删服务端业务数据

logout 与失效清理 MUST 清除本地 token 与受保护 store，MUST NOT 调用删除用户或其它服务端业务数据的接口。完整认证页面 MUST 留到后续提案。

#### Scenario: logout 不删除服务端用户

- **WHEN** 前端执行 logout
- **THEN** 它调用登出 API 并清理本地状态，但不发送删除用户或业务数据的请求
