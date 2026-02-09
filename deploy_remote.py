#!/usr/bin/env python3
"""
易乐航远程部署脚本 - 使用 paramiko SSH 连接
运行前安装: pip install paramiko
"""
import paramiko
import os
import sys
from pathlib import Path

# 服务器配置
SERVER_HOST = "8.134.33.19"
SERVER_USER = "root"
SERVER_PASSWORD = "Qq159741"
DOMAIN = "yilehang.cornna.xyz"
PROJECT_DIR = "/opt/yilehang"

def create_ssh_client():
    """创建 SSH 客户端"""
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(SERVER_HOST, username=SERVER_USER, password=SERVER_PASSWORD)
        print(f"[OK] 已连接到服务器 {SERVER_HOST}")
        return client
    except Exception as e:
        print(f"[ERROR] 连接失败: {e}")
        sys.exit(1)

def run_remote_command(client, command, show_output=True):
    """执行远程命令"""
    if show_output:
        print(f"\n执行: {command}")
    stdin, stdout, stderr = client.exec_command(command)
    exit_status = stdout.channel.recv_exit_status()

    output = stdout.read().decode('utf-8')
    error = stderr.read().decode('utf-8')

    if show_output and output:
        print(output)
    if error and exit_status != 0:
        print(f"错误: {error}")

    return exit_status == 0, output, error

def upload_directory(client, local_path, remote_path, exclude_patterns=None):
    """上传目录到远程服务器"""
    if exclude_patterns is None:
        exclude_patterns = ['node_modules', '.git', 'dist', '__pycache__', '*.pyc', '.env']

    print(f"\n上传 {local_path} -> {remote_path}")

    sftp = client.open_sftp()

    # 确保远程目录存在
    try:
        sftp.stat(remote_path)
    except FileNotFoundError:
        run_remote_command(client, f"mkdir -p {remote_path}", show_output=False)

    local_path = Path(local_path)
    uploaded_count = 0

    for local_file in local_path.rglob('*'):
        if local_file.is_file():
            # 检查是否应该排除
            relative_path = local_file.relative_to(local_path)
            should_exclude = False
            for pattern in exclude_patterns:
                if pattern in str(relative_path):
                    should_exclude = True
                    break

            if should_exclude:
                continue

            remote_file = f"{remote_path}/{relative_path}".replace('\\', '/')
            remote_dir = os.path.dirname(remote_file)

            # 确保远程目录存在
            try:
                sftp.stat(remote_dir)
            except FileNotFoundError:
                run_remote_command(client, f"mkdir -p {remote_dir}", show_output=False)

            # 上传文件
            try:
                sftp.put(str(local_file), remote_file)
                uploaded_count += 1
                if uploaded_count % 10 == 0:
                    print(f"  已上传 {uploaded_count} 个文件...")
            except Exception as e:
                print(f"  上传失败 {local_file}: {e}")

    sftp.close()
    print(f"[OK] 上传完成，共 {uploaded_count} 个文件")

