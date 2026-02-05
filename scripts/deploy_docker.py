"""
Docker方式部署脚本 - 将项目部署到VPS服务器
使用独立端口8088，不影响服务器其他服务
"""
import os
import sys
import subprocess
import tarfile
import tempfile
from pathlib import Path

try:
    import paramiko
except ImportError:
    print("正在安装 paramiko...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "paramiko"])
    import paramiko


# 服务器配置
SERVER_HOST = "8.134.33.19"
SERVER_USER = "root"
SERVER_PASSWORD = "Qq159741"
SERVER_PORT = 22

# 项目路径
PROJECT_ROOT = Path(__file__).parent.parent
APPS_DIR = PROJECT_ROOT / "apps"

# 远程路径
REMOTE_BASE = "/opt/yilehang"


def create_ssh_client() -> paramiko.SSHClient:
    """创建SSH客户端"""
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print(f"[SSH] 连接到 {SERVER_USER}@{SERVER_HOST}:{SERVER_PORT}")
    client.connect(
        hostname=SERVER_HOST,
        port=SERVER_PORT,
        username=SERVER_USER,
        password=SERVER_PASSWORD,
        timeout=30
    )
    print("[SSH] 连接成功")
    return client


def exec_remote(client: paramiko.SSHClient, cmd: str, check: bool = True) -> tuple:
    """执行远程命令"""
    print(f"[远程] {cmd[:100]}..." if len(cmd) > 100 else f"[远程] {cmd}")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=600)
    exit_code = stdout.channel.recv_exit_status()
    out = stdout.read().decode('utf-8', errors='ignore')
    err = stderr.read().decode('utf-8', errors='ignore')

    if out and len(out) < 2000:
        print(out)
    if err and exit_code != 0:
        print(f"[错误] {err[:500]}")

    if check and exit_code != 0:
        raise Exception(f"命令执行失败 (exit={exit_code}): {cmd[:100]}")

    return exit_code, out, err


def upload_with_tar(client: paramiko.SSHClient, local_path: Path, remote_path: str, name: str):
    """使用tar压缩上传"""
    print(f"[打包上传] {local_path.name} -> {remote_path}")

    with tempfile.NamedTemporaryFile(suffix='.tar.gz', delete=False) as tmp:
        tar_path = tmp.name

    try:
        with tarfile.open(tar_path, 'w:gz') as tar:
            tar.add(local_path, arcname=name)

        sftp = client.open_sftp()
        remote_tar = f"/tmp/{name}.tar.gz"
        print(f"  上传中...")
        sftp.put(tar_path, remote_tar)
        sftp.close()

        exec_remote(client, f"mkdir -p {remote_path}")
        exec_remote(client, f"tar -xzf {remote_tar} -C {remote_path} --strip-components=1")
        exec_remote(client, f"rm -f {remote_tar}")
        print(f"  完成")

    finally:
        if os.path.exists(tar_path):
            os.remove(tar_path)


def cleanup_old_deployment(client: paramiko.SSHClient):
    """清理旧的部署残留"""
    print("\n" + "=" * 50)
    print("步骤 0: 清理旧部署残留")
    print("=" * 50)

    # 停止并删除旧容器
    print("\n[清理] 停止旧的Docker容器...")
    exec_remote(client, "docker stop yilehang-nginx yilehang-api yilehang-postgres yilehang-redis 2>/dev/null || true", check=False)
    exec_remote(client, "docker rm yilehang-nginx yilehang-api yilehang-postgres yilehang-redis 2>/dev/null || true", check=False)

    # 删除旧的项目目录
    print("\n[清理] 删除旧的项目目录...")
    exec_remote(client, f"rm -rf {REMOTE_BASE}", check=False)

    print("[清理] 清理完成")


