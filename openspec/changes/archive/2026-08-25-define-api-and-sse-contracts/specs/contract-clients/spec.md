## Purpose

规定前端 transport 与后端序列化都必须消费合同包，禁止复制私有 envelope 或 SSE union，并用测试证明形状一致。

## ADDED Requirements

### Requirement: 前端 apiClient 解 envelope

前端 MUST 提供 typed `apiClient`，能解析成功与失败 envelope，并把 `data` 或 `error` 交给调用方。它 MUST 提供注入 request id 与 bearer 的扩展点，但本提案不实现真实登录。

#### Scenario: 成功时返回 data

- **WHEN** apiClient 收到成功 envelope
- **THEN** 调用方得到类型化 `data`，并能读到 `requestId`

#### Scenario: 失败时抛出或返回合同 error

- **WHEN** apiClient 收到失败 envelope
- **THEN** 调用方得到合同中的 `error` 结构，而不是临时字段

### Requirement: 前端 sseClient 解析跨 chunk frame

前端 MUST 提供 typed `sseClient`，按 SSE 帧边界解析，即使一个事件被拆到多个 chunk，或多个事件挤在一个 chunk。解析出的事件 MUST 使用合同包的判别联合，不得在前端再定义一套 event type。

#### Scenario: 分块帧仍能还原事件

- **WHEN** 一个完整 SSE 帧被拆成两个 chunk 输入 parser
- **THEN** parser 只在帧完整后产出一个合同事件

#### Scenario: 禁止私有 event union

- **WHEN** 检查前端源码的 SSE 类型导入
- **THEN** 事件联合来自 `@super-ai/api-contracts`，前端没有平行的私有 union 定义

### Requirement: 后端形状由合同测试对齐

后端无需导入 TypeScript。Pydantic 或序列化 JSON 的字段 MUST 由合同测试对照合同包中的机器可读定义证明一致，覆盖成功/失败 envelope、错误目录与 SSE 事件。

#### Scenario: 序列化形状匹配合同

- **WHEN** 运行跨语言合同测试
- **THEN** 后端序列化的 envelope、错误码与 SSE 事件字段与合同定义一致
