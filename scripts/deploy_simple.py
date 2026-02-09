"""
绠€鍖栫増鍓嶇閮ㄧ讲鑴氭湰 - 灏嗛」鐩儴缃插埌VPS鏈嶅姟鍣?鍏堥儴缃插悗绔疉PI鍜孨ginx锛屽墠绔娇鐢ㄥ崰浣嶉〉闈?"""
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

if not SERVER_PASSWORD:
    print("错误: 必须设置 SERVER_PASSWORD 环境变量")
    sys.exit(1)
SERVER_PORT = 22

# 椤圭洰璺緞
PROJECT_ROOT = Path(__file__).parent.parent
APPS_DIR = PROJECT_ROOT / "apps"
DOCKER_DIR = PROJECT_ROOT / "docker"

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
    print(f"[杩滅▼] {cmd[:80]}..." if len(cmd) > 80 else f"[杩滅▼] {cmd}")
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


def setup_server(client: paramiko.SSHClient):
    """閰嶇疆鏈嶅姟鍣ㄧ幆澧?""
    print("\n" + "=" * 50)
    print("姝ラ 1: 閰嶇疆鏈嶅姟鍣ㄧ幆澧?)
    print("=" * 50)

    # 妫€鏌ュ苟瀹夎 Docker
    print("\n[鏈嶅姟鍣╙ 妫€鏌?Docker 瀹夎...")
    exit_code, _, _ = exec_remote(client, "docker --version", check=False)
    if exit_code != 0:
        print("[鏈嶅姟鍣╙ Docker 鏈畨瑁咃紝姝ｅ湪瀹夎...")
        # 瀹夎 Docker
        exec_remote(client, "apt-get update -y")
        exec_remote(client, "apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release")
        exec_remote(client, "curl -fsSL https://get.docker.com | sh", check=False)
        exec_remote(client, "systemctl start docker")
        exec_remote(client, "systemctl enable docker")
        print("[鏈嶅姟鍣╙ Docker 瀹夎瀹屾垚")

    # 妫€鏌ュ苟瀹夎 Docker Compose
    print("\n[鏈嶅姟鍣╙ 妫€鏌?Docker Compose...")
    exit_code, _, _ = exec_remote(client, "docker compose version", check=False)
    if exit_code != 0:
        exit_code, _, _ = exec_remote(client, "docker-compose --version", check=False)
        if exit_code != 0:
            print("[鏈嶅姟鍣╙ 瀹夎 Docker Compose 鎻掍欢...")
            exec_remote(client, "apt-get install -y docker-compose-plugin", check=False)

    # 鍒涘缓椤圭洰鐩綍
    print("\n[鏈嶅姟鍣╙ 鍒涘缓椤圭洰鐩綍...")
    exec_remote(client, f"mkdir -p {REMOTE_BASE}/apps/admin/dist")
    exec_remote(client, f"mkdir -p {REMOTE_BASE}/apps/client/dist")
    exec_remote(client, f"mkdir -p {REMOTE_BASE}/apps/api")
    exec_remote(client, f"mkdir -p {REMOTE_BASE}/docker/nginx")
    exec_remote(client, f"mkdir -p {REMOTE_BASE}/database")


def deploy_files(client: paramiko.SSHClient):
    """閮ㄧ讲鏂囦欢鍒版湇鍔″櫒"""
    print("\n" + "=" * 50)
    print("姝ラ 2: 閮ㄧ讲鏂囦欢鍒版湇鍔″櫒")
    print("=" * 50)

    sftp = client.open_sftp()

    # 涓婁紶 API 浠ｇ爜
    api_dir = APPS_DIR / "api"
    if api_dir.exists():
        print("\n[閮ㄧ讲] 涓婁紶 API 鍚庣...")
        upload_with_tar(client, api_dir, f"{REMOTE_BASE}/apps/api", "api")

    # 涓婁紶 Docker 閰嶇疆
    print("\n[閮ㄧ讲] 涓婁紶 Docker 閰嶇疆...")

    nginx_conf = DOCKER_DIR / "nginx" / "nginx.conf"
    if nginx_conf.exists():
        sftp.put(str(nginx_conf), f"{REMOTE_BASE}/docker/nginx/nginx.conf")

    dockerfile = DOCKER_DIR / "Dockerfile.api"
    if dockerfile.exists():
        sftp.put(str(dockerfile), f"{REMOTE_BASE}/docker/Dockerfile.api")

    compose_file = DOCKER_DIR / "docker-compose.prod.yml"
    if compose_file.exists():
        sftp.put(str(compose_file), f"{REMOTE_BASE}/docker/docker-compose.prod.yml")

    # 涓婁紶鏁版嵁搴撹縼绉绘枃浠?    print("\n[閮ㄧ讲] 涓婁紶鏁版嵁搴撴枃浠?..")
    db_dir = PROJECT_ROOT / "database"
    if db_dir.exists():
        upload_with_tar(client, db_dir, f"{REMOTE_BASE}/database", "database")

    sftp.close()


def create_placeholder_pages(client: paramiko.SSHClient):
    """鍒涘缓鍗犱綅椤甸潰"""
    print("\n[閰嶇疆] 鍒涘缓鍓嶇鍗犱綅椤甸潰...")

    # Client 鍗犱綅椤甸潰
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
        <div class="logo">馃弮</div>
        <h1>鏄撲箰鑸蜂箰鑸垚闀?/h1>
        <p class="subtitle">ITS鏅烘収浣撴暀浜戝钩鍙?- 瀛﹀憳/瀹堕暱绔?/p>
        <div class="status">馃殌 绯荤粺閮ㄧ讲涓?..</div>
        <div class="features">
            <div class="feature">
                <div class="feature-icon">馃搳</div>
                <div>鎴愰暱妗ｆ</div>
            </div>
            <div class="feature">
                <div class="feature-icon">馃</div>
                <div>AI闄粌</div>
            </div>
            <div class="feature">
                <div class="feature-icon">馃搮</div>
                <div>璇剧▼棰勭害</div>
            </div>
            <div class="feature">
                <div class="feature-icon">馃摑</div>
                <div>浣滀笟鎵撳崱</div>
            </div>
        </div>
    </div>
</body>
</html>'''

    # Admin 鍗犱綅椤甸潰
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
        <div class="logo">鈿欙笍</div>
        <h1>鏄撲箰鑸风鐞嗗悗鍙?/h1>
        <p class="subtitle">ITS鏅烘収浣撴暀浜戝钩鍙?- 杩愯惀绠＄悊绯荤粺</p>
        <div class="status">馃敡 绯荤粺閮ㄧ讲涓?..</div>
        <div class="modules">
            <div class="module">
                <div class="module-icon">馃懃</div>
                <div class="module-name">鐢ㄦ埛绠＄悊</div>
            </div>
            <div class="module">
                <div class="module-icon">馃摎</div>
                <div class="module-name">璇剧▼绠＄悊</div>
            </div>
            <div class="module">
                <div class="module-icon">馃搮</div>
                <div class="module-name">鎺掕绯荤粺</div>
            </div>
            <div class="module">
                <div class="module-icon">馃挵</div>
                <div class="module-name">璐㈠姟涓績</div>
            </div>
            <div class="module">
                <div class="module-icon">馃搳</div>
                <div class="module-name">鏁版嵁鍒嗘瀽</div>
            </div>
            <div class="module">
                <div class="module-icon">馃敂</div>
                <div class="module-name">娑堟伅閫氱煡</div>
            </div>
        </div>
    </div>
</body>
</html>'''

    exec_remote(client, f"cat > {REMOTE_BASE}/apps/client/dist/index.html << 'HTML_EOF'\n{client_html}\nHTML_EOF")
    exec_remote(client, f"cat > {REMOTE_BASE}/apps/admin/dist/index.html << 'HTML_EOF'\n{admin_html}\nHTML_EOF")


def create_configs(client: paramiko.SSHClient):
    """鍒涘缓閰嶇疆鏂囦欢"""
    print("\n[閰嶇疆] 鍒涘缓 Nginx 閰嶇疆...")

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

    print("\n[閰嶇疆] 鍒涘缓 Docker Compose 閰嶇疆...")

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

  api:
    build:
      context: ../apps/api
      dockerfile: /opt/yilehang/docker/Dockerfile.api
    container_name: yilehang-api
    environment:
      DATABASE_URL: postgresql+asyncpg://postgres:postgres123@postgres:5432/yilehang
      DEBUG: "false"
      SECRET_KEY: yilehang-secret-key-2024
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
    depends_on:
      - api
    restart: unless-stopped

volumes:
  postgres_data:
'''

    exec_remote(client, f"cat > {REMOTE_BASE}/docker/docker-compose.prod.yml << 'COMPOSE_EOF'\n{compose_config}\nCOMPOSE_EOF")


def start_services(client: paramiko.SSHClient):
    """鍚姩鏈嶅姟"""
    print("\n" + "=" * 50)
    print("姝ラ 3: 鍚姩鏈嶅姟")
    print("=" * 50)

    # 妫€娴?docker compose 鍛戒护鏍煎紡
    exit_code, _, _ = exec_remote(client, "docker compose version", check=False)
    compose_cmd = "docker compose" if exit_code == 0 else "docker-compose"

    # 鍋滄鏃ф湇鍔?    print("\n[鏈嶅姟] 鍋滄鏃ф湇鍔?..")
    exec_remote(client, f"cd {REMOTE_BASE}/docker && {compose_cmd} -f docker-compose.prod.yml down 2>/dev/null || true", check=False)

    # 鍚姩鏂版湇鍔?    print("\n[鏈嶅姟] 鍚姩鏈嶅姟 (杩欏彲鑳介渶瑕佸嚑鍒嗛挓)...")
    exec_remote(client, f"cd {REMOTE_BASE}/docker && {compose_cmd} -f docker-compose.prod.yml up -d --build")

    # 绛夊緟鏈嶅姟鍚姩
    print("\n[鏈嶅姟] 绛夊緟鏈嶅姟鍚姩...")
    import time
    time.sleep(15)

    # 妫€鏌ユ湇鍔＄姸鎬?    print("\n[鏈嶅姟] 妫€鏌ユ湇鍔＄姸鎬?..")
    exec_remote(client, f"cd {REMOTE_BASE}/docker && {compose_cmd} -f docker-compose.prod.yml ps")


def main():
    """涓诲嚱鏁?""
    print("=" * 50)
    print("鏄撲箰鑸稩TS鏅烘収浣撴暀浜戝钩鍙?- 閮ㄧ讲鑴氭湰")
    print("=" * 50)
    print(f"鐩爣鏈嶅姟鍣? {SERVER_USER}@{SERVER_HOST}")

    client = None
    try:
        client = create_ssh_client()

        setup_server(client)
        deploy_files(client)
        create_placeholder_pages(client)
        create_configs(client)
        start_services(client)

        print("\n" + "=" * 50)
        print("閮ㄧ讲瀹屾垚!")
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
