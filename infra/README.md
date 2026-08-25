# 基础设施边界

本目录只锁定职责，不在本提案运行应用容器。

## Compose 最终托管

- etcd
- MinIO
- Milvus
- Attu
- Alertmanager

## 必须在主机运行

- 后端
- 前端
- 官方 CLS MCP Server

不要在此添加应用 Compose 服务，也不要创建应用容器构建文件。
