# API Contracts

HTTP envelope、错误目录、OpenAPI 与 SSE 事件的单一事实来源。

当前 OpenAPI 覆盖 `GET /health` 与认证 path。新增 endpoint 必须先扩展 `openapi/openapi.json` 与类型，再写实现。

## 验证

```bash
npm run contracts:typecheck
npm run contracts:test
```
