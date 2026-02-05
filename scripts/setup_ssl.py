"""Configure domain and SSL via acme.sh, update nginx + compose."""
import paramiko
import time
import sys

SERVER = "82.158.88.34"
USER = "root"
PASSWORD = "Qq159741"
DOMAIN = "yilehang.cornna.xyz"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(SERVER, username=USER, password=PASSWORD, timeout=30)


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


def ensure_docker():
    run("command -v curl >/dev/null 2>&1 || (apt-get update -y && apt-get install -y curl)", check=False)
    code, _ = run("command -v docker", check=False)
    if code != 0:
        run("curl -fsSL https://get.docker.com | sh")
    run("systemctl enable --now docker", check=False)


def install_compose():
    run("command -v curl >/dev/null 2>&1 || (apt-get update -y && apt-get install -y curl)", check=False)
    if run("command -v apt-get", check=False)[0] == 0:
        run("apt-get update -y && apt-get install -y docker-compose-plugin", check=False)
    elif run("command -v yum", check=False)[0] == 0:
        run("yum install -y docker-compose-plugin", check=False)
    elif run("command -v dnf", check=False)[0] == 0:
        run("dnf install -y docker-compose-plugin", check=False)
    elif run("command -v apk", check=False)[0] == 0:
        run("apk add --no-cache docker-cli-compose", check=False)

    run(
        "curl -L https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m) "
        "-o /usr/local/bin/docker-compose",
        check=False,
    )
    run("chmod +x /usr/local/bin/docker-compose", check=False)


def get_compose_cmd() -> str:
    if run("docker compose version", check=False)[0] == 0:
        return "docker compose"
    if run("docker-compose --version", check=False)[0] == 0:
        return "docker-compose"
    install_compose()
    if run("docker compose version", check=False)[0] == 0:
        return "docker compose"
    if run("docker-compose --version", check=False)[0] == 0:
        return "docker-compose"
    raise Exception("Docker Compose not available")


ensure_docker()
compose_cmd = get_compose_cmd()

print("=== 0. DNS check ===")
_, dns_ip = run(f"getent hosts {DOMAIN} | awk '{{print $1}}' | head -n 1", check=False)
if SERVER not in dns_ip:
    print(f"[WARN] DNS for {DOMAIN} -> {dns_ip.strip()} (expected {SERVER}).")
    print("Update DNS first, then re-run this script.")
    client.close()
    sys.exit(1)

print("=== 1. Install acme.sh (if missing) ===")
exit_code, _ = run("~/.acme.sh/acme.sh --version", check=False)
if exit_code != 0:
    run("apt-get update -y", check=False)
    run("apt-get install -y curl socat", check=False)
    run("curl https://get.acme.sh | sh", check=False)

print("=== 2. Stop services on port 80 ===")
run("docker stop yilehang-nginx 2>/dev/null; echo done", check=False)
run("systemctl stop nginx 2>/dev/null; echo done", check=False)
run("pkill -f 'nginx' 2>/dev/null; echo done", check=False)
time.sleep(2)

print("\n=== 3. Check port 80 ===")
run("netstat -tlnp | grep ':80' || echo 'Port 80 is free'", check=False)

print("\n=== 4. Issue SSL certificate ===")
exit_code, out = run(f"~/.acme.sh/acme.sh --issue -d {DOMAIN} --standalone --httpport 80 --force", check=False)

if exit_code != 0 and "already" not in out.lower():
    print("Try webroot mode...")
    run("mkdir -p /var/www/acme", check=False)
    run(f"~/.acme.sh/acme.sh --issue -d {DOMAIN} --webroot /var/www/acme --force", check=False)

print("\n=== 5. Verify cert files ===")
run(f"ls -la ~/.acme.sh/{DOMAIN}_ecc/ 2>/dev/null || ls -la ~/.acme.sh/{DOMAIN}/ 2>/dev/null || echo 'No cert found'", check=False)

print("\n=== 6. Install cert ===")
run("mkdir -p /opt/yilehang/ssl")
exit_code, _ = run(f"~/.acme.sh/acme.sh --install-cert -d {DOMAIN} --ecc --key-file /opt/yilehang/ssl/key.pem --fullchain-file /opt/yilehang/ssl/cert.pem", check=False)
if exit_code != 0:
    run(f"~/.acme.sh/acme.sh --install-cert -d {DOMAIN} --key-file /opt/yilehang/ssl/key.pem --fullchain-file /opt/yilehang/ssl/cert.pem", check=False)

print("\n=== 7. Check cert files ===")
run("ls -la /opt/yilehang/ssl/", check=False)

print("\n=== 8. Update nginx config ===")
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

print("\n=== 9. Update docker-compose.yml ===")
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

print("\n=== 10. Start Docker services ===")
run(f"cd /opt/yilehang/docker && {compose_cmd} up -d", check=False)

print("\n=== 11. Wait for services ===")
time.sleep(10)

print("\n=== 12. Check status ===")
run("docker ps", check=False)
run("docker logs yilehang-nginx --tail 15 2>&1", check=False)

client.close()

print("\n" + "=" * 50)
print("SSL setup done")
print("=" * 50)
print("Access:")
print(f"  - HTTPS: https://{DOMAIN}/")
print(f"  - Admin: https://{DOMAIN}/admin")
print(f"  - API docs: https://{DOMAIN}/docs")
print("\nNotes:")
print(f"1. Ensure domain {DOMAIN} resolves to {SERVER}")
print("2. Ensure firewall allows 80/443")
