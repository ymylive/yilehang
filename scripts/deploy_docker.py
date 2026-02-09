"""
Docker鏂瑰紡閮ㄧ讲鑴氭湰 - 灏嗛」鐩儴缃插埌VPS鏈嶅姟鍣?浣跨敤鐙珛绔彛8088锛屼笉褰卞搷鏈嶅姟鍣ㄥ叾浠栨湇鍔?"""
import os
import sys
import subprocess
import tarfile
import tempfile
from pathlib import Path

try:
    import paramiko
except ImportError:
    print("姝ｅ湪瀹夎 paramiko...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "paramiko"])
    import paramiko


# 服务器配置
SERVER_HOST = os.getenv("SERVER_HOST", "82.158.88.34")
SERVER_USER = os.getenv("SERVER_USER", "root")
SERVER_PASSWORD = os.getenv("SERVER_PASSWORD")
SERVER_PORT = int(os.getenv("SERVER_PORT", "22"))

if not SERVER_PASSWORD:
    print("错误: 必须设置 SERVER_PASSWORD 环境变量")
    print("使用方法: export SERVER_PASSWORD='your-password' && python deploy_docker.py")
    sys.exit(1)

# 椤圭洰璺緞
PROJECT_ROOT = Path(__file__).parent.parent
APPS_DIR = PROJECT_ROOT / "apps"

# 杩滅▼璺緞
REMOTE_BASE = "/opt/yilehang"


def create_ssh_client() -> paramiko.SSHClient:
    """鍒涘缓SSH瀹㈡埛绔?""
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print(f"[SSH] 杩炴帴鍒?{SERVER_USER}@{SERVER_HOST}:{SERVER_PORT}")
    client.connect(
        hostname=SERVER_HOST,
        port=SERVER_PORT,
        username=SERVER_USER,
        password=SERVER_PASSWORD,
        timeout=30
    )
    print("[SSH] 杩炴帴鎴愬姛")
    return client


def exec_remote(client: paramiko.SSHClient, cmd: str, check: bool = True) -> tuple:
    """鎵ц杩滅▼鍛戒护"""
    print(f"[杩滅▼] {cmd[:100]}..." if len(cmd) > 100 else f"[杩滅▼] {cmd}")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=600)
    exit_code = stdout.channel.recv_exit_status()
    out = stdout.read().decode('utf-8', errors='ignore')
    err = stderr.read().decode('utf-8', errors='ignore')

    if out and len(out) < 2000:
        print(out)
    if err and exit_code != 0:
        print(f"[閿欒] {err[:500]}")

    if check and exit_code != 0:
        raise Exception(f"鍛戒护鎵ц澶辫触 (exit={exit_code}): {cmd[:100]}")

    return exit_code, out, err


def upload_with_tar(client: paramiko.SSHClient, local_path: Path, remote_path: str, name: str):
    """浣跨敤tar鍘嬬缉涓婁紶"""
    print(f"[鎵撳寘涓婁紶] {local_path.name} -> {remote_path}")

    with tempfile.NamedTemporaryFile(suffix='.tar.gz', delete=False) as tmp:
        tar_path = tmp.name

    try:
        with tarfile.open(tar_path, 'w:gz') as tar:
            tar.add(local_path, arcname=name)

        sftp = client.open_sftp()
        remote_tar = f"/tmp/{name}.tar.gz"
        print(f"  涓婁紶涓?..")
        sftp.put(tar_path, remote_tar)
        sftp.close()

        exec_remote(client, f"mkdir -p {remote_path}")
        exec_remote(client, f"tar -xzf {remote_tar} -C {remote_path} --strip-components=1")
        exec_remote(client, f"rm -f {remote_tar}")
        print(f"  瀹屾垚")

    finally:
        if os.path.exists(tar_path):
            os.remove(tar_path)


def cleanup_old_deployment(client: paramiko.SSHClient):
    """娓呯悊鏃х殑閮ㄧ讲娈嬬暀"""
    print("\n" + "=" * 50)
    print("姝ラ 0: 娓呯悊鏃ч儴缃叉畫鐣?)
    print("=" * 50)

    # 鍋滄骞跺垹闄ゆ棫瀹瑰櫒
    print("\n[娓呯悊] 鍋滄鏃х殑Docker瀹瑰櫒...")
    exec_remote(client, "docker stop yilehang-nginx yilehang-api yilehang-postgres 2>/dev/null || true", check=False)
    exec_remote(client, "docker rm yilehang-nginx yilehang-api yilehang-postgres 2>/dev/null || true", check=False)

    # 鍒犻櫎鏃х殑椤圭洰鐩綍
    print("\n[娓呯悊] 鍒犻櫎鏃х殑椤圭洰鐩綍...")
    exec_remote(client, f"rm -rf {REMOTE_BASE}", check=False)

    print("[娓呯悊] 娓呯悊瀹屾垚")


def setup_docker(client: paramiko.SSHClient):
    """閰嶇疆Docker鐜"""
    print("\n" + "=" * 50)
    print("姝ラ 1: 閰嶇疆Docker鐜")
    print("=" * 50)

    # 妫€鏌ocker鏄惁瀹夎
    print("\n[Docker] 妫€鏌ocker瀹夎...")
    exit_code, _, _ = exec_remote(client, "docker --version", check=False)
    if exit_code != 0:
        print("[Docker] Docker鏈畨瑁咃紝姝ｅ湪瀹夎...")
        exec_remote(client, "apt-get update -y")
        exec_remote(client, "apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release")
        exec_remote(client, "curl -fsSL https://get.docker.com | sh")
        exec_remote(client, "systemctl start docker")
        exec_remote(client, "systemctl enable docker")
        print("[Docker] Docker瀹夎瀹屾垚")
    else:
        print("[Docker] Docker宸插畨瑁?)

    # 瀹夎docker-compose鐙珛鐗堟湰
    print("\n[Docker] 瀹夎docker-compose...")
    exec_remote(client, "apt-get update -y && apt-get install -y docker-compose", check=False)

    # 瀹夎buildx鎻掍欢
    print("\n[Docker] 瀹夎Docker Buildx鎻掍欢...")
    exec_remote(client, "mkdir -p ~/.docker/cli-plugins", check=False)
    exec_remote(client, "curl -SL https://github.com/docker/buildx/releases/download/v0.12.1/buildx-v0.12.1.linux-amd64 -o ~/.docker/cli-plugins/docker-buildx", check=False)
    exec_remote(client, "chmod +x ~/.docker/cli-plugins/docker-buildx", check=False)

    # 鍒涘缓椤圭洰鐩綍
    print("\n[鐩綍] 鍒涘缓椤圭洰鐩綍...")
    exec_remote(client, f"mkdir -p {REMOTE_BASE}/apps/admin/dist")
    exec_remote(client, f"mkdir -p {REMOTE_BASE}/apps/client/dist")
    exec_remote(client, f"mkdir -p {REMOTE_BASE}/apps/api")
    exec_remote(client, f"mkdir -p {REMOTE_BASE}/docker/nginx")


def deploy_api(client: paramiko.SSHClient):
    """閮ㄧ讲API浠ｇ爜"""
    print("\n" + "=" * 50)
    print("姝ラ 2: 閮ㄧ讲API浠ｇ爜")
    print("=" * 50)

    api_dir = APPS_DIR / "api"
    if api_dir.exists():
        upload_with_tar(client, api_dir, f"{REMOTE_BASE}/apps/api", "api")


def create_docker_configs(client: paramiko.SSHClient):
    """鍒涘缓Docker閰嶇疆鏂囦欢"""
    print("\n" + "=" * 50)
    print("姝ラ 3: 鍒涘缓Docker閰嶇疆")
    print("=" * 50)

    # Dockerfile for API - 浣跨敤鍥藉唴闀滃儚婧?    print("\n[閰嶇疆] 鍒涘缓API Dockerfile...")
    dockerfile = '''FROM python:3.11-slim

WORKDIR /app

# 浣跨敤闃块噷浜戦暅鍍忔簮
RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list.d/debian.sources 2>/dev/null || true

RUN apt-get update && apt-get install -y \\
    gcc \\
    libpq-dev \\
    && rm -rf /var/lib/apt/lists/*

# 浣跨敤鍥藉唴pip闀滃儚
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

COPY pyproject.toml .

RUN pip install --no-cache-dir pip -U && \\
    pip install --no-cache-dir .

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
'''
    exec_remote(client, f"cat > {REMOTE_BASE}/docker/Dockerfile.api << 'EOF'\n{dockerfile}\nEOF")

    # Nginx閰嶇疆
    print("\n[閰嶇疆] 鍒涘缓Nginx閰嶇疆...")
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

    # Docker Compose閰嶇疆 - 浣跨敤8088绔彛
    print("\n[閰嶇疆] 鍒涘缓Docker Compose閰嶇疆...")
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

  api:
    build:
      context: ../apps/api
      dockerfile: /opt/yilehang/docker/Dockerfile.api
    container_name: yilehang-api
    environment:
      DATABASE_URL: postgresql+asyncpg://postgres:postgres123@postgres:5432/yilehang
      DEBUG: "false"
      SECRET_KEY: yilehang-secret-key-2024-prod
    networks:
      - yilehang_network
    depends_on:
      postgres:
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
'''
    exec_remote(client, f"cat > {REMOTE_BASE}/docker/docker-compose.yml << 'EOF'\n{compose_config}\nEOF")


def create_placeholder_pages(client: paramiko.SSHClient):
    """鍒涘缓鍗犱綅椤甸潰"""
    print("\n[閰嶇疆] 鍒涘缓鍓嶇鍗犱綅椤甸潰...")

    client_html = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>鏄撲箰鑸蜂箰鑸垚闀?/title>
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
        <div class="logo">馃弮</div>
        <h1>鏄撲箰鑸蜂箰鑸垚闀?/h1>
        <p class="subtitle">ITS鏅烘収浣撴暀浜戝钩鍙?- 瀛﹀憳/瀹堕暱绔?/p>
        <div class="status">鉁?鍚庣鏈嶅姟宸查儴缃?/div>
    </div>
</body>
</html>'''

    admin_html = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>鏄撲箰鑸风鐞嗗悗鍙?/title>
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
        <div class="logo">鈿欙笍</div>
        <h1>鏄撲箰鑸风鐞嗗悗鍙?/h1>
        <p class="subtitle">ITS鏅烘収浣撴暀浜戝钩鍙?- 杩愯惀绠＄悊绯荤粺</p>
        <div class="status">鉁?鍚庣鏈嶅姟宸查儴缃?/div>
    </div>
</body>
</html>'''

    exec_remote(client, f"cat > {REMOTE_BASE}/apps/client/dist/index.html << 'EOF'\n{client_html}\nEOF")
    exec_remote(client, f"cat > {REMOTE_BASE}/apps/admin/dist/index.html << 'EOF'\n{admin_html}\nEOF")


def start_services(client: paramiko.SSHClient):
    """鍚姩Docker鏈嶅姟"""
    print("\n" + "=" * 50)
    print("姝ラ 4: 鍚姩Docker鏈嶅姟")
    print("=" * 50)

    # 妫€娴媎ocker compose鍛戒护鏍煎紡
    exit_code, _, _ = exec_remote(client, "docker compose version", check=False)
    compose_cmd = "docker compose" if exit_code == 0 else "docker-compose"

    # 鍚姩鏈嶅姟
    print("\n[鏈嶅姟] 鏋勫缓骞跺惎鍔ㄦ湇鍔?(杩欏彲鑳介渶瑕佸嚑鍒嗛挓)...")
    exec_remote(client, f"cd {REMOTE_BASE}/docker && {compose_cmd} up -d --build")

    # 绛夊緟鏈嶅姟鍚姩
    print("\n[鏈嶅姟] 绛夊緟鏈嶅姟鍚姩...")
    import time
    time.sleep(20)

    # 妫€鏌ユ湇鍔＄姸鎬?    print("\n[鏈嶅姟] 妫€鏌ユ湇鍔＄姸鎬?..")
    exec_remote(client, f"cd {REMOTE_BASE}/docker && {compose_cmd} ps")

    # 妫€鏌PI鍋ュ悍鐘舵€?    print("\n[鏈嶅姟] 妫€鏌PI鍋ュ悍鐘舵€?..")
    exec_remote(client, "curl -s http://localhost:8088/docs > /dev/null && echo 'API鏈嶅姟姝ｅ父' || echo 'API鏈嶅姟寮傚父'", check=False)


def main():
    """涓诲嚱鏁?""
    print("=" * 50)
    print("鏄撲箰鑸稩TS鏅烘収浣撴暀浜戝钩鍙?- Docker閮ㄧ讲")
    print("=" * 50)
    print(f"鐩爣鏈嶅姟鍣? {SERVER_USER}@{SERVER_HOST}")
    print(f"鏈嶅姟绔彛: 8088 (涓嶅奖鍝嶅叾浠栨湇鍔?")

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
        print("馃帀 閮ㄧ讲瀹屾垚!")
        print("=" * 50)
        print(f"璁块棶鍦板潃:")
        print(f"  - 瀹㈡埛绔? http://{SERVER_HOST}:8088/")
        print(f"  - 绠＄悊鍚庡彴: http://{SERVER_HOST}:8088/admin")
        print(f"  - API鏂囨。: http://{SERVER_HOST}:8088/docs")

    except Exception as e:
        print(f"\n[閿欒] 閮ㄧ讲澶辫触: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        if client:
            client.close()


if __name__ == "__main__":
    main()
