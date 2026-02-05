"""
简化版前端部署脚本 - 将项目部署到VPS服务器
先部署后端API和Nginx，前端使用占位页面
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
DOCKER_DIR = PROJECT_ROOT / "docker"

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
    print(f"[远程] {cmd[:80]}..." if len(cmd) > 80 else f"[远程] {cmd}")
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


def setup_server(client: paramiko.SSHClient):
    """配置服务器环境"""
    print("\n" + "=" * 50)
    print("步骤 1: 配置服务器环境")
    print("=" * 50)

    # 检查并安装 Docker
    print("\n[服务器] 检查 Docker 安装...")
    exit_code, _, _ = exec_remote(client, "docker --version", check=False)
    if exit_code != 0:
        print("[服务器] Docker 未安装，正在安装...")
        # 安装 Docker
        exec_remote(client, "apt-get update -y")
        exec_remote(client, "apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release")
        exec_remote(client, "curl -fsSL https://get.docker.com | sh", check=False)
        exec_remote(client, "systemctl start docker")
        exec_remote(client, "systemctl enable docker")
        print("[服务器] Docker 安装完成")

    # 检查并安装 Docker Compose
    print("\n[服务器] 检查 Docker Compose...")
    exit_code, _, _ = exec_remote(client, "docker compose version", check=False)
    if exit_code != 0:
        exit_code, _, _ = exec_remote(client, "docker-compose --version", check=False)
        if exit_code != 0:
            print("[服务器] 安装 Docker Compose 插件...")
            exec_remote(client, "apt-get install -y docker-compose-plugin", check=False)

    # 创建项目目录
    print("\n[服务器] 创建项目目录...")
    exec_remote(client, f"mkdir -p {REMOTE_BASE}/apps/admin/dist")
    exec_remote(client, f"mkdir -p {REMOTE_BASE}/apps/client/dist")
    exec_remote(client, f"mkdir -p {REMOTE_BASE}/apps/api")
    exec_remote(client, f"mkdir -p {REMOTE_BASE}/docker/nginx")
    exec_remote(client, f"mkdir -p {REMOTE_BASE}/database")


def deploy_files(client: paramiko.SSHClient):
    """部署文件到服务器"""
    print("\n" + "=" * 50)
    print("步骤 2: 部署文件到服务器")
    print("=" * 50)

    sftp = client.open_sftp()

    # 上传 API 代码
    api_dir = APPS_DIR / "api"
    if api_dir.exists():
        print("\n[部署] 上传 API 后端...")
        upload_with_tar(client, api_dir, f"{REMOTE_BASE}/apps/api", "api")

    # 上传 Docker 配置
    print("\n[部署] 上传 Docker 配置...")

    nginx_conf = DOCKER_DIR / "nginx" / "nginx.conf"
    if nginx_conf.exists():
        sftp.put(str(nginx_conf), f"{REMOTE_BASE}/docker/nginx/nginx.conf")

    dockerfile = DOCKER_DIR / "Dockerfile.api"
    if dockerfile.exists():
        sftp.put(str(dockerfile), f"{REMOTE_BASE}/docker/Dockerfile.api")

    compose_file = DOCKER_DIR / "docker-compose.prod.yml"
    if compose_file.exists():
        sftp.put(str(compose_file), f"{REMOTE_BASE}/docker/docker-compose.prod.yml")

    # 上传数据库迁移文件
    print("\n[部署] 上传数据库文件...")
    db_dir = PROJECT_ROOT / "database"
    if db_dir.exists():
        upload_with_tar(client, db_dir, f"{REMOTE_BASE}/database", "database")

    sftp.close()


def create_placeholder_pages(client: paramiko.SSHClient):
    """创建占位页面"""
    print("\n[配置] 创建前端占位页面...")

    # Client 占位页面
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
        .container {
            text-align: center;
            color: white;
            padding: 40px;
        }
        .logo { font-size: 64px; margin-bottom: 20px; }
        h1 { font-size: 32px; margin-bottom: 10px; }
        .subtitle { font-size: 18px; opacity: 0.9; margin-bottom: 30px; }
        .status {
            background: rgba(255,255,255,0.2);
            padding: 15px 30px;
            border-radius: 30px;
            display: inline-block;
        }
        .features {
            margin-top: 40px;
            display: flex;
            gap: 20px;
            justify-content: center;
            flex-wrap: wrap;
        }
        .feature {
            background: rgba(255,255,255,0.15);
            padding: 20px;
            border-radius: 15px;
            width: 150px;
        }
        .feature-icon { font-size: 32px; margin-bottom: 10px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">🏃</div>
        <h1>易乐航·乐航成长</h1>
        <p class="subtitle">ITS智慧体教云平台 - 学员/家长端</p>
        <div class="status">🚀 系统部署中...</div>
        <div class="features">
            <div class="feature">
                <div class="feature-icon">📊</div>
                <div>成长档案</div>
            </div>
            <div class="feature">
                <div class="feature-icon">🤖</div>
                <div>AI陪练</div>
            </div>
            <div class="feature">
                <div class="feature-icon">📅</div>
                <div>课程预约</div>
            </div>
            <div class="feature">
                <div class="feature-icon">📝</div>
                <div>作业打卡</div>
            </div>
        </div>
    </div>
</body>
</html>'''

    # Admin 占位页面
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
        .container {
            text-align: center;
            color: white;
            padding: 40px;
        }
        .logo { font-size: 64px; margin-bottom: 20px; }
        h1 { font-size: 32px; margin-bottom: 10px; }
        .subtitle { font-size: 18px; opacity: 0.9; margin-bottom: 30px; }
        .status {
            background: rgba(102, 126, 234, 0.3);
            padding: 15px 30px;
            border-radius: 30px;
            display: inline-block;
            border: 1px solid rgba(102, 126, 234, 0.5);
        }
        .modules {
            margin-top: 40px;
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 15px;
            max-width: 500px;
        }
        .module {
            background: rgba(255,255,255,0.1);
            padding: 20px 15px;
            border-radius: 10px;
        }
        .module-icon { font-size: 28px; margin-bottom: 8px; }
        .module-name { font-size: 14px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">⚙️</div>
        <h1>易乐航·管理后台</h1>
        <p class="subtitle">ITS智慧体教云平台 - 运营管理系统</p>
        <div class="status">🔧 系统部署中...</div>
        <div class="modules">
            <div class="module">
                <div class="module-icon">👥</div>
                <div class="module-name">用户管理</div>
            </div>
            <div class="module">
                <div class="module-icon">📚</div>
                <div class="module-name">课程管理</div>
            </div>
            <div class="module">
                <div class="module-icon">📅</div>
                <div class="module-name">排课系统</div>
            </div>
            <div class="module">
                <div class="module-icon">💰</div>
                <div class="module-name">财务中心</div>
            </div>
            <div class="module">
                <div class="module-icon">📊</div>
                <div class="module-name">数据分析</div>
            </div>
            <div class="module">
                <div class="module-icon">🔔</div>
                <div class="module-name">消息通知</div>
            </div>
        </div>
    </div>
</body>
</html>'''

    exec_remote(client, f"cat > {REMOTE_BASE}/apps/client/dist/index.html << 'HTML_EOF'\n{client_html}\nHTML_EOF")
    exec_remote(client, f"cat > {REMOTE_BASE}/apps/admin/dist/index.html << 'HTML_EOF'\n{admin_html}\nHTML_EOF")


def create_configs(client: paramiko.SSHClient):
    """创建配置文件"""
    print("\n[配置] 创建 Nginx 配置...")

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

    exec_remote(client, f"cat > {REMOTE_BASE}/docker/nginx/nginx.conf << 'NGINX_EOF'\n{nginx_config}\nNGINX_EOF")

    print("\n[配置] 创建 Docker Compose 配置...")

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
      - postgres_data:/var/lib/postgresql/data
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
      - redis_data:/data
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
      SECRET_KEY: yilehang-secret-key-2024
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
    depends_on:
      - api
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:'''

    exec_remote(client, f"cat > {REMOTE_BASE}/docker/docker-compose.prod.yml << 'COMPOSE_EOF'\n{compose_config}\nCOMPOSE_EOF")


def start_services(client: paramiko.SSHClient):
    """启动服务"""
    print("\n" + "=" * 50)
    print("步骤 3: 启动服务")
    print("=" * 50)

    # 检测 docker compose 命令格式
    exit_code, _, _ = exec_remote(client, "docker compose version", check=False)
    compose_cmd = "docker compose" if exit_code == 0 else "docker-compose"

    # 停止旧服务
    print("\n[服务] 停止旧服务...")
    exec_remote(client, f"cd {REMOTE_BASE}/docker && {compose_cmd} -f docker-compose.prod.yml down 2>/dev/null || true", check=False)

    # 启动新服务
    print("\n[服务] 启动服务 (这可能需要几分钟)...")
    exec_remote(client, f"cd {REMOTE_BASE}/docker && {compose_cmd} -f docker-compose.prod.yml up -d --build")

    # 等待服务启动
    print("\n[服务] 等待服务启动...")
    import time
    time.sleep(15)

    # 检查服务状态
    print("\n[服务] 检查服务状态...")
    exec_remote(client, f"cd {REMOTE_BASE}/docker && {compose_cmd} -f docker-compose.prod.yml ps")


def main():
    """主函数"""
    print("=" * 50)
    print("易乐航·ITS智慧体教云平台 - 部署脚本")
    print("=" * 50)
    print(f"目标服务器: {SERVER_USER}@{SERVER_HOST}")

    client = None
    try:
        client = create_ssh_client()

        setup_server(client)
        deploy_files(client)
        create_placeholder_pages(client)
        create_configs(client)
        start_services(client)

        print("\n" + "=" * 50)
        print("部署完成!")
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
