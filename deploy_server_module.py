#!/usr/bin/env python3
"""
部署 deploy/server/ 模块到远程服务器
使用 paramiko SSH 连接
"""
import paramiko
import os
import sys
from pathlib import Path

# 服务器配置
SERVER_HOST = os.getenv("SERVER_HOST", "8.134.33.19")
SERVER_USER = os.getenv("SERVER_USER", "root")
SERVER_PASSWORD = os.getenv("SERVER_PASSWORD")

if not SERVER_PASSWORD:
    print("错误: 必须设置 SERVER_PASSWORD 环境变量")
    sys.exit(1)
PROJECT_DIR = "/opt/yilehang-server"

def create_ssh_client():
    """创建 SSH 客户端"""
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(SERVER_HOST, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)
        print(f"[OK] 已连接到服务器 {SERVER_HOST}")
        return client
    except Exception as e:
        print(f"[ERROR] 连接失败: {e}")
        sys.exit(1)

def run_remote_command(client, command, show_output=True):
    """执行远程命令"""
    if show_output:
        print(f"\n→ {command}")
    stdin, stdout, stderr = client.exec_command(command)
    exit_status = stdout.channel.recv_exit_status()

    output = stdout.read().decode('utf-8')
    error = stderr.read().decode('utf-8')

    if show_output and output:
        print(output.strip())
    if error and exit_status != 0:
        print(f"[ERROR] {error.strip()}")

    return exit_status == 0, output, error

def upload_file(sftp, local_path, remote_path):
    """上传单个文件"""
    try:
        sftp.put(str(local_path), remote_path)
        return True
    except Exception as e:
        print(f"[ERROR] 上传失败 {local_path}: {e}")
        return False

def upload_directory(client, local_path, remote_path, exclude_patterns=None):
    """上传目录到远程服务器"""
    if exclude_patterns is None:
        exclude_patterns = ['node_modules', '.git', 'dist', '__pycache__', '*.pyc', '.env', '*.log']

    print(f"\n上传 {local_path} -> {remote_path}")

    sftp = client.open_sftp()
    run_remote_command(client, f"mkdir -p {remote_path}", show_output=False)

    local_path = Path(local_path)
    uploaded_count = 0

    for local_file in local_path.rglob('*'):
        if local_file.is_file():
            relative_path = local_file.relative_to(local_path)
            should_exclude = any(pattern in str(relative_path) for pattern in exclude_patterns)

            if should_exclude:
                continue

            remote_file = f"{remote_path}/{relative_path}".replace('\\', '/')
            remote_dir = os.path.dirname(remote_file)

            run_remote_command(client, f"mkdir -p {remote_dir}", show_output=False)

            if upload_file(sftp, local_file, remote_file):
                uploaded_count += 1
                if uploaded_count % 10 == 0:
                    print(f"  已上传 {uploaded_count} 个文件...")

    sftp.close()
    print(f"[OK] 上传完成，共 {uploaded_count} 个文件")

def main():
    print("=" * 60)
    print("易乐航服务端模块部署")
    print("=" * 60)
    print(f"目标服务器: {SERVER_HOST}")
    print(f"项目目录: {PROJECT_DIR}")

    client = create_ssh_client()

    try:
        # 1. 创建项目目录
        print("\n" + "=" * 60)
        print("步骤 1: 创建项目目录")
        print("=" * 60)
        run_remote_command(client, f"mkdir -p {PROJECT_DIR}")

        # 2. 上传项目文件
        print("\n" + "=" * 60)
        print("步骤 2: 上传项目文件")
        print("=" * 60)

        # 上传 apps/api
        upload_directory(client, "apps/api", f"{PROJECT_DIR}/apps/api")

        # 上传 deploy/server
        upload_directory(client, "deploy/server", f"{PROJECT_DIR}/deploy/server")

        # 3. 检查并安装 Docker
        print("\n" + "=" * 60)
        print("步骤 3: 检查 Docker")
        print("=" * 60)
        success, output, _ = run_remote_command(client, "docker --version")
        if not success:
            print("安装 Docker...")
            run_remote_command(client, "curl -fsSL https://get.docker.com | sh")

        success, output, _ = run_remote_command(client, "docker-compose --version")
        if not success:
            print("安装 Docker Compose...")
            run_remote_command(client, "curl -L https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m) -o /usr/local/bin/docker-compose && chmod +x /usr/local/bin/docker-compose")

        # 4. 创建 .env 文件
        print("\n" + "=" * 60)
        print("步骤 4: 创建环境变量文件")
        print("=" * 60)
        env_content = f"""POSTGRES_USER=postgres
POSTGRES_PASSWORD=yilehang2024secure
POSTGRES_DB=yilehang
SECRET_KEY=prod-secret-key-{os.urandom(16).hex()}
DEBUG=false
WECHAT_APPID=wxdbd150a0458a3c7c
WECHAT_SECRET=
ALLOW_WECHAT_LOGIN_WITHOUT_SECRET=true
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=
SMTP_PASSWORD=
SMTP_FROM=
SMTP_USE_SSL=false
DEV_PRINT_CODE_ON_SEND_FAIL=false
"""
        run_remote_command(client, f"cd {PROJECT_DIR}/deploy/server && cat > .env << 'EOF'\n{env_content}\nEOF")

        # 5. 停止旧容器
        print("\n" + "=" * 60)
        print("步骤 5: 停止旧容器")
        print("=" * 60)
        run_remote_command(client, f"cd {PROJECT_DIR}/deploy/server && docker-compose down")

        # 6. 启动新容器
        print("\n" + "=" * 60)
        print("步骤 6: 启动 Docker 容器")
        print("=" * 60)
        run_remote_command(client, f"cd {PROJECT_DIR}/deploy/server && docker-compose up -d --build")

        # 7. 等待服务启动
        print("\n等待服务启动...")
        import time
        time.sleep(15)

        # 8. 初始化数据库
        print("\n" + "=" * 60)
        print("步骤 7: 初始化数据库")
        print("=" * 60)
        run_remote_command(client, f"cd {PROJECT_DIR}/deploy/server && docker-compose exec -T api python -m scripts.init_db")
        run_remote_command(client, f"cd {PROJECT_DIR}/deploy/server && docker-compose exec -T api python -m scripts.seed_data")
        run_remote_command(client, f"cd {PROJECT_DIR}/deploy/server && docker-compose exec -T api python -m scripts.seed_role_permissions")

        # 9. 检查服务状态
        print("\n" + "=" * 60)
        print("步骤 8: 检查服务状态")
        print("=" * 60)
        run_remote_command(client, f"cd {PROJECT_DIR}/deploy/server && docker-compose ps")

        # 10. 测试 API
        print("\n" + "=" * 60)
        print("步骤 9: 测试 API")
        print("=" * 60)
        run_remote_command(client, f"curl -s http://localhost/health || echo '健康检查失败'")

        print("\n" + "=" * 60)
        print("部署完成!")
        print("=" * 60)
        print(f"\nAPI 地址: http://{SERVER_HOST}")
        print(f"API 文档: http://{SERVER_HOST}/docs")
        print(f"健康检查: http://{SERVER_HOST}/health")
        print("\n查看日志:")
        print(f"  ssh {SERVER_USER}@{SERVER_HOST}")
        print(f"  cd {PROJECT_DIR}/deploy/server")
        print(f"  docker-compose logs -f")

    except Exception as e:
        print(f"\n[ERROR] 部署失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        client.close()

if __name__ == "__main__":
    main()
