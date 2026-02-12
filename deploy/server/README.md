# 韧翎成长计划 - 服务端独立部署

本目录包含服务端（FastAPI + PostgreSQL + Nginx）的独立部署配置。

## 目录结构

```
deploy/server/
├── docker-compose.yml   # 编排：API + PostgreSQL + Nginx
├── Dockerfile           # API 镜像构建
├── nginx.conf           # Nginx 配置（仅代理 API）
├── .env.example         # 环境变量模板
└── README.md            # 本文件
```

## 快速开始

### 1. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env，填入实际的数据库密码、SECRET_KEY、微信配置等
```

### 2. 启动服务

```bash
cd deploy/server
docker compose up -d --build
```

### 3. 初始化数据库（首次部署）

```bash
# 运行数据库迁移
docker compose exec api alembic upgrade head

# （可选）导入测试数据
docker compose exec api python -m scripts.seed_data
docker compose exec api python -m scripts.seed_role_permissions
```

### 4. 验证

```bash
# 健康检查
curl http://localhost/health

# API 文档
# Swagger UI: http://localhost/docs
# ReDoc:      http://localhost/redoc
```

## 服务说明

| 服务 | 容器名 | 端口 | 说明 |
|------|--------|------|------|
| PostgreSQL | yilehang-server-postgres | 内部 5432（不暴露） | 数据库 |
| FastAPI | yilehang-server-api | 8001:8000 | API 服务 |
| Nginx | yilehang-server-nginx | 80:80 | 反向代理 |

## Nginx 代理路由

| 路径 | 目标 |
|------|------|
| `/api/*` | FastAPI API 接口 |
| `/docs` | Swagger UI 文档 |
| `/redoc` | ReDoc 文档 |
| `/openapi.json` | OpenAPI Schema |
| `/health` | 健康检查 |
| `/uploads/*` | 上传文件 |

## 常用命令

```bash
# 查看日志
docker compose logs -f api

# 重启 API
docker compose restart api

# 停止所有服务
docker compose down

# 停止并清除数据卷（危险：会删除数据库数据）
docker compose down -v

# 重新构建 API 镜像
docker compose build api
```

## 生产环境建议

1. **必须修改** `.env` 中的 `POSTGRES_PASSWORD` 和 `SECRET_KEY`
2. 如需 HTTPS，在 Nginx 前加一层带 SSL 证书的反向代理，或修改 `nginx.conf` 添加 SSL 配置
3. 定期备份 PostgreSQL 数据卷
4. 建议配置日志收集和监控
