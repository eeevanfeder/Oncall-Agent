# 后端骨架

包路径：`src/super_ai`。只允许 `from super_ai...`。

当前提供应用工厂、`/health`、SQLite persistence foundation，以及认证 HTTP API（注册/登录/登出/当前用户）。导入模块时不会连接 SQLite、Milvus、LLM 或 MCP。完整登录页面、聊天与其它产品能力尚未实现。

## 验证

```bash
uv sync
mkdir -p var
uv run alembic upgrade head
uv run ruff check .
uv run pyright
uv run pytest
```

