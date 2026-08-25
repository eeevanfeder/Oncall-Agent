# http-envelope Specification

## Purpose

规定所有 HTTP JSON 接口使用同一套成功与失败 envelope，以及稳定错误目录和 request id，使前后端与后续提案不能再发明临时响应形状。

## Requirements

### Requirement: 成功响应必须使用统一 envelope

成功 HTTP JSON 响应 MUST 为 `{ok:true,data,meta:{requestId}}`。`data` MUST 承载业务载荷。`meta.requestId` MUST 为非空字符串。

#### Scenario: 成功 envelope 形状

- **WHEN** 后端返回成功 JSON
- **THEN** 顶层含 `ok=true`、`data` 与 `meta.requestId`，且不含 `error`

### Requirement: 失败响应必须使用统一 envelope

失败 HTTP JSON 响应 MUST 为 `{ok:false,error:{code,category,httpStatus,message,details?},meta:{requestId}}`。`details` 可省略。成功与失败 MUST 互斥。

#### Scenario: 失败 envelope 含完整 error

- **WHEN** 后端返回失败 JSON
- **THEN** 顶层含 `ok=false`、`error.code`、`error.category`、`error.httpStatus`、`error.message` 与 `meta.requestId`，且不含业务 `data`

#### Scenario: 失败可省略 details

- **WHEN** 失败没有附加细节
- **THEN** 响应可以没有 `error.details`，其余必填字段仍在

### Requirement: 稳定错误目录

合同 MUST 提供可扩展错误目录，至少包含 `AUTH_*`、`BUSINESS_*`、`VALIDATION_*`、`SYSTEM_*`。每个错误 MUST 含 `category`、HTTP status 与安全默认消息。运行时 MUST 使用目录中的 code，不得临时拼造未登记 code。

#### Scenario: 目录项可被解析

- **WHEN** 查询一个已登记错误 code
- **THEN** 能得到其 category、httpStatus 与默认 message

### Requirement: 校验错误暴露字段路径

请求体或查询校验失败 MUST 使用 `VALIDATION_*` 错误，并在 `details` 中提供字段路径列表，使客户端能定位问题字段。

#### Scenario: 校验失败包含字段路径

- **WHEN** 请求触发验证错误
- **THEN** 失败 envelope 的 `error.details` 包含至少一个字段路径

### Requirement: Request ID 透传或生成

若请求带 `X-Request-ID`，响应 MUST 回传同一值到响应头与 `meta.requestId`。若缺失，服务 MUST 生成新的 request id 并同时写入响应头与 envelope。

#### Scenario: 透传已有 request id

- **WHEN** 请求头包含 `X-Request-ID`
- **THEN** 响应头与 `meta.requestId` 等于该值

#### Scenario: 缺失时生成 request id

- **WHEN** 请求没有 `X-Request-ID`
- **THEN** 响应头与 `meta.requestId` 仍是同一非空值
