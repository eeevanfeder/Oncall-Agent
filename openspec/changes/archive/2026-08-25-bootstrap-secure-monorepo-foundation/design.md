## Context

仓库已完成 `git init` 与 OpenSpec 初始化，仅有默认 `openspec/config.yaml` 与 Cursor 工作流文件，没有应用代码。动机见 `proposal.md` 的 Why。本设计把第一提案的技术栈、目录骨架和安全配置边界一次锁定，避免后续提案各自发明布局。

## Goals / Non-Goals

**Goals:**

- 用最终目录与包导入规则搭好单仓，而不是临时目录。
- 用模板 + `.gitignore` + 深合并加载从第一天隔离密钥。
- 前端构建只注入 public allowlist，用 sentinel 扫描证明 secret 不进 bundle。
- 用最小 `/health` 与桌面 Web 骨架跑通质量命令。

**Non-Goals:**

- 不实现认证、聊天、知识库、AIOps、MCP、LLM provider typed validation（后者属后续 P06）。
- 不把 Agent/AI 运行时依赖装进本提案可运行骨架。
- 不创建应用 Docker/Compose 服务，不设计 filter-repo/force push。
- 不把 OS 环境变量当作项目配置源。

## Decisions

### 决策：锁定技术栈（必须写入本文件与项目指南）

**后端**

- Python >=3.10、FastAPI、Pydantic v2、uv、hatchling、src layout
- SQLAlchemy 2 async、aiosqlite、Alembic（依赖可列入 pyproject 以锁定版本，本提案不实现连接与迁移运行）
- pytest、pytest-asyncio（`asyncio_mode=auto`）、Ruff、strict Pyright
- Ruff：`line-length=100`、`target-version=py310`、规则 `B/E/F/I/UP`

**Agent/AI（后续提案实现，本提案只锁定名称）**

- LangChain 1.x `create_agent`、LangGraph、langchain-openai、langchain-mcp-adapters、MCP
- pymilvus 3、rank-bm25、pypdf、langchain-text-splitters、httpx

**前端**

- Vue 3.5、Vite 6、TypeScript 5.6 strict
- `exactOptionalPropertyTypes`、`noUncheckedIndexedAccess`、`isolatedModules`
- `module`/`moduleResolution` 为 ES2022 / Bundler
- Pinia 3、Vue Router 4、Vitest 2、marked、DOMPurify、lucide-vue-next

**仓库**

- npm workspaces、OpenSpec spec-driven、VitePress 文档、Conventional Commits

备选：Poetry + 后端独立仓、或 pnpm。否决原因：提案已指定 uv + npm workspaces，且第一提案必须一次锁死，避免二次搬迁。

### 决策：后端包名与 import-safety

包路径为 `apps/backend/src/super_ai`。hatchling 配置 `package-dir` / `packages`，使 `from super_ai...` 成为唯一合法导入。静态测试扫描 `from src.super_ai` 与 `import src.super_ai`。应用工厂与配置加载不得在模块顶层打开 SQLite、Milvus、LLM 或 MCP。

备选：包名用仓库目录名。否决：提案明确要求 `super_ai`。

### 决策：通用 JSON 深合并，而不是环境变量

加载顺序：`config/project.json` 为基座，`config/user.project.json` 递归深合并覆盖。对象递归合并，数组与标量整段替换。缺失的本机文件视为空对象。测试通过临时目录注入配置，生产函数接受显式路径参数，默认指向仓库 `config/`。

应用不读取 `os.environ` 作为项目配置。本机可从 template 复制 ignored 空文件以便 build，但不得 stage。

备选：12-factor 环境变量。否决：提案要求只读本地 JSON，且密钥不能进 Git/CI 日志。

### 决策：前端 public-config allowlist

`vite.config.ts` 在构建时读取与后端相同的深合并结果，但只通过 `define` 或 virtual module 注入：

- `frontend.title`
- `frontend.apiBaseUrl`
- 明确标记为 public 的 analytics key（例如 `frontend.analytics.publicKey`，且源字段带 `public` 语义）

LLM、CLS、MCP、MinIO secret 永不注入。前端源码不得 `import` 完整 JSON。测试用 sentinel 值构建后扫描 `apps/frontend/dist`。

备选：运行时请求后端 `/config`。否决：本提案没有认证与后端配置 API，桌面 Web 骨架只需构建期公开字段。

### 决策：基础设施只建边界

`infra/README.md` 写明 Compose 最终只托管 etcd、MinIO、Milvus、Attu、Alertmanager；后端、前端、官方 CLS MCP Server 在主机运行。可放空的 `infra/compose/` 占位目录与说明，但不写应用服务、不创建 `app.Dockerfile`、不创建 `project.compose.json`。

### 决策：质量命令与安装顺序

P01 生成 package/pyproject 后立即：

1. 根目录 `npm install`
2. `apps/backend` 下 `uv sync`

验收命令：

- `openspec validate --all`
- `uv run ruff check .`、`uv run pyright`、`uv run pytest`（在 backend）
- contracts `typecheck` / `test`
- frontend `typecheck` / `test` / `build`
- `git diff --check`

## Risks / Trade-offs

- [本机缺 `project.json` 导致 frontend build 失败] → 模板复制脚本写入 ignored 空文件；测试使用临时配置，不依赖开发者文件。
- [SQLAlchemy/Alembic 列入依赖但无迁移] → 文档明确“锁定依赖，不在本提案连接数据库”；import-safety 测试防止隐式连接。
- [Agent/AI 名称写入指南但未安装] → README/AGENTS 明确“后续提案实现”，避免使用者以为可运行。
- [VitePress 尚未有产品文档] → 只放骨架首页，说明仓库结构与验证命令。

## Migration Plan

全新仓库，无运行中服务。落地顺序：目录与忽略规则 → 配置模板与加载器 → 后端/前端/contracts 骨架 → 安装依赖 → 质量门禁 → 归档同步主 specs。回滚即删除本提案新增文件，无需数据迁移，也无需 force push。
