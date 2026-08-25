## 1. 合同包

- [x] 1.1 在 `packages/api-contracts` 定义成功/失败 envelope、错误目录 JSON+TS、SSE 判别联合与 OpenAPI health，并用测试覆盖四类 envelope、全事件目录、tool 生命周期和错误复用
- [x] 1.2 导出单一入口，禁止第二套平行类型；typecheck/test 通过

## 2. 后端对齐

- [x] 2.1 实现 Pydantic envelope、错误目录加载、success/error helper、X-Request-ID 中间件与校验/异常 handler，并用测试覆盖 request-id 与验证错误字段路径
- [x] 2.2 将 `/health` 改为成功 envelope；合同测试证明序列化形状与 catalog/OpenAPI 一致
- [x] 2.3 backend `ruff` / `pyright` / `pytest` 通过，且 import 期间仍不连接外部系统

## 3. 前端 transport

- [x] 3.1 实现 typed apiClient（解 envelope、request id/bearer 扩展点）与 sseClient（跨 chunk frame parser），事件类型只从合同包导入
- [x] 3.2 用测试覆盖分块 frame parser，并断言前端没有私有 SSE event union
- [x] 3.3 frontend typecheck/test/build 通过

## 4. 指南与验收

- [x] 4.1 更新 `AGENTS.md` 与合同 README：先补合同再加 endpoint；后续只能扩展不能自造临时 payload
- [x] 4.2 运行 `openspec validate --all` 与 `git diff --check`，全部门禁通过后验证并归档
