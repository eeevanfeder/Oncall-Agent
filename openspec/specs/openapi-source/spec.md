# openapi-source Specification

## Purpose

把机器可读 OpenAPI 放在合同包中，使 path 与 schema 先于实现存在；当前只覆盖 foundation/health，后续提案必须先补合同再加 endpoint。

## Requirements

### Requirement: OpenAPI 合同可被机器读取

`packages/api-contracts` MUST 提供可解析的 OpenAPI 文档，描述当前公开 HTTP path。文档组织 MUST 允许后续提案按能力追加 path，而不是另起一份私有 spec。

#### Scenario: 合同可解析且含 health

- **WHEN** 读取合同包中的 OpenAPI 文档
- **THEN** 它是合法 OpenAPI 对象，并包含 foundation health path

### Requirement: 当前只覆盖 foundation health

OpenAPI MUST 登记 foundation health 以及本提案的认证 path：`POST /auth/register`、`POST /auth/login`、`POST /auth/logout`、`GET /auth/me`。文档 MUST 描述 Auth DTO、请求/响应 schema，以及 bearer security scheme。health 成功响应仍为成功 envelope，data 为 `{status:"ok"}`。

#### Scenario: 无额外业务 path

- **WHEN** 列出 OpenAPI paths
- **THEN** 包含 health 与上述认证 path，不含聊天、知识库或其它未立项 path

#### Scenario: 合同含 bearer 与 401

- **WHEN** 读取认证 path 的安全与错误描述
- **THEN** 受保护路径引用 bearer scheme，并登记 401 错误

### Requirement: 先合同后 endpoint

工程规则 MUST 要求：新增 HTTP endpoint 前先扩展合同包 OpenAPI 与类型。实现 MUST NOT 先上线无合同的临时 path。

#### Scenario: 指南写明顺序

- **WHEN** 阅读 `AGENTS.md` 或合同包说明
- **THEN** 能看到“先补合同再加 endpoint”的约束
