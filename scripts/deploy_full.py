"""Full Docker deployment script (swap + cleanup + upload + compose)."""
import sys
import subprocess
import tarfile
import tempfile
import os
from pathlib import Path

try:
    import paramiko
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "paramiko"])
    import paramiko

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

# Server config
SERVER = "82.158.88.34"
USER = "root"
PASSWORD = "Qq159741"
PROJECT_ROOT = Path(__file__).parent.parent


def run(client, cmd, check=True, timeout=600):
    print(f">>> {cmd[:120]}...")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)
    exit_code = stdout.channel.recv_exit_status()
    out = stdout.read().decode('utf-8', errors='ignore')
    err = stderr.read().decode('utf-8', errors='ignore')
    if out:
        print(out[:1500])
    if err and exit_code != 0:
        print(f"ERROR: {err[:300]}")
    if check and exit_code != 0:
        raise Exception(f"Command failed: {cmd[:60]}")
    return exit_code, out


def ensure_docker(client):
    run(client, "command -v curl >/dev/null 2>&1 || (apt-get update -y && apt-get install -y curl)", check=False)
    code, _ = run(client, "command -v docker", check=False)
    if code != 0:
        run(client, "curl -fsSL https://get.docker.com | sh")
    run(client, "systemctl enable --now docker", check=False)
    run(client, "docker --version", check=False)


def install_compose(client):
    # ensure curl
    run(client, "command -v curl >/dev/null 2>&1 || (apt-get update -y && apt-get install -y curl)", check=False)

    # try package manager
    if run(client, "command -v apt-get", check=False)[0] == 0:
        run(client, "apt-get update -y && apt-get install -y docker-compose-plugin", check=False)
    elif run(client, "command -v yum", check=False)[0] == 0:
        run(client, "yum install -y docker-compose-plugin", check=False)
    elif run(client, "command -v dnf", check=False)[0] == 0:
        run(client, "dnf install -y docker-compose-plugin", check=False)
    elif run(client, "command -v apk", check=False)[0] == 0:
        run(client, "apk add --no-cache docker-cli-compose", check=False)

    # fallback to standalone binary
    run(
        client,
        "curl -L https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m) "
        "-o /usr/local/bin/docker-compose",
        check=False,
    )
    run(client, "chmod +x /usr/local/bin/docker-compose", check=False)


def get_compose_cmd(client) -> str:
    if run(client, "docker compose version", check=False)[0] == 0:
        return "docker compose"
    if run(client, "docker-compose --version", check=False)[0] == 0:
        return "docker-compose"

    install_compose(client)

    if run(client, "docker compose version", check=False)[0] == 0:
        return "docker compose"
    if run(client, "docker-compose --version", check=False)[0] == 0:
        return "docker-compose"

    raise Exception("Docker Compose not available")


def upload_api(client):
    """Upload API code."""
    print("\n=== Upload API code ===")
    api_dir = PROJECT_ROOT / "apps" / "api"

    with tempfile.NamedTemporaryFile(suffix='.tar.gz', delete=False) as tmp:
        tar_path = tmp.name

    try:
        print("Packing API code...")
        with tarfile.open(tar_path, 'w:gz') as tar:
            tar.add(api_dir, arcname='api')

        print("Uploading to server...")
        sftp = client.open_sftp()
        sftp.put(tar_path, '/tmp/api.tar.gz')
        sftp.close()

        print("Extracting...")
        run(client, "mkdir -p /opt/yilehang/apps/api")
        run(client, "tar -xzf /tmp/api.tar.gz -C /opt/yilehang/apps/api --strip-components=1")
        run(client, "rm -f /tmp/api.tar.gz")
        print("API upload done")
    finally:
        if os.path.exists(tar_path):
            os.remove(tar_path)


