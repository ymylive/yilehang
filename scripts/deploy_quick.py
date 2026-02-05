"""
简化Docker部署脚本
"""
import sys
import subprocess

try:
    import paramiko
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "paramiko"])
    import paramiko

# 服务器配置
SERVER = "8.134.33.19"
USER = "root"
PASSWORD = "Qq159741"

def run(client, cmd):
    print(f">>> {cmd}")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=300)
    exit_code = stdout.channel.recv_exit_status()
    out = stdout.read().decode('utf-8', errors='ignore')
    err = stderr.read().decode('utf-8', errors='ignore')
    if out:
        print(out[:2000])
    if err and exit_code != 0:
        print(f"ERROR: {err[:500]}")
    return exit_code

def main():
    print(f"连接到 {USER}@{SERVER}...")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(SERVER, username=USER, password=PASSWORD, timeout=30)
    print("连接成功!")

    # 1. 清理旧部署
    print("\n=== 清理旧部署 ===")
    run(client, "docker stop yilehang-nginx yilehang-api yilehang-postgres yilehang-redis 2>/dev/null; docker rm yilehang-nginx yilehang-api yilehang-postgres yilehang-redis 2>/dev/null; rm -rf /opt/yilehang; echo 'cleaned'")

    # 2. 检查Docker
    print("\n=== 检查Docker ===")
    run(client, "docker --version")
    run(client, "docker-compose --version || echo 'docker-compose not found'")

    # 3. 创建目录
    print("\n=== 创建目录 ===")
    run(client, "mkdir -p /opt/yilehang/{apps/{api,client/dist,admin/dist},docker/nginx}")

    # 4. 创建docker-compose.yml
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
    command: sh -c "pip install fastapi uvicorn sqlalchemy asyncpg pydantic pydantic-settings python-jose passlib python-multipart redis httpx -q && uvicorn app.main:app --host 0.0.0.0 --port 8000"
    volumes:
      - /opt/yilehang/apps/api:/app
    environment:
      DATABASE_URL: postgresql+asyncpg://postgres:postgres123@postgres:5432/yilehang
      REDIS_URL: redis://redis:6379/0
      SECRET_KEY: yilehang-secret-2024
    networks:
      - yilehang
    depends_on:
      - postgres
      - redis
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

    # 5. 创建nginx配置
    nginx = '''events { worker_connections 1024; }
http {
    include /etc/nginx/mime.types;
    upstream api { server api:8000; }
    server {
        listen 80;
        location /api { proxy_pass http://api; proxy_set_header Host $host; }
        location /docs { proxy_pass http://api/docs; }
        location /openapi.json { proxy_pass http://api/openapi.json; }
        location /admin { alias /usr/share/nginx/html/admin; try_files $uri /admin/index.html; }
        location / { root /usr/share/nginx/html/client; try_files $uri /index.html; }
    }
}'''
    run(client, f"cat > /opt/yilehang/docker/nginx/nginx.conf << 'EOFNGINX'\n{nginx}\nEOFNGINX")

    # 6. 创建占位页面
    client_html = '<!DOCTYPE html><html><head><meta charset="UTF-8"><title>易乐航</title></head><body style="display:flex;justify-content:center;align-items:center;height:100vh;background:linear-gradient(135deg,#667eea,#764ba2);"><div style="text-align:center;color:white;"><h1>易乐航·乐航成长</h1><p>后端服务已部署</p></div></body></html>'
    admin_html = '<!DOCTYPE html><html><head><meta charset="UTF-8"><title>管理后台</title></head><body style="display:flex;justify-content:center;align-items:center;height:100vh;background:linear-gradient(135deg,#1a1a2e,#16213e);"><div style="text-align:center;color:white;"><h1>易乐航·管理后台</h1><p>后端服务已部署</p></div></body></html>'
    run(client, f"echo '{client_html}' > /opt/yilehang/apps/client/dist/index.html")
    run(client, f"echo '{admin_html}' > /opt/yilehang/apps/admin/dist/index.html")

    print("\n配置文件创建完成，现在需要上传API代码...")
    client.close()
    print("\n请手动执行以下步骤完成部署:")
    print("1. 上传API代码到服务器")
    print("2. 在服务器上执行: cd /opt/yilehang/docker && docker-compose up -d")
    print(f"\n访问地址: http://{SERVER}:8088/")

if __name__ == "__main__":
    main()
