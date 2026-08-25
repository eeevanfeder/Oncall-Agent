# 前端骨架

Vue 3.5 + Vite 6 桌面 Web 骨架。构建期只注入公开配置 allowlist，不读取完整项目 JSON。

提供可复用 `authClient` 与 auth 状态；完整登录页面、聊天、知识库、AIOps、MCP 尚未实现。

## 验证

在仓库根目录：

```bash
npm run frontend:typecheck
npm run frontend:test
npm run frontend:build
```
