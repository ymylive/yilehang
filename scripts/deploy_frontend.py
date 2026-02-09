"""
鍓嶇閮ㄧ讲鑴氭湰 - 灏嗗墠绔簲鐢ㄩ儴缃插埌VPS鏈嶅姟鍣?鏀寔 Windows 鐜锛屼娇鐢?paramiko 杩涜 SSH/SFTP 鎿嶄綔
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


def run_local_command(cmd: str, cwd: Path = None) -> bool:
    """鎵ц鏈湴鍛戒护"""
    print(f"[鏈湴] 鎵ц: {cmd}")
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            cwd=cwd or PROJECT_ROOT,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore'
        )
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0:
            print(f"[璀﹀憡] 鍛戒护杩斿洖闈為浂鐘舵€? {result.returncode}")
            if result.stderr:
                print(result.stderr)
            return False
        return True
    except Exception as e:
        print(f"[閿欒] 鎵ц鍛戒护澶辫触: {e}")
        return False


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
    print(f"[杩滅▼] 鎵ц: {cmd}")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=300)
    exit_code = stdout.channel.recv_exit_status()
    out = stdout.read().decode('utf-8', errors='ignore')
    err = stderr.read().decode('utf-8', errors='ignore')

    if out:
        print(out)
    if err and exit_code != 0:
        print(f"[閿欒] {err}")

    if check and exit_code != 0:
        raise Exception(f"鍛戒护鎵ц澶辫触: {cmd}")

    return exit_code, out, err


def upload_directory(sftp: paramiko.SFTPClient, local_path: Path, remote_path: str):
    """涓婁紶鐩綍鍒拌繙绋嬫湇鍔″櫒"""
    print(f"[涓婁紶] {local_path} -> {remote_path}")

    # 鍒涘缓杩滅▼鐩綍
    try:
        sftp.mkdir(remote_path)
    except IOError:
        pass  # 鐩綍宸插瓨鍦?
    for item in local_path.iterdir():
        local_item = local_path / item.name
        remote_item = f"{remote_path}/{item.name}"

        if item.is_dir():
            # 璺宠繃涓嶉渶瑕佺殑鐩綍
            if item.name in ['node_modules', '__pycache__', '.git', '.venv']:
                continue
            upload_directory(sftp, local_item, remote_item)
        else:
            print(f"  涓婁紶鏂囦欢: {item.name}")
            sftp.put(str(local_item), remote_item)


def upload_with_tar(client: paramiko.SSHClient, local_path: Path, remote_path: str, name: str):
    """浣跨敤tar鍘嬬缉涓婁紶锛堟洿蹇級"""
    print(f"[鎵撳寘涓婁紶] {local_path} -> {remote_path}")

    # 鍒涘缓涓存椂tar鏂囦欢
    with tempfile.NamedTemporaryFile(suffix='.tar.gz', delete=False) as tmp:
        tar_path = tmp.name

    try:
        # 鍒涘缓tar鍖?        print(f"  鍒涘缓鍘嬬缉鍖? {tar_path}")
        with tarfile.open(tar_path, 'w:gz') as tar:
            tar.add(local_path, arcname=name)

        # 涓婁紶tar鍖?        sftp = client.open_sftp()
        remote_tar = f"/tmp/{name}.tar.gz"
        print(f"  涓婁紶鍘嬬缉鍖?..")
        sftp.put(tar_path, remote_tar)
        sftp.close()

        # 瑙ｅ帇鍒扮洰鏍囩洰褰?        exec_remote(client, f"mkdir -p {remote_path}")
        exec_remote(client, f"tar -xzf {remote_tar} -C {remote_path} --strip-components=1")
        exec_remote(client, f"rm -f {remote_tar}")

    finally:
        # 娓呯悊涓存椂鏂囦欢
        if os.path.exists(tar_path):
            os.remove(tar_path)


def build_frontend():
    """鏋勫缓鍓嶇搴旂敤"""
    print("\n" + "=" * 50)
    print("姝ラ 1: 鏋勫缓鍓嶇搴旂敤")
    print("=" * 50)

    # 妫€鏌ユ槸鍚﹀畨瑁呬簡pnpm
    if not run_local_command("pnpm --version"):
        print("[閿欒] 璇峰厛瀹夎 pnpm: npm install -g pnpm")
        return False

    # 瀹夎渚濊禆
    print("\n[鏋勫缓] 瀹夎渚濊禆...")
    run_local_command("pnpm install")

    # 鏋勫缓 admin
    print("\n[鏋勫缓] 鏋勫缓绠＄悊鍚庡彴 (admin)...")
    admin_success = run_local_command("pnpm build:admin")

    # 鏋勫缓 client
    print("\n[鏋勫缓] 鏋勫缓瀹㈡埛绔?(client)...")
    client_success = run_local_command("pnpm build:client")

    # 妫€鏌ユ瀯寤虹粨鏋?    admin_dist = APPS_DIR / "admin" / "dist"
    client_dist = APPS_DIR / "client" / "dist" / "build" / "h5"

    if not admin_dist.exists():
        print(f"[璀﹀憡] Admin 鏋勫缓鐩綍涓嶅瓨鍦? {admin_dist}")
    else:
        print(f"[鎴愬姛] Admin 鏋勫缓瀹屾垚: {admin_dist}")

    if not client_dist.exists():
        # 灏濊瘯鍏朵粬鍙兘鐨勮矾寰?        client_dist = APPS_DIR / "client" / "dist" / "h5"
        if not client_dist.exists():
            print(f"[璀﹀憡] Client 鏋勫缓鐩綍涓嶅瓨鍦?)
        else:
            print(f"[鎴愬姛] Client 鏋勫缓瀹屾垚: {client_dist}")
    else:
        print(f"[鎴愬姛] Client 鏋勫缓瀹屾垚: {client_dist}")

    return True


def setup_server(client: paramiko.SSHClient):
    """閰嶇疆鏈嶅姟鍣ㄧ幆澧?""
    print("\n" + "=" * 50)
    print("姝ラ 2: 閰嶇疆鏈嶅姟鍣ㄧ幆澧?)
    print("=" * 50)

    # 妫€鏌ュ苟瀹夎 Docker
    print("\n[鏈嶅姟鍣╙ 妫€鏌?Docker...")
    exit_code, _, _ = exec_remote(client, "docker --version", check=False)
    if exit_code != 0:
        print("[鏈嶅姟鍣╙ 瀹夎 Docker...")
        exec_remote(client, "curl -fsSL https://get.docker.com | sh", check=False)
        exec_remote(client, "systemctl start docker && systemctl enable docker")

    # 妫€鏌ュ苟瀹夎 Docker Compose
    print("\n[鏈嶅姟鍣╙ 妫€鏌?Docker Compose...")
    exit_code, _, _ = exec_remote(client, "docker-compose --version", check=False)
    if exit_code != 0:
        print("[鏈嶅姟鍣╙ 瀹夎 Docker Compose...")
        exec_remote(client,
            "curl -L 'https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)' -o /usr/local/bin/docker-compose && chmod +x /usr/local/bin/docker-compose",
            check=False
        )

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
    print("姝ラ 3: 閮ㄧ讲鏂囦欢鍒版湇鍔″櫒")
    print("=" * 50)

    sftp = client.open_sftp()

    # 涓婁紶 admin dist
    admin_dist = APPS_DIR / "admin" / "dist"
    if admin_dist.exists():
        print("\n[閮ㄧ讲] 涓婁紶 Admin 鍓嶇...")
        upload_with_tar(client, admin_dist, f"{REMOTE_BASE}/apps/admin/dist", "admin-dist")

    # 涓婁紶 client dist
    client_dist = APPS_DIR / "client" / "dist" / "build" / "h5"
    if not client_dist.exists():
        client_dist = APPS_DIR / "client" / "dist" / "h5"
    if client_dist.exists():
        print("\n[閮ㄧ讲] 涓婁紶 Client 鍓嶇...")
        upload_with_tar(client, client_dist, f"{REMOTE_BASE}/apps/client/dist", "client-dist")

    # 涓婁紶 API 浠ｇ爜
    api_dir = APPS_DIR / "api"
    if api_dir.exists():
        print("\n[閮ㄧ讲] 涓婁紶 API 鍚庣...")
        upload_with_tar(client, api_dir, f"{REMOTE_BASE}/apps/api", "api")

    # 涓婁紶 Docker 閰嶇疆
    print("\n[閮ㄧ讲] 涓婁紶 Docker 閰嶇疆...")

    # nginx.conf
    nginx_conf = DOCKER_DIR / "nginx" / "nginx.conf"
    if nginx_conf.exists():
        sftp.put(str(nginx_conf), f"{REMOTE_BASE}/docker/nginx/nginx.conf")

    # Dockerfile.api
    dockerfile = DOCKER_DIR / "Dockerfile.api"
    if dockerfile.exists():
        sftp.put(str(dockerfile), f"{REMOTE_BASE}/docker/Dockerfile.api")

    # docker-compose.prod.yml
    compose_file = DOCKER_DIR / "docker-compose.prod.yml"
    if compose_file.exists():
        sftp.put(str(compose_file), f"{REMOTE_BASE}/docker/docker-compose.prod.yml")

    # 涓婁紶鏁版嵁搴撹縼绉绘枃浠?    print("\n[閮ㄧ讲] 涓婁紶鏁版嵁搴撴枃浠?..")
    db_dir = PROJECT_ROOT / "database"
    if db_dir.exists():
        upload_with_tar(client, db_dir, f"{REMOTE_BASE}/database", "database")

    sftp.close()


def fix_nginx_config(client: paramiko.SSHClient):
    """淇 nginx 閰嶇疆涓殑璺緞"""
    print("\n[閰嶇疆] 淇 Nginx 閰嶇疆...")

    nginx_config = f"""events {{
    worker_connections 1024;
}}

http {{
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;

    sendfile        on;
    keepalive_timeout  65;

    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml;

    upstream api {{
        server api:8000;
    }}

    server {{
        listen 80;
        server_name _;

        # API浠ｇ悊
        location /api {{
            proxy_pass http://api;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }}

        # API鏂囨。
        location /docs {{
            proxy_pass http://api/docs;
            proxy_set_header Host $host;
        }}

        location /redoc {{
            proxy_pass http://api/redoc;
            proxy_set_header Host $host;
        }}

        location /openapi.json {{
            proxy_pass http://api/api/v1/openapi.json;
            proxy_set_header Host $host;
        }}

        # 绠＄悊鍚庡彴
        location /admin {{
            alias /usr/share/nginx/html/admin;
            try_files $uri $uri/ /admin/index.html;
        }}

        # C绔疕5
        location / {{
            root /usr/share/nginx/html/client;
            try_files $uri $uri/ /index.html;
        }}
    }}
}}
"""

    # 鍐欏叆閰嶇疆鏂囦欢
    exec_remote(client, f"cat > {REMOTE_BASE}/docker/nginx/nginx.conf << 'NGINX_EOF'\n{nginx_config}\nNGINX_EOF")


def fix_docker_compose(client: paramiko.SSHClient):
    """淇 docker-compose 閰嶇疆"""
    print("\n[閰嶇疆] 淇 Docker Compose 閰嶇疆...")

    compose_config = """version: '3.8'

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
      SECRET_KEY: yilehang-secret-key-change-in-production
    depends_on:
      postgres:
        condition: service_healthy
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    container_name: yilehang-nginx
    ports:
      - "80:80"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ../apps/client/dist:/usr/share/nginx/html/client:ro
      - ../apps/admin/dist:/usr/share/nginx/html/admin:ro
    depends_on:
      - api
    restart: unless-stopped

volumes:
  postgres_data:
"""

    exec_remote(client, f"cat > {REMOTE_BASE}/docker/docker-compose.prod.yml << 'COMPOSE_EOF'\n{compose_config}\nCOMPOSE_EOF")


def start_services(client: paramiko.SSHClient):
    """鍚姩鏈嶅姟"""
    print("\n" + "=" * 50)
    print("姝ラ 4: 鍚姩鏈嶅姟")
    print("=" * 50)

    # 淇閰嶇疆
    fix_nginx_config(client)
    fix_docker_compose(client)

    # 妫€娴?docker compose 鍛戒护鏍煎紡
    exit_code, _, _ = exec_remote(client, "docker compose version", check=False)
    if exit_code == 0:
        compose_cmd = "docker compose"
    else:
        compose_cmd = "docker-compose"

    # 鍋滄鏃ф湇鍔?    print("\n[鏈嶅姟] 鍋滄鏃ф湇鍔?..")
    exec_remote(client, f"cd {REMOTE_BASE}/docker && {compose_cmd} -f docker-compose.prod.yml down", check=False)

    # 鍚姩鏂版湇鍔?    print("\n[鏈嶅姟] 鍚姩鏈嶅姟...")
    exec_remote(client, f"cd {REMOTE_BASE}/docker && {compose_cmd} -f docker-compose.prod.yml up -d --build")

    # 绛夊緟鏈嶅姟鍚姩
    print("\n[鏈嶅姟] 绛夊緟鏈嶅姟鍚姩...")
    import time
    time.sleep(10)

    # 妫€鏌ユ湇鍔＄姸鎬?    print("\n[鏈嶅姟] 妫€鏌ユ湇鍔＄姸鎬?..")
    exec_remote(client, f"cd {REMOTE_BASE}/docker && docker-compose -f docker-compose.prod.yml ps")


def main():
    """涓诲嚱鏁?""
    print("=" * 50)
    print("鏄撲箰鑸稩TS鏅烘収浣撴暀浜戝钩鍙?- 鍓嶇閮ㄧ讲鑴氭湰")
    print("=" * 50)
    print(f"鐩爣鏈嶅姟鍣? {SERVER_USER}@{SERVER_HOST}")
    print(f"椤圭洰鐩綍: {PROJECT_ROOT}")

    # 姝ラ1: 鏋勫缓鍓嶇
    build_frontend()

    # 杩炴帴鏈嶅姟鍣?    client = None
    try:
        client = create_ssh_client()

        # 姝ラ2: 閰嶇疆鏈嶅姟鍣?        setup_server(client)

        # 姝ラ3: 閮ㄧ讲鏂囦欢
        deploy_files(client)

        # 姝ラ4: 鍚姩鏈嶅姟
        start_services(client)

        print("\n" + "=" * 50)
        print("閮ㄧ讲瀹屾垚!")
        print("=" * 50)
        print(f"璁块棶鍦板潃:")
        print(f"  - 瀹㈡埛绔? http://{SERVER_HOST}/")
        print(f"  - 绠＄悊鍚庡彴: http://{SERVER_HOST}/admin")
        print(f"  - API鏂囨。: http://{SERVER_HOST}/docs")

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
