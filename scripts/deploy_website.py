#!/usr/bin/env python3
"""
全量部署脚本 - 部署官网及所有服务到 VPS
Usage: python scripts/deploy_website.py
"""

import os
import sys
from pathlib import Path

try:
    import paramiko
except ImportError:
    print("Installing paramiko...")
    os.system(f"{sys.executable} -m pip install paramiko -q")
    import paramiko

# Server configuration
SERVER_HOST = "8.134.33.19"
SERVER_USER = "root"
SERVER_PASSWORD = "Qq159741"
REMOTE_BASE = "/opt/yilehang"
LOCAL_BASE = Path(__file__).parent.parent


def get_ssh_client():
    """Create SSH client connection."""
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print(f"Connecting to {SERVER_HOST}...")
    client.connect(SERVER_HOST, username=SERVER_USER, password=SERVER_PASSWORD, timeout=30)
    return client


def run_command(client, command: str, description: str = "") -> tuple[bool, str]:
    """Run command on remote server."""
    if description:
        print(f"\n>>> {description}")

    stdin, stdout, stderr = client.exec_command(command, timeout=300)
    exit_code = stdout.channel.recv_exit_status()
    output = stdout.read().decode()
    error = stderr.read().decode()

    if output.strip():
        for line in output.strip().split('\n')[:20]:
            print(f"    {line}")
        if len(output.strip().split('\n')) > 20:
            print("    ... (truncated)")
    if error.strip() and exit_code != 0:
        print(f"    [ERROR] {error.strip()[:200]}")

    return exit_code == 0, output


def upload_file(sftp, local_path: Path, remote_path: str):
    """Upload a single file."""
    remote_dir = os.path.dirname(remote_path)
    try:
        sftp.stat(remote_dir)
    except FileNotFoundError:
        # Create parent directories
        parts = remote_dir.split('/')
        current = ''
        for part in parts:
            if part:
                current += f'/{part}'
                try:
                    sftp.stat(current)
                except FileNotFoundError:
                    sftp.mkdir(current)

    sftp.put(str(local_path), remote_path)


def upload_directory(sftp, local_path: Path, remote_path: str, exclude=None):
    """Recursively upload a directory."""
    exclude = exclude or []

    try:
        sftp.stat(remote_path)
    except FileNotFoundError:
        sftp.mkdir(remote_path)

    for item in local_path.iterdir():
        if item.name in exclude or item.name.startswith('.'):
            continue

        remote_item = f"{remote_path}/{item.name}"

        if item.is_dir():
            upload_directory(sftp, item, remote_item, exclude)
        else:
            sftp.put(str(item), remote_item)


def main():
    print("=" * 60)
    print("易乐航全量部署脚本")
    print("=" * 60)

    client = get_ssh_client()

    try:
        # Step 1: Stop and remove ALL old Docker containers
        print("\n" + "=" * 60)
        print("Step 1: 清理旧的 Docker 服务")
        print("=" * 60)

        run_command(client, "docker-compose -f /opt/yilehang/docker/docker-compose.prod.yml down 2>/dev/null || true", "停止旧的 docker-compose 服务")
        run_command(client, "docker stop $(docker ps -aq) 2>/dev/null || true", "停止所有容器")
        run_command(client, "docker rm $(docker ps -aq) 2>/dev/null || true", "删除所有容器")
        run_command(client, "docker system prune -f", "清理 Docker 缓存")

        # Step 2: Create directory structure
        print("\n" + "=" * 60)
        print("Step 2: 创建目录结构")
        print("=" * 60)

        run_command(client, f"rm -rf {REMOTE_BASE}", "删除旧目录")
        run_command(client, f"mkdir -p {REMOTE_BASE}/{{docker/nginx,website/assets,apps/api}}", "创建目录结构")

        # Step 3: Upload files
        print("\n" + "=" * 60)
        print("Step 3: 上传文件")
        print("=" * 60)

        sftp = client.open_sftp()

        # Upload website
        print("\n>>> 上传官网文件...")
        website_local = LOCAL_BASE / "website"
        upload_directory(sftp, website_local, f"{REMOTE_BASE}/website")
        print("    官网文件上传完成")

        # Upload docker configs
        print("\n>>> 上传 Docker 配置...")
        upload_file(sftp, LOCAL_BASE / "docker" / "docker-compose.prod.yml", f"{REMOTE_BASE}/docker/docker-compose.prod.yml")
        upload_file(sftp, LOCAL_BASE / "docker" / "nginx" / "nginx.conf", f"{REMOTE_BASE}/docker/nginx/nginx.conf")
        print("    Docker 配置上传完成")

        # Upload API Dockerfile
        print("\n>>> 上传 API Dockerfile...")
        dockerfile_path = LOCAL_BASE / "docker" / "Dockerfile.api"
        if dockerfile_path.exists():
            upload_file(sftp, dockerfile_path, f"{REMOTE_BASE}/docker/Dockerfile.api")

        # Upload API source
        print("\n>>> 上传 API 源码...")
        api_local = LOCAL_BASE / "apps" / "api"
        if api_local.exists():
            upload_directory(sftp, api_local, f"{REMOTE_BASE}/apps/api", exclude=['__pycache__', '.pytest_cache', 'venv', '.venv'])
        print("    API 源码上传完成")

        sftp.close()

        # Step 4: Create simplified docker-compose for website only
        print("\n" + "=" * 60)
        print("Step 4: 创建官网 Docker 配置")
        print("=" * 60)

        website_compose = '''version: '3.8'

services:
  nginx:
    image: nginx:alpine
    container_name: yilehang-website
    ports:
      - "80:80"
    volumes:
      - /opt/yilehang/website:/usr/share/nginx/html:ro
      - /opt/yilehang/nginx.conf:/etc/nginx/conf.d/default.conf:ro
    restart: unless-stopped
'''

        nginx_conf = '''server {
    listen 80;
    server_name _;

    root /usr/share/nginx/html;
    index index.html;

    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location ~* \\.(jpg|jpeg|png|gif|ico|css|js|svg|woff|woff2)$ {
        expires 7d;
        add_header Cache-Control "public, immutable";
    }
}
'''

        run_command(client, f"cat > {REMOTE_BASE}/docker-compose.yml << 'EOF'\n{website_compose}EOF", "创建 docker-compose.yml")
        run_command(client, f"cat > {REMOTE_BASE}/nginx.conf << 'EOF'\n{nginx_conf}EOF", "创建 nginx.conf")

        # Step 5: Start Docker services
        print("\n" + "=" * 60)
        print("Step 5: 启动 Docker 服务")
        print("=" * 60)

        run_command(client, f"cd {REMOTE_BASE} && docker-compose up -d", "启动官网服务")

        # Step 6: Verify deployment
        print("\n" + "=" * 60)
        print("Step 6: 验证部署")
        print("=" * 60)

        run_command(client, "docker ps", "查看运行中的容器")
        run_command(client, f"ls -la {REMOTE_BASE}/website/", "查看官网文件")

        # Test website
        success, output = run_command(client, "curl -s -o /dev/null -w '%{http_code}' http://localhost", "测试官网访问")

        print("\n" + "=" * 60)
        print("部署完成!")
        print("=" * 60)
        print(f"官网地址: http://{SERVER_HOST}")
        print("=" * 60)

    except Exception as e:
        print(f"\n[ERROR] 部署失败: {e}")
        raise
    finally:
        client.close()


if __name__ == "__main__":
    main()