def setup_docker(client: paramiko.SSHClient):
    """配置Docker环境"""
    print("\n" + "=" * 50)
    print("步骤 1: 配置Docker环境")
    print("=" * 50)

    # 检查Docker是否安装
    print("\n[Docker] 检查Docker安装...")
    exit_code, _, _ = exec_remote(client, "docker --version", check=False)
    if exit_code != 0:
        print("[Docker] Docker未安装，正在安装...")
        exec_remote(client, "apt-get update -y")
        exec_remote(client, "apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release")
        exec_remote(client, "curl -fsSL https://get.docker.com | sh")
        exec_remote(client, "systemctl start docker")
        exec_remote(client, "systemctl enable docker")
        print("[Docker] Docker安装完成")
    else:
        print("[Docker] Docker已安装")

    # 安装docker-compose独立版本
    print("\n[Docker] 安装docker-compose...")
    exec_remote(client, "apt-get update -y && apt-get install -y docker-compose", check=False)

    # 安装buildx插件
    print("\n[Docker] 安装Docker Buildx插件...")
    exec_remote(client, "mkdir -p ~/.docker/cli-plugins", check=False)
    exec_remote(client, "curl -SL https://github.com/docker/buildx/releases/download/v0.12.1/buildx-v0.12.1.linux-amd64 -o ~/.docker/cli-plugins/docker-buildx", check=False)
    exec_remote(client, "chmod +x ~/.docker/cli-plugins/docker-buildx", check=False)

    # 创建项目目录
    print("\n[目录] 创建项目目录...")
    exec_remote(client, f"mkdir -p {REMOTE_BASE}/apps/admin/dist")
    exec_remote(client, f"mkdir -p {REMOTE_BASE}/apps/client/dist")
    exec_remote(client, f"mkdir -p {REMOTE_BASE}/apps/api")
    exec_remote(client, f"mkdir -p {REMOTE_BASE}/docker/nginx")


def deploy_api(client: paramiko.SSHClient):
    """部署API代码"""
    print("\n" + "=" * 50)
    print("步骤 2: 部署API代码")
    print("=" * 50)

    api_dir = APPS_DIR / "api"
    if api_dir.exists():
        upload_with_tar(client, api_dir, f"{REMOTE_BASE}/apps/api", "api")


def create_docker_configs(client: paramiko.SSHClient):
    """创建Docker配置文件"""
    print("\n" + "=" * 50)
    print("步骤 3: 创建Docker配置")
    print("=" * 50)

    # Dockerfile for API - 使用国内镜像源
    print("\n[配置] 创建API Dockerfile...")
    dockerfile = '''FROM python:3.11-slim

WORKDIR /app

# 使用阿里云镜像源
RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list.d/debian.sources 2>/dev/null || true

RUN apt-get update && apt-get install -y \\
    gcc \\
    libpq-dev \\
    && rm -rf /var/lib/apt/lists/*

# 使用国内pip镜像
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

COPY pyproject.toml .

RUN pip install --no-cache-dir pip -U && \\
    pip install --no-cache-dir .

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
'''
    exec_remote(client, f"cat > {REMOTE_BASE}/docker/Dockerfile.api << 'EOF'\n{dockerfile}\nEOF")

    # Nginx配置
    print("\n[配置] 创建Nginx配置...")
    nginx_config = '''events {
    worker_connections 1024;
}

http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;

    sendfile        on;
    keepalive_timeout  65;

    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml;

    upstream api {
        server api:8000;
    }

    server {
        listen 80;
        server_name _;

        location /api {
            proxy_pass http://api;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        location /docs {
            proxy_pass http://api/docs;
            proxy_set_header Host $host;
        }

        location /redoc {
            proxy_pass http://api/redoc;
            proxy_set_header Host $host;
        }

        location /openapi.json {
            proxy_pass http://api/openapi.json;
            proxy_set_header Host $host;
        }

        location /admin {
            alias /usr/share/nginx/html/admin;
            try_files $uri $uri/ /admin/index.html;
        }

        location / {
            root /usr/share/nginx/html/client;
            try_files $uri $uri/ /index.html;
        }
    }
}'''
    exec_remote(client, f"cat > {REMOTE_BASE}/docker/nginx/nginx.conf << 'EOF'\n{nginx_config}\nEOF")

    # Docker Compose配置 - 使用8088端口
    print("\n[配置] 创建Docker Compose配置...")
    compose_config = '''version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    container_name: yilehang-postgres
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres123
      POSTGRES_DB: yilehang
    volumes:
      - yilehang_postgres_data:/var/lib/postgresql/data
    networks:
      - yilehang_network
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: yilehang-redis
    volumes:
      - yilehang_redis_data:/data
    networks:
      - yilehang_network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  api:
    build:
      context: ../apps/api
      dockerfile: /opt/yilehang/docker/Dockerfile.api
    container_name: yilehang-api
    environment:
      DATABASE_URL: postgresql+asyncpg://postgres:postgres123@postgres:5432/yilehang
      REDIS_URL: redis://redis:6379/0
      DEBUG: "false"
      SECRET_KEY: yilehang-secret-key-2024-prod
    networks:
      - yilehang_network
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    container_name: yilehang-nginx
    ports:
      - "8088:80"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ../apps/client/dist:/usr/share/nginx/html/client:ro
      - ../apps/admin/dist:/usr/share/nginx/html/admin:ro
    networks:
      - yilehang_network
    depends_on:
      - api
    restart: unless-stopped

networks:
  yilehang_network:
    name: yilehang_network

volumes:
  yilehang_postgres_data:
  yilehang_redis_data:'''
    exec_remote(client, f"cat > {REMOTE_BASE}/docker/docker-compose.yml << 'EOF'\n{compose_config}\nEOF")