def main():
    print(f"Connecting to {USER}@{SERVER}...")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(SERVER, username=USER, password=PASSWORD, timeout=30)
    print("Connected")

    ensure_docker(client)
    compose_cmd = get_compose_cmd(client)

    # 0. Configure swap
    print("\n=== Configure swap (8GB) ===")
    run(client, "free -h", check=False)

    exit_code, out = run(client, "swapon --show", check=False)
    if "swapfile" in out or "/swap" in out:
        print("Swap exists, disabling...")
        run(client, "swapoff -a", check=False)
        run(client, "rm -f /swapfile", check=False)

    print("Creating swapfile...")
    run(client, "fallocate -l 8G /swapfile || dd if=/dev/zero of=/swapfile bs=1M count=8192")
    run(client, "chmod 600 /swapfile")
    run(client, "mkswap /swapfile")
    run(client, "swapon /swapfile")
    run(client, "grep -q '/swapfile' /etc/fstab || echo '/swapfile none swap sw 0 0' >> /etc/fstab", check=False)
    run(client, "free -h", check=False)

    # 1. Clean zombie processes
    print("\n=== Clean zombie processes ===")
    run(client, "ps aux | grep -w Z | grep -v grep || echo 'No zombie process'", check=False)
    run(
        client,
        "for pid in $(ps -eo pid,stat | awk '$2 ~ /Z/ {print $1}'); do "
        "ppid=$(ps -o ppid= -p $pid 2>/dev/null); "
        "[ -n \"$ppid\" ] && kill -9 $ppid 2>/dev/null; "
        "done; echo 'done'",
        check=False,
    )

    # 2. Clean old deployment
    print("\n=== Clean old deployment ===")
    run(client, f"cd /opt/yilehang/docker && {compose_cmd} down 2>/dev/null; echo 'done'", check=False)
    run(client, "docker stop yilehang-nginx yilehang-api yilehang-postgres yilehang-redis 2>/dev/null; "
                "docker rm yilehang-nginx yilehang-api yilehang-postgres yilehang-redis 2>/dev/null; echo 'cleaned'", check=False)

    # 3. Create directories
    print("\n=== Create directories ===")
    run(client, "mkdir -p /opt/yilehang/{apps/{api,client/dist,admin/dist},docker/nginx}")

    # 4. Upload API
    upload_api(client)

    # 5. Create docker-compose.yml
    print("\n=== Create docker-compose.yml ===")
    compose = '''version: "3.8"
services:
  postgres:
    image: postgres:15-alpine
    container_name: yilehang-postgres
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres123
      POSTGRES_DB: yilehang
    volumes:
      - yilehang_pg:/var/lib/postgresql/data
    networks:
      - yilehang
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5

  api:
    image: python:3.11-slim
    container_name: yilehang-api
    working_dir: /app
    command: sh -c "pip install -i https://pypi.tuna.tsinghua.edu.cn/simple fastapi uvicorn sqlalchemy asyncpg pydantic pydantic-settings python-jose passlib httpx bcrypt -q && uvicorn app.main:app --host 0.0.0.0 --port 8000"
    volumes:
      - /opt/yilehang/apps/api:/app
    environment:
      DATABASE_URL: postgresql+asyncpg://postgres:postgres123@postgres:5432/yilehang
      SECRET_KEY: yilehang-secret-2024
    networks:
      - yilehang
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
      - /opt/yilehang/docker/nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - /opt/yilehang/apps/client/dist:/usr/share/nginx/html/client:ro
      - /opt/yilehang/apps/admin/dist:/usr/share/nginx/html/admin:ro
    networks:
      - yilehang
    depends_on:
      - api
    restart: unless-stopped

networks:
  yilehang:
    name: yilehang

volumes:
  yilehang_pg:
'''
    run(client, f"cat > /opt/yilehang/docker/docker-compose.yml << 'EOFCOMPOSE'\n{compose}\nEOFCOMPOSE")

    # 6. Create nginx config
    nginx = '''events { worker_connections 1024; }
http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;
    upstream api { server api:8000; }
    server {
        listen 80;
        location /api { proxy_pass http://api; proxy_set_header Host $host; proxy_set_header X-Real-IP $remote_addr; }
        location /docs { proxy_pass http://api/docs; proxy_set_header Host $host; }
        location /redoc { proxy_pass http://api/redoc; proxy_set_header Host $host; }
        location /openapi.json { proxy_pass http://api/openapi.json; proxy_set_header Host $host; }
        location /admin { alias /usr/share/nginx/html/admin; try_files $uri $uri/ /admin/index.html; }
        location / { root /usr/share/nginx/html/client; try_files $uri $uri/ /index.html; }
    }
}'''
    run(client, f"cat > /opt/yilehang/docker/nginx/nginx.conf << 'EOFNGINX'\n{nginx}\nEOFNGINX")

    # 7. Placeholder pages
    print("\n=== Create placeholder pages ===")
    client_html = '''<!DOCTYPE html>
<html lang="zh-CN">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Yilehang</title>
<style>*{margin:0;padding:0}body{min-height:100vh;display:flex;align-items:center;justify-content:center;background:linear-gradient(135deg,#FFB347,#FF8800);font-family:system-ui}
.c{text-align:center;color:#fff;padding:40px}.logo{font-size:80px;margin-bottom:20px}h1{font-size:36px;margin-bottom:10px}.sub{opacity:.9;margin-bottom:30px}
.status{background:rgba(255,255,255,.2);padding:15px 30px;border-radius:30px;display:inline-block}</style></head>
<body><div class="c"><div class="logo">??</div><h1>Yilehang · Sports Growth</h1><p class="sub">ITS Intelligent Sports Platform</p><div class="status">? Service ready</div></div></body></html>'''

    admin_html = '''<!DOCTYPE html>
<html lang="zh-CN">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Admin</title>
<style>*{margin:0;padding:0}body{min-height:100vh;display:flex;align-items:center;justify-content:center;background:linear-gradient(135deg,#2a2a2a,#1a1a1a);font-family:system-ui}
.c{text-align:center;color:#fff;padding:40px}.logo{font-size:80px;margin-bottom:20px}h1{font-size:36px;margin-bottom:10px}.sub{opacity:.9;margin-bottom:30px}
.status{background:rgba(255,255,255,.2);padding:15px 30px;border-radius:30px;display:inline-block}</style></head>
<body><div class="c"><div class="logo">???</div><h1>Yilehang Admin</h1><p class="sub">Operations Console</p><div class="status">? Service ready</div></div></body></html>'''

    run(client, f"cat > /opt/yilehang/apps/client/dist/index.html << 'EOFHTML'\n{client_html}\nEOFHTML")
    run(client, f"cat > /opt/yilehang/apps/admin/dist/index.html << 'EOFHTML'\n{admin_html}\nEOFHTML")

    # 8. Start services
    print("\n=== Start Docker services ===")
    run(client, f"cd /opt/yilehang/docker && {compose_cmd} pull", check=False)
    run(client, f"cd /opt/yilehang/docker && {compose_cmd} up -d")

    # Wait
    print("\nWaiting for services...")
    import time
    time.sleep(30)

    # Check status
    print("\n=== Service status ===")
    run(client, f"cd /opt/yilehang/docker && {compose_cmd} ps", check=False)
    run(client, "docker logs yilehang-api --tail 20 2>&1 || echo 'no logs'", check=False)

    client.close()

    print("\n" + "=" * 50)
    print("Deployment done")
    print("=" * 50)
    print("Access:")
    print(f"  - Client: http://{SERVER}/")
    print(f"  - Admin: http://{SERVER}/admin")
    print(f"  - API docs: http://{SERVER}/docs")


if __name__ == "__main__":
    main()