def main():
    print("=" * 60)
    print("易乐航远程部署脚本")
    print("=" * 60)
    print(f"目标服务器: {SERVER_HOST}")
    print(f"域名: {DOMAIN}")
    print(f"项目目录: {PROJECT_DIR}")

    # 检查 paramiko
    try:
        import paramiko
    except ImportError:
        print("\n错误: 需要安装 paramiko")
        print("运行: pip install paramiko")
        sys.exit(1)

    # 连接服务器
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

        # 上传核心目录
        upload_directory(client, "apps/api", f"{PROJECT_DIR}/apps/api")
        upload_directory(client, "apps/unified-miniapp", f"{PROJECT_DIR}/apps/unified-miniapp")
        upload_directory(client, "docker", f"{PROJECT_DIR}/docker")

        # 上传根目录文件
        sftp = client.open_sftp()
        for file in ['package.json', 'pnpm-workspace.yaml']:
            if os.path.exists(file):
                sftp.put(file, f"{PROJECT_DIR}/{file}")
        sftp.close()

        # 3. 安装 Docker
        print("\n" + "=" * 60)
        print("步骤 3: 检查并安装 Docker")
        print("=" * 60)
        success, output, _ = run_remote_command(client, "docker --version")
        if not success:
            print("安装 Docker...")
            run_remote_command(client, "curl -fsSL https://get.docker.com | sh")

        success, output, _ = run_remote_command(client, "docker-compose --version")
        if not success:
            print("安装 Docker Compose...")
            run_remote_command(client,
                "curl -L https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m) -o /usr/local/bin/docker-compose && chmod +x /usr/local/bin/docker-compose")

        # 4. 创建环境变量文件
        print("\n" + "=" * 60)
        print("步骤 4: 创建环境变量文件")
        print("=" * 60)
        env_content = f"""POSTGRES_PASSWORD=yilehang2024
SECRET_KEY=your-secret-key-change-in-production-{os.urandom(16).hex()}
WECHAT_APPID=wxdbd150a0458a3c7c
WECHAT_SECRET=
DOMAIN={DOMAIN}
ALLOW_WECHAT_LOGIN_WITHOUT_SECRET=true
DEV_PRINT_CODE_ON_SEND_FAIL=true
"""
        run_remote_command(client, f"cd {PROJECT_DIR}/docker && cat > .env << 'EOF'\n{env_content}\nEOF")

        # 5. 启动 Docker 容器
        print("\n" + "=" * 60)
        print("步骤 5: 启动 Docker 容器")
        print("=" * 60)
        run_remote_command(client, f"cd {PROJECT_DIR}/docker && docker-compose -f docker-compose.prod.yml down")
        run_remote_command(client, f"cd {PROJECT_DIR}/docker && docker-compose -f docker-compose.prod.yml up -d --build")

        # 6. 等待服务启动
        print("\n等待服务启动...")
        import time
        time.sleep(10)

        # 7. 初始化数据库
        print("\n" + "=" * 60)
        print("步骤 6: 初始化数据库")
        print("=" * 60)
        run_remote_command(client, f"cd {PROJECT_DIR}/docker && docker-compose -f docker-compose.prod.yml exec -T api python -m scripts.init_db")
        run_remote_command(client, f"cd {PROJECT_DIR}/docker && docker-compose -f docker-compose.prod.yml exec -T api python -m scripts.seed_data")
        run_remote_command(client, f"cd {PROJECT_DIR}/docker && docker-compose -f docker-compose.prod.yml exec -T api python -m scripts.seed_role_permissions")

        # 8. 检查服务状态
        print("\n" + "=" * 60)
        print("步骤 7: 检查服务状态")
        print("=" * 60)
        run_remote_command(client, f"cd {PROJECT_DIR}/docker && docker-compose -f docker-compose.prod.yml ps")

        # 9. 显示日志
        print("\n" + "=" * 60)
        print("最近日志")
        print("=" * 60)
        run_remote_command(client, f"cd {PROJECT_DIR}/docker && docker-compose -f docker-compose.prod.yml logs --tail=20 api")

        print("\n" + "=" * 60)
        print("部署完成!")
        print("=" * 60)
        print(f"\nAPI 地址: http://{SERVER_HOST}:8001")
        print(f"API 文档: http://{SERVER_HOST}:8001/docs")
        print(f"\n前端域名: https://{DOMAIN}")
        print("\n请配置域名 DNS:")
        print(f"  A 记录: {DOMAIN} -> {SERVER_HOST}")
        print("\n查看日志:")
        print(f"  ssh {SERVER_USER}@{SERVER_HOST}")
        print(f"  cd {PROJECT_DIR}/docker")
        print(f"  docker-compose -f docker-compose.prod.yml logs -f")

    except Exception as e:
        print(f"\n部署失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        client.close()

if __name__ == "__main__":
    main()
