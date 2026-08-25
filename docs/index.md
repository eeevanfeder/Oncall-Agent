# Super AI 文档骨架

本站点只说明仓库骨架与验证方式。认证、聊天、知识库、AIOps、MCP 尚未实现。

## 验证

在仓库根目录：

```bash
npm install
npm run frontend:typecheck
npm run frontend:test
npm run frontend:build
npm run contracts:typecheck
npm run contracts:test
```

后端：

```bash
cd apps/backend
uv sync
uv run ruff check .
uv run pyright
uv run pytest
```
