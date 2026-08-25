## Purpose

把 SSE 事件定义为来自合同包的判别联合，覆盖聊天与 AIOps 公共通道，避免前后端各自声明临时事件结构。

## ADDED Requirements

### Requirement: SSE 事件公共字段

每个 SSE 事件 MUST 包含 `id`、`type`、`channel`、`timestamp`。`channel` MUST 为 `chat` 或 `aiops`。

#### Scenario: 公共字段齐全

- **WHEN** 校验任意合法 SSE 事件
- **THEN** 它含有非空 `id`、已知 `type`、合法 `channel` 与 `timestamp`

### Requirement: 完整事件目录

合同 MUST 定义且仅以判别联合导出这些 `type`：`content.delta`、`reasoning.delta`、`tool.call`、`reference.source`、`task.status`、`report`、`complete`、`error`。实现 MUST NOT 再声明平行的私有 event union。

#### Scenario: 目录闭合

- **WHEN** 枚举合同中的 SSE type
- **THEN** 恰好覆盖上述八种 type

### Requirement: tool.call 生命周期

`tool.call` MUST 支持 `started`、`delta`、`completed`、`failed` 阶段，并用稳定 `toolCallId` 关联同一调用。

#### Scenario: 四阶段可区分

- **WHEN** 构造同一 `toolCallId` 的 started/delta/completed/failed 事件
- **THEN** 合同能区分阶段，且失败阶段可携带复用的错误结构

### Requirement: SSE error 复用 HTTP 错误结构

`error` 事件的错误对象 MUST 复用 HTTP `error` 字段结构（`code`、`category`、`httpStatus`、`message`、可选 `details`），不得另造一套 SSE 专用错误字段。

#### Scenario: 错误结构一致

- **WHEN** 比较 HTTP 失败 envelope 的 `error` 与 SSE `error` 事件载荷
- **THEN** 二者字段集合一致，且能使用同一错误目录 code
