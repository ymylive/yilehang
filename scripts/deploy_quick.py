"""
绠€鍖朌ocker閮ㄧ讲鑴氭湰
"""
import sys
import subprocess

try:
    import paramiko
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "paramiko"])
    import paramiko

# 服务器配置
SERVER = "82.158.88.34"
USER = "root"
PASSWORD = os.getenv("SERVER_PASSWORD")

if not PASSWORD:
    print("错误: 必须设置 SERVER_PASSWORD 环境变量")
    sys.exit(1)

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
    print(f"杩炴帴鍒?{USER}@{SERVER}...")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(SERVER, username=USER, password=PASSWORD, timeout=30)
    print("杩炴帴鎴愬姛!")

    # 1. 娓呯悊鏃ч儴缃?    print("\n=== 娓呯悊鏃ч儴缃?===")
    run(client, "docker stop renling-nginx renling-api renling-postgres 2>/dev/null; docker rm renling-nginx renling-api renling-postgres 2>/dev/null; rm -rf /opt/renling; echo 'cleaned'")

    # 2. 妫€鏌ocker
    print("\n=== 妫€鏌ocker ===")
    run(client, "docker --version")
    run(client, "docker-compose --version || echo 'docker-compose not found'")

    # 3. 鍒涘缓鐩綍
    print("\n=== 鍒涘缓鐩綍 ===")
    run(client, "mkdir -p /opt/renling/{apps/{api,client/dist,admin/dist},docker/nginx}")

    # 4. 鍒涘缓docker-compose.yml
    print("\n=== 鍒涘缓Docker閰嶇疆 ===")
    compose = '''version: "3.8"
services:
  postgres:
    image: postgres:15-alpine
    container_name: renling-postgres
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres123
      POSTGRES_DB: renling
    volumes:
      - renling_pg:/var/lib/postgresql/data
    networks:
      - renling
    restart: unless-stopped

  api:
    image: python:3.11-slim
    container_name: renling-api
    working_dir: /app
    command: sh -c "pip install fastapi uvicorn sqlalchemy asyncpg pydantic pydantic-settings python-jose passlib httpx -q && uvicorn app.main:app --host 0.0.0.0 --port 8000"
    volumes:
      - /opt/renling/apps/api:/app
    environment:
      DATABASE_URL: postgresql+asyncpg://postgres:${POSTGRES_PASSWORD:-change-me-in-production}@postgres:5432/renling
      SECRET_KEY: ${SECRET_KEY:?set-in-env}
    networks:
      - renling
    depends_on:
      - postgres
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    container_name: renling-nginx
    ports:
      - "8088:80"
    volumes:
      - /opt/renling/docker/nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - /opt/renling/apps/client/dist:/usr/share/nginx/html/client:ro
      - /opt/renling/apps/admin/dist:/usr/share/nginx/html/admin:ro
    networks:
      - renling
    depends_on:
      - api
    restart: unless-stopped

networks:
  renling:
    name: renling

volumes:
  renling_pg:
'''
    run(client, f"cat > /opt/renling/docker/docker-compose.yml << 'EOFCOMPOSE'\n{compose}\nEOFCOMPOSE")

    # 5. 鍒涘缓nginx閰嶇疆
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
    run(client, f"cat > /opt/renling/docker/nginx/nginx.conf << 'EOFNGINX'\n{nginx}\nEOFNGINX")

    # 6. 鍒涘缓鍗犱綅椤甸潰
    client_html = '<!DOCTYPE html><html><head><meta charset="UTF-8"><title>鏄撲箰鑸?/title></head><body style="display:flex;justify-content:center;align-items:center;height:100vh;background:linear-gradient(135deg,#667eea,#764ba2);"><div style="text-align:center;color:white;"><h1>鏄撲箰鑸蜂箰鑸垚闀?/h1><p>鍚庣鏈嶅姟宸查儴缃?/p></div></body></html>'
    admin_html = '<!DOCTYPE html><html><head><meta charset="UTF-8"><title>绠＄悊鍚庡彴</title></head><body style="display:flex;justify-content:center;align-items:center;height:100vh;background:linear-gradient(135deg,#1a1a2e,#16213e);"><div style="text-align:center;color:white;"><h1>鏄撲箰鑸风鐞嗗悗鍙?/h1><p>鍚庣鏈嶅姟宸查儴缃?/p></div></body></html>'
    run(client, f"echo '{client_html}' > /opt/renling/apps/client/dist/index.html")
    run(client, f"echo '{admin_html}' > /opt/renling/apps/admin/dist/index.html")

    print("\n閰嶇疆鏂囦欢鍒涘缓瀹屾垚锛岀幇鍦ㄩ渶瑕佷笂浼燗PI浠ｇ爜...")
    client.close()
    print("\n璇锋墜鍔ㄦ墽琛屼互涓嬫楠ゅ畬鎴愰儴缃?")
    print("1. 涓婁紶API浠ｇ爜鍒版湇鍔″櫒")
    print("2. 鍦ㄦ湇鍔″櫒涓婃墽琛? cd /opt/renling/docker && docker-compose up -d")
    print(f"\n璁块棶鍦板潃: http://{SERVER}:8088/")

if __name__ == "__main__":
    main()
