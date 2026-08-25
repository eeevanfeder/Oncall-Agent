# secure-config Specification

## Purpose

从第一天锁定可提交配置模板、忽略规则和深合并加载行为，确保密钥不会进入 Git 或浏览器 bundle，并让测试不依赖开发者本机真实配置。

## Requirements

### Requirement: 只提交空配置模板

仓库 MUST 只提交 `config/project.template.json` 与 `config/user.project.template.json`。模板中所有 key、secret、password 字段 MUST 为空。仓库 MUST NOT 提交 `config/project.json` 或 `config/user.project.json`。

#### Scenario: 模板可提交且密钥为空

- **WHEN** 检查已跟踪的配置文件
- **THEN** 仅存在两份 template，且其中 key/secret/password 均为空字符串或空对象

#### Scenario: 本机配置未被跟踪

- **WHEN** 工作区从模板复制出 `config/project.json` 或 `config/user.project.json` 供本地 build 使用
- **THEN** 这些文件保持被忽略状态，且 MUST NOT 被 stage

### Requirement: 忽略密钥、产物与本地状态

`.gitignore` MUST 忽略 `config/project.json`、`config/user.project.json`、`.env*`、`.idea`、`.venv`、`node_modules`、`dist`、`coverage`、缓存目录、`docs/.vitepress/cache`、`docs/.vitepress/dist`、`apps/backend/var`、SQLite 文件与日志文件。最小测试 MUST 覆盖这些忽略规则。

#### Scenario: 忽略规则生效

- **WHEN** 运行忽略规则测试
- **THEN** 上述路径均被识别为忽略，且 template 文件不被忽略

### Requirement: 后端递归深合并加载本地 JSON

后端 MUST 提供通用 JSON 配置加载：先读取 `project.json`，再以 `user.project.json` 做递归深合并。应用 MUST 只使用该深合并结果作为项目配置，MUST NOT 把 OS 环境变量当作项目配置来源。测试 MUST 通过临时配置注入，不得读取开发者真实本机值。后续 LLM typed validation/provider MUST 留到独立提案，本提案只提供通用加载。

#### Scenario: 用户配置覆盖嵌套字段

- **WHEN** 测试注入临时 `project.json` 与部分覆盖的 `user.project.json`
- **THEN** 加载结果对重叠键使用用户值，并保留未覆盖的嵌套字段

#### Scenario: 不读取操作系统环境变量

- **WHEN** 操作系统中存在同名环境变量，且临时 JSON 配置为另一组值
- **THEN** 应用配置结果等于 JSON 深合并，而不采用环境变量

### Requirement: 前端只注入 public allowlist

前端 MUST NOT 直接 import 两份完整项目 JSON。构建期可以读取深合并配置，但 MUST 只通过 define 或 virtual module 向运行时代码注入 allowlist 字段：`frontend.title`、`frontend.apiBaseUrl`，以及明确标记为 public 的 analytics key。LLM、CLS、MCP、MinIO secret MUST NEVER 进入浏览器 bundle。最小测试 MUST 用 sentinel secret 构建后扫描 `dist`，证明这些 secret 不存在。

#### Scenario: 运行时只能看到 allowlist

- **WHEN** 前端运行时代码读取公开配置
- **THEN** 仅能获得 allowlist 字段，不能获得完整项目 JSON

#### Scenario: 构建产物不含 sentinel secret

- **WHEN** 用含 sentinel secret 的临时配置执行前端 build，并扫描 `dist`
- **THEN** LLM、CLS、MCP、MinIO 的 sentinel 值均不出现在产物中

### Requirement: 禁止历史改写步骤

从零项目 MUST NOT 设计或文档化 `git filter-repo` 或 force push 作为配置安全方案。安全边界 MUST 依赖忽略规则与模板，而不是改写已发布历史。

#### Scenario: 文档不含破坏性历史改写

- **WHEN** 检查本提案引入的工程文档与脚本说明
- **THEN** 不存在将 filter-repo 或 force push 作为密钥清理步骤的指引
