# Super AI

这是单仓工程骨架。当前可验证目录、配置边界、健康检查、认证 HTTP API 与前端 auth 状态。**尚未实现**完整登录页面、聊天、知识库、AIOps、MCP。

## 本机准备

```bash
# 可选：复制被忽略的空本机配置，供本地 build 使用，不要提交
bash scripts/copy-local-config.sh

npm install
cd apps/backend && uv sync
```

## 验证

```bash
openspec validate --all
git diff --check

cd apps/backend
uv run ruff check .
uv run pyright
uv run pytest

cd ../..
npm run contracts:typecheck
npm run contracts:test
npm run frontend:typecheck
npm run frontend:test
npm run frontend:build
```

## 目录

见 `AGENTS.md`。
