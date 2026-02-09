# 易乐航官网独立部署

基于 nginx:alpine 的静态官网独立部署模块。

## 目录结构

```
deploy/website/
├── Dockerfile           # 基于 nginx:alpine，打包静态文件
├── docker-compose.yml   # 独立部署编排
├── nginx.conf           # nginx 站点配置
└── README.md
```

静态文件来源：项目根目录 `website/`（index.html, help.html, assets/）

## 快速部署

在项目根目录执行：

```bash
docker compose -f deploy/website/docker-compose.yml up -d --build
```

## 停止服务

```bash
docker compose -f deploy/website/docker-compose.yml down
```

## 域名与 SSL

nginx 配置中 `server_name` 为 `www.yilehang.com yilehang.com`。

### Let's Encrypt SSL 配置

1. ACME challenge 目录已挂载为 Docker volume `acme-data`，映射到容器内 `/var/www/acme`。

2. 使用 acme.sh 签发证书（在宿主机执行）：

```bash
acme.sh --issue -d yilehang.com -d www.yilehang.com --webroot /var/lib/docker/volumes/deploy_website_acme-data/_data
```

3. 签发成功后，在 nginx.conf 中添加 443 server block 并挂载证书文件，或在宿主机使用反向代理终结 SSL。

## 构建上下文

Dockerfile 的构建上下文为项目根目录（`../..`），因此 `docker compose` 命令需在项目根目录或使用 `-f` 指定 compose 文件路径。

## 端口

| 服务 | 端口 |
|------|------|
| HTTP | 80   |

如需修改端口映射，编辑 `docker-compose.yml` 中的 `ports` 配置。
