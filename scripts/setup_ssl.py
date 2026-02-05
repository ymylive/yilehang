"""配置域名和SSL证书 - 修复版"""
import paramiko
import time

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect("8.134.33.19", username="root", password="Qq159741", timeout=30)

def run(cmd, check=True):
    print(f">>> {cmd[:100]}...")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=300)
    exit_code = stdout.channel.recv_exit_status()
    out = stdout.read().decode('utf-8', errors='ignore')
    err = stderr.read().decode('utf-8', errors='ignore')
    if out:
        print(out[:2000])
    if err:
        print(f"STDERR: {err[:500]}")
    if check and exit_code != 0:
        raise Exception(f"Command failed: {cmd[:50]}")
    return exit_code, out

DOMAIN = "yilehang.cornna.xyz"

print("=== 1. 停止所有占用80端口的进程 ===")
run("docker stop yilehang-nginx 2>/dev/null; echo done", check=False)
run("systemctl stop nginx 2>/dev/null; echo done", check=False)
run("pkill -f 'nginx' 2>/dev/null; echo done", check=False)
time.sleep(2)

print("\n=== 2. 检查80端口是否释放 ===")
run("netstat -tlnp | grep ':80' || echo 'Port 80 is free'", check=False)

print("\n=== 3. 申请SSL证书 ===")
exit_code, out = run(f"~/.acme.sh/acme.sh --issue -d {DOMAIN} --standalone --httpport 80 --force", check=False)

if exit_code != 0 and "already" not in out.lower():
    print("尝试使用webroot模式...")
    run("mkdir -p /var/www/acme", check=False)
    run(f"~/.acme.sh/acme.sh --issue -d {DOMAIN} --webroot /var/www/acme --force", check=False)

print("\n=== 4. 检查证书是否存在 ===")
run(f"ls -la ~/.acme.sh/{DOMAIN}_ecc/ 2>/dev/null || ls -la ~/.acme.sh/{DOMAIN}/ 2>/dev/null || echo 'No cert found'", check=False)

print("\n=== 5. 安装证书 ===")
run("mkdir -p /opt/yilehang/ssl")
# 尝试ECC证书
exit_code, _ = run(f"~/.acme.sh/acme.sh --install-cert -d {DOMAIN} --ecc --key-file /opt/yilehang/ssl/key.pem --fullchain-file /opt/yilehang/ssl/cert.pem", check=False)
if exit_code != 0:
    # 尝试RSA证书
    run(f"~/.acme.sh/acme.sh --install-cert -d {DOMAIN} --key-file /opt/yilehang/ssl/key.pem --fullchain-file /opt/yilehang/ssl/cert.pem", check=False)

print("\n=== 6. 检查证书文件 ===")
run("ls -la /opt/yilehang/ssl/", check=False)

print("\n=== 7. 更新nginx配置 ===")
nginx_conf = f'''events {{ worker_connections 1024; }}
http {{
    include /etc/nginx/mime.types;
    default_type application/octet-stream;
    upstream api {{ server api:8000; }}

    server {{
        listen 80;
        server_name {DOMAIN};
        return 301 https://$host$request_uri;
    }}

    server {{
        listen 443 ssl;
        server_name {DOMAIN};

        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers HIGH:!aNULL:!MD5;

        location /api {{
            proxy_pass http://api;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }}
        location /docs {{ proxy_pass http://api/docs; proxy_set_header Host $host; }}
        location /redoc {{ proxy_pass http://api/redoc; proxy_set_header Host $host; }}
        location /openapi.json {{ proxy_pass http://api/openapi.json; proxy_set_header Host $host; }}
        location /admin {{ alias /usr/share/nginx/html/admin; try_files $uri $uri/ /admin/index.html; }}
        location / {{ root /usr/share/nginx/html/client; try_files $uri $uri/ /index.html; }}
    }}
}}'''

run(f"cat > /opt/yilehang/docker/nginx/nginx.conf << 'EOFNGINX'\n{nginx_conf}\nEOFNGINX")

print("\n=== 8. 更新docker-compose.yml ===")
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
      - "80:80"
      - "443:443"
    volumes:
      - /opt/yilehang/docker/nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - /opt/yilehang/apps/client/dist:/usr/share/nginx/html/client:ro
      - /opt/yilehang/apps/admin/dist:/usr/share/nginx/html/admin:ro
      - /opt/yilehang/ssl:/etc/nginx/ssl:ro
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

run(f"cat > /opt/yilehang/docker/docker-compose.yml << 'EOFCOMPOSE'\n{compose}\nEOFCOMPOSE")

print("\n=== 9. 启动Docker服务 ===")
run("cd /opt/yilehang/docker && docker-compose up -d", check=False)

print("\n=== 10. 等待服务启动 ===")
time.sleep(10)

print("\n=== 11. 检查服务状态 ===")
run("docker ps", check=False)
run("docker logs yilehang-nginx --tail 15 2>&1", check=False)

client.close()

print("\n" + "=" * 50)
print("SSL配置完成!")
print("=" * 50)
print(f"访问地址:")
print(f"  - HTTPS: https://{DOMAIN}/")
print(f"  - 管理后台: https://{DOMAIN}/admin")
print(f"  - API文档: https://{DOMAIN}/docs")
print("\n注意事项:")
print(f"1. 确保域名 {DOMAIN} 已解析到 8.134.33.19")
print("2. 确保阿里云安全组已开放 80 和 443 端口")