def create_placeholder_pages(client: paramiko.SSHClient):
    """创建占位页面"""
    print("\n[配置] 创建前端占位页面...")

    client_html = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>易乐航·乐航成长</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .container { text-align: center; color: white; padding: 40px; }
        .logo { font-size: 64px; margin-bottom: 20px; }
        h1 { font-size: 32px; margin-bottom: 10px; }
        .subtitle { font-size: 18px; opacity: 0.9; margin-bottom: 30px; }
        .status { background: rgba(255,255,255,0.2); padding: 15px 30px; border-radius: 30px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">🏃</div>
        <h1>易乐航·乐航成长</h1>
        <p class="subtitle">ITS智慧体教云平台 - 学员/家长端</p>
        <div class="status">✅ 后端服务已部署</div>
    </div>
</body>
</html>'''

    admin_html = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>易乐航·管理后台</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .container { text-align: center; color: white; padding: 40px; }
        .logo { font-size: 64px; margin-bottom: 20px; }
        h1 { font-size: 32px; margin-bottom: 10px; }
        .subtitle { font-size: 18px; opacity: 0.9; margin-bottom: 30px; }
        .status { background: rgba(102, 126, 234, 0.3); padding: 15px 30px; border-radius: 30px; border: 1px solid rgba(102, 126, 234, 0.5); }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">⚙️</div>
        <h1>易乐航·管理后台</h1>
        <p class="subtitle">ITS智慧体教云平台 - 运营管理系统</p>
        <div class="status">✅ 后端服务已部署</div>
    </div>
</body>
</html>'''

    exec_remote(client, f"cat > {REMOTE_BASE}/apps/client/dist/index.html << 'EOF'\n{client_html}\nEOF")
    exec_remote(client, f"cat > {REMOTE_BASE}/apps/admin/dist/index.html << 'EOF'\n{admin_html}\nEOF")


def start_services(client: paramiko.SSHClient):
    """启动Docker服务"""
    print("\n" + "=" * 50)
    print("步骤 4: 启动Docker服务")
    print("=" * 50)

    # 检测docker compose命令格式
    exit_code, _, _ = exec_remote(client, "docker compose version", check=False)
    compose_cmd = "docker compose" if exit_code == 0 else "docker-compose"

    # 启动服务
    print("\n[服务] 构建并启动服务 (这可能需要几分钟)...")
    exec_remote(client, f"cd {REMOTE_BASE}/docker && {compose_cmd} up -d --build")

    # 等待服务启动
    print("\n[服务] 等待服务启动...")
    import time
    time.sleep(20)

    # 检查服务状态
    print("\n[服务] 检查服务状态...")
    exec_remote(client, f"cd {REMOTE_BASE}/docker && {compose_cmd} ps")

    # 检查API健康状态
    print("\n[服务] 检查API健康状态...")
    exec_remote(client, "curl -s http://localhost:8088/docs > /dev/null && echo 'API服务正常' || echo 'API服务异常'", check=False)


def main():
    """主函数"""
    print("=" * 50)
    print("易乐航·ITS智慧体教云平台 - Docker部署")
    print("=" * 50)
    print(f"目标服务器: {SERVER_USER}@{SERVER_HOST}")
    print(f"服务端口: 8088 (不影响其他服务)")

    client = None
    try:
        client = create_ssh_client()

        cleanup_old_deployment(client)
        setup_docker(client)
        deploy_api(client)
        create_docker_configs(client)
        create_placeholder_pages(client)
        start_services(client)

        print("\n" + "=" * 50)
        print("🎉 部署完成!")
        print("=" * 50)
        print(f"访问地址:")
        print(f"  - 客户端: http://{SERVER_HOST}:8088/")
        print(f"  - 管理后台: http://{SERVER_HOST}:8088/admin")
        print(f"  - API文档: http://{SERVER_HOST}:8088/docs")

    except Exception as e:
        print(f"\n[错误] 部署失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        if client:
            client.close()


if __name__ == "__main__":
    main()
