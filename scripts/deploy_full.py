"""
完整Docker部署脚本 - 包含swap配置和僵尸进程清理
"""
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

# 服务器配置
SERVER = "8.134.33.19"
USER = "root"
PASSWORD = "Qq159741"
PROJECT_ROOT = Path(__file__).parent.parent

def run(client, cmd, check=True):
    print(f">>> {cmd[:100]}...")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=600)
    exit_code = stdout.channel.recv_exit_status()
    out = stdout.read().decode('utf-8', errors='ignore')
    err = stderr.read().decode('utf-8', errors='ignore')
    if out:
        print(out[:1500])
    if err and exit_code != 0:
        print(f"ERROR: {err[:300]}")
    if check and exit_code != 0:
        raise Exception(f"Command failed: {cmd[:50]}")
    return exit_code, out

def upload_api(client):
    """上传API代码"""
    print("\n=== 上传API代码 ===")
    api_dir = PROJECT_ROOT / "apps" / "api"

    with tempfile.NamedTemporaryFile(suffix='.tar.gz', delete=False) as tmp:
        tar_path = tmp.name

    try:
        print("打包API代码...")
        with tarfile.open(tar_path, 'w:gz') as tar:
            tar.add(api_dir, arcname='api')

        print("上传到服务器...")
        sftp = client.open_sftp()
        sftp.put(tar_path, '/tmp/api.tar.gz')
        sftp.close()

        print("解压...")
        run(client, "tar -xzf /tmp/api.tar.gz -C /opt/yilehang/apps/api --strip-components=1")
        run(client, "rm -f /tmp/api.tar.gz")
        print("API代码上传完成")
    finally:
        if os.path.exists(tar_path):
            os.remove(tar_path)

