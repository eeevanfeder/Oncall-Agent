## 1. 目录、忽略规则与配置模板

- [x] 1.1 建立 `apps/backend`、`apps/frontend`、`packages/api-contracts`、`config`、`infra`、`scripts`、`docs` 目录骨架，并用测试断言这些路径存在
- [x] 1.2 添加 `.gitignore`（忽略 `config/project.json`、`config/user.project.json`、`.env*`、`.idea`、`.venv`、`node_modules`、`dist`、`coverage`、缓存、`docs/.vitepress/cache`、`docs/.vitepress/dist`、`apps/backend/var`、SQLite 与日志），并用测试验证 template 不被忽略、本机配置被忽略
- [x] 1.3 提交空的 `config/project.template.json` 与 `config/user.project.template.json`，并用测试确认所有 key/secret/password 为空

## 2. 配置加载与前端 allowlist

- [x] 2.1 实现后端通用 JSON 深合并加载（`project.json` + `user.project.json`），用临时配置测试覆盖嵌套字段，并证明不读取 OS 环境变量作为项目配置
- [x] 2.2 实现前端构建期 public-config allowlist（仅 `frontend.title`、`frontend.apiBaseUrl`、明确 public 的 analytics key），并验证运行时代码不能 import 完整 JSON
- [x] 2.3 用 sentinel secret 执行前端 build 后扫描 `dist`，验证 LLM/CLS/MCP/MinIO secret 不在产物中

## 3. 后端骨架与质量工具

- [x] 3.1 添加 backend `pyproject.toml`（Python>=3.10、hatchling src layout、FastAPI、Pydantic v2、锁定的数据层与质量工具、Ruff/Pyright/pytest-asyncio=auto），生成后在 `apps/backend` 执行 `uv sync` 并确认 `uv.lock` 存在
- [x] 3.2 实现 `apps/backend/src/super_ai` 包、应用工厂与 `/health`，并用测试证明 `from super_ai...` 可用、不存在 `src.super_ai` 导入、import 期间不连接 SQLite/Milvus/LLM/MCP
- [x] 3.3 使 backend `uv run ruff check .`、`uv run pyright`、`uv run pytest` 全部通过

## 4. 合约、前端与根工作区

- [x] 4.1 建立 `packages/api-contracts` typed entrypoint 与最小 foundation 类型，并让 typecheck/test 通过
- [x] 4.2 建立 Vue 3.5 / Vite 6 / TS 5.6 strict / Pinia 3 / Vue Router 4 / Vitest 2 桌面 Web 骨架及 dev/typecheck/test/build scripts
- [x] 4.3 建立根 `package.json` workspaces、docs VitePress 骨架，执行根 `npm install`，并让 contracts/frontend/docs scripts 可运行

## 5. 工程指南、基础设施边界与总验收

- [x] 5.1 编写根 `AGENTS.md` 与中文 README/各 workspace README，更新 `openspec/config.yaml` 项目上下文，锁定技术栈与约束，且不声称未实现功能
- [x] 5.2 创建 `infra/` 边界说明（Compose 仅 etcd/MinIO/Milvus/Attu/Alertmanager；应用与官方 CLS MCP Server 主机运行），并确认不存在 `app.Dockerfile` 与 `project.compose.json`
- [x] 5.3 运行 `openspec validate --all` 与 `git diff --check`，确认文档不含 filter-repo/force push 清理步骤，全部门禁通过后再进入验证与归档
