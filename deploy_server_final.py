#!/usr/bin/env python3
"""最终部署脚本 - 清理并重新部署"""

import paramiko
import os
from pathlib import Path

SERVER_HOST = os.getenv("SERVER_HOST", "8.134.33.19")
SERVER_USER = os.getenv("SERVER_USER", "root")
SERVER_PASSWORD = os.getenv("SERVER_PASSWORD")

if not SERVER_PASSWORD:
    print("错误: 必须设置 SERVER_PASSWORD 环境变量")
    sys.exit(1)
PROJECT_DIR = "/opt/yilehang-server"

def run_cmd(ssh, cmd, desc=""):
    if desc:
        print(f"\n{desc}")
    print(f"$ {cmd}")
    stdin, stdout, stderr = ssh.exec_command(cmd)
    exit_code = stdout.channel.recv_exit_status()
    out = stdout.read().decode('utf-8', errors='ignore')
    err = stderr.read().decode('utf-8', errors='ignore')
    if out:
        print(out)
    if err and exit_code != 0:
        print(f"[ERROR] {err}")
    return exit_code, out, err

def upload_dir(sftp, local_dir, remote_dir):
    """递归上传目录"""
    local_path = Path(local_dir)
    for item in local_path.rglob('*'):
        if item.is_file():
            rel_path = item.relative_to(local_path)
            remote_file = f"{remote_dir}/{rel_path}".replace('\\', '/')
            remote_parent = os.path.dirname(remote_file)

            # 创建远程目录
            try:
                sftp.stat(remote_parent)
            except:
                run_cmd(ssh, f"mkdir -p {remote_parent}")

            sftp.put(str(item), remote_file)

def main():
    print("=" * 60)
    print("最终部署")
    print("=" * 60)

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        print(f"\n连接 {SERVER_HOST}...")
        ssh.connect(SERVER_HOST, username=SERVER_USER, password=SERVER_PASSWORD)
        print("[OK]")

        # 1. 清理
        print("\n" + "=" * 60)
        print("步骤 1: 清理")
        print("=" * 60)

        run_cmd(ssh, f"cd {PROJECT_DIR}/deploy/server && docker-compose down -v 2>/dev/null || true", "停止容器")
        run_cmd(ssh, "docker images | grep server | awk '{print $3}' | xargs -r docker rmi -f", "删除镜像")

        # 2. 上传文件
        print("\n" + "=" * 60)
        print("步骤 2: 上传文件")
        print("=" * 60)

        sftp = ssh.open_sftp()

        # 上传 apps/api
        print("上传 apps/api...")
        local_api = "E:/project/yilehang/apps/api"
        upload_dir(sftp, local_api, f"{PROJECT_DIR}/apps/api")

        # 上传 deploy/server
        print("上传 deploy/server...")
        for f in ['Dockerfile', 'nginx.conf', '.env.example']:
            local_f = f"E:/project/yilehang/deploy/server/{f}"
            remote_f = f"{PROJECT_DIR}/deploy/server/{f}"
            sftp.put(local_f, remote_f)

        # 上传正确的 docker-compose.yml
        local_compose = "E:/project/yilehang/deploy/server/docker-compose.yml"
        remote_compose = f"{PROJECT_DIR}/deploy/server/docker-compose.yml"
        sftp.put(local_compose, remote_compose)

        sftp.close()
        print("[OK]")

        # 3. 创建 .env
        print("\n" + "=" * 60)
        print("步骤 3: 配置环境变量")
        print("=" * 60)

        env_content = """POSTGRES_USER=postgres
POSTGRES_PASSWORD=yilehang2024secure
POSTGRES_DB=yilehang
SECRET_KEY=prod-key-$(openssl rand -hex 16)
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
DEV_PRINT_CODE_ON_SEND_FAIL=false"""

        run_cmd(ssh, f"cd {PROJECT_DIR}/deploy/server && cat > .env << 'EOF'\n{env_content}\nEOF")

        # 4. 启动
        print("\n" + "=" * 60)
        print("步骤 4: 启动服务")
        print("=" * 60)

        run_cmd(ssh, f"cd {PROJECT_DIR}/deploy/server && docker-compose up -d --build", "构建并启动")

        # 等待
        print("\n等待 20 秒...")
        import time
        time.sleep(20)

        # 5. 初始化数据库
        print("\n" + "=" * 60)
        print("步骤 5: 初始化数据库")
        print("=" * 60)

        run_cmd(ssh, f"cd {PROJECT_DIR}/deploy/server && docker-compose exec -T api python -m scripts.init_db")
        run_cmd(ssh, f"cd {PROJECT_DIR}/deploy/server && docker-compose exec -T api python -m scripts.seed_data")
        run_cmd(ssh, f"cd {PROJECT_DIR}/deploy/server && docker-compose exec -T api python -m scripts.seed_role_permissions")

        # 6. 检查
        print("\n" + "=" * 60)
        print("步骤 6: 检查")
        print("=" * 60)

        run_cmd(ssh, f"cd {PROJECT_DIR}/deploy/server && docker-compose ps")
        run_cmd(ssh, "curl -s http://localhost/health")

        print("\n" + "=" * 60)
        print("完成!")
        print("=" * 60)
        print(f"\nAPI: http://{SERVER_HOST}")
        print(f"文档: http://{SERVER_HOST}/docs")

    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        ssh.close()

    return 0

if __name__ == "__main__":
    exit(main())