def main():
    print(f"连接到 {USER}@{SERVER}...")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(SERVER, username=USER, password=PASSWORD, timeout=30)
    print("连接成功!")

    # 0. 配置Swap到8GB
    print("\n=== 配置Swap内存到8GB ===")
    run(client, "free -h", check=False)

    # 检查现有swap
    exit_code, out = run(client, "swapon --show", check=False)
    if "swapfile" in out or "/swap" in out:
        print("已有swap，先关闭...")
        run(client, "swapoff -a", check=False)
        run(client, "rm -f /swapfile", check=False)

    # 创建8GB swap
    print("创建8GB swap文件...")
    run(client, "fallocate -l 8G /swapfile || dd if=/dev/zero of=/swapfile bs=1M count=8192")
    run(client, "chmod 600 /swapfile")
    run(client, "mkswap /swapfile")
    run(client, "swapon /swapfile")

    # 添加到fstab
    run(client, "grep -q '/swapfile' /etc/fstab || echo '/swapfile none swap sw 0 0' >> /etc/fstab", check=False)

    print("Swap配置完成，当前内存状态:")
    run(client, "free -h", check=False)

    # 1. 清理僵尸进程
    print("\n=== 清理僵尸进程 ===")
    run(client, "ps aux | grep -w Z | grep -v grep || echo '无僵尸进程'", check=False)
    # 尝试杀死僵尸进程的父进程
    run(client, "for pid in $(ps -eo pid,stat | awk '$2 ~ /Z/ {print $1}'); do ppid=$(ps -o ppid= -p $pid 2>/dev/null); [ -n \"$ppid\" ] && kill -9 $ppid 2>/dev/null; done; echo 'done'", check=False)

    # 2. 清理旧部署
    print("\n=== 清理旧部署 ===")
    run(client, "cd /opt/yilehang/docker && docker-compose down 2>/dev/null; echo 'done'", check=False)
    run(client, "docker stop yilehang-nginx yilehang-api yilehang-postgres yilehang-redis 2>/dev/null; docker rm yilehang-nginx yilehang-api yilehang-postgres yilehang-redis 2>/dev/null; echo 'cleaned'", check=False)

    # 3. 创建目录
    print("\n=== 创建目录 ===")
    run(client, "mkdir -p /opt/yilehang/{apps/{api,client/dist,admin/dist},docker/nginx}")

    # 4. 上传API代码
    upload_api(client)

    # 5. 创建docker-compose.yml
    print("\n=== 创建Docker配置 ===")
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

  redis:
    image: redis:7-alpine
    container_name: yilehang-redis
    networks:
      - yilehang
    restart: unless-stopped

  api:
    image: python:3.11-slim
    container_name: yilehang-api
    working_dir: /app
    command: sh -c "pip install -i https://pypi.tuna.tsinghua.edu.cn/simple fastapi uvicorn sqlalchemy asyncpg pydantic pydantic-settings python-jose passlib python-multipart redis httpx aiofiles bcrypt -q && uvicorn app.main:app --host 0.0.0.0 --port 8000"
    volumes:
      - /opt/yilehang/apps/api:/app
    environment:
      DATABASE_URL: postgresql+asyncpg://postgres:postgres123@postgres:5432/yilehang
      REDIS_URL: redis://redis:6379/0
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
      - "8088:80"
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

    # 6. 创建nginx配置
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

    # 7. 创建占位页面
    print("\n=== 创建占位页面 ===")
    client_html = '''<!DOCTYPE html>
<html lang="zh-CN">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>易乐航</title>
<style>*{margin:0;padding:0}body{min-height:100vh;display:flex;align-items:center;justify-content:center;background:linear-gradient(135deg,#667eea,#764ba2);font-family:system-ui}
.c{text-align:center;color:#fff;padding:40px}.logo{font-size:80px;margin-bottom:20px}h1{font-size:36px;margin-bottom:10px}.sub{opacity:.9;margin-bottom:30px}
.status{background:rgba(255,255,255,.2);padding:15px 30px;border-radius:30px;display:inline-block}</style></head>
<body><div class="c"><div class="logo">🏃</div><h1>易乐航·乐航成长</h1><p class="sub">ITS智慧体教云平台</p><div class="status">✅ 服务已部署</div></div></body></html>'''

    admin_html = '''<!DOCTYPE html>
<html lang="zh-CN">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>管理后台</title>
<style>*{margin:0;padding:0}body{min-height:100vh;display:flex;align-items:center;justify-content:center;background:linear-gradient(135deg,#1a1a2e,#16213e);font-family:system-ui}
.c{text-align:center;color:#fff;padding:40px}.logo{font-size:80px;margin-bottom:20px}h1{font-size:36px;margin-bottom:10px}.sub{opacity:.9;margin-bottom:30px}
.status{background:rgba(102,126,234,.3);padding:15px 30px;border-radius:30px;border:1px solid rgba(102,126,234,.5)}</style></head>
<body><div class="c"><div class="logo">⚙️</div><h1>易乐航·管理后台</h1><p class="sub">运营管理系统</p><div class="status">✅ 服务已部署</div></div></body></html>'''

    run(client, f"cat > /opt/yilehang/apps/client/dist/index.html << 'EOFHTML'\n{client_html}\nEOFHTML")
    run(client, f"cat > /opt/yilehang/apps/admin/dist/index.html << 'EOFHTML'\n{admin_html}\nEOFHTML")

    # 8. 启动服务
    print("\n=== 启动Docker服务 ===")
    run(client, "cd /opt/yilehang/docker && docker-compose pull")
    run(client, "cd /opt/yilehang/docker && docker-compose up -d")

    # 等待服务启动
    print("\n等待服务启动...")
    import time
    time.sleep(30)

    # 检查状态
    print("\n=== 服务状态 ===")
    run(client, "cd /opt/yilehang/docker && docker-compose ps", check=False)
    run(client, "docker logs yilehang-api --tail 20 2>&1 || echo 'no logs'", check=False)

    client.close()

    print("\n" + "=" * 50)
    print("🎉 部署完成!")
    print("=" * 50)
    print(f"访问地址:")
    print(f"  - 客户端: http://{SERVER}:8088/")
    print(f"  - 管理后台: http://{SERVER}:8088/admin")
    print(f"  - API文档: http://{SERVER}:8088/docs")

if __name__ == "__main__":
    main()
