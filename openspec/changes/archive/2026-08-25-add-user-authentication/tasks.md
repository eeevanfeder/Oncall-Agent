## 1. 合同（先写测试）

- [x] 1.1 先写合同验收测试：Auth DTO、`AUTH_INVALID_CREDENTIALS`、bearer、认证 path；再扩展 catalog / OpenAPI / TypeScript 类型

## 2. 后端（先写测试）

- [x] 2.1 先写后端验收测试：迁移、注册、重复邮箱、正确/错误登录、哈希非明文、库中无 raw token、lastSeen、撤销、`/auth/me`、统一错误
- [x] 2.2 实现 users/auth_sessions 迁移、owner-safe Repository、AuthService（Argon2、dummy 校验、token hash）与 FastAPI 依赖/路由/CORS

## 3. 前端（先写测试）

- [x] 3.1 先写前端验收测试：token 唯一入库、initialize 调 `/auth/me`、失效与 logout 清理本地且不删服务端数据
- [x] 3.2 实现 `authClient` 与 auth store；不实现完整页面

## 4. 指南与验收

- [x] 4.1 更新 `AGENTS.md` 与 README：认证 API 已落地，完整页面与其它产品能力未实现
- [x] 4.2 运行受影响的 backend/contracts/frontend 门禁、`openspec validate --all`、`git diff --check`，通过后验证并归档
