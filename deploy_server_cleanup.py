#!/usr/bin/env python3
"""清理并重新部署服务端模块到远程服务器"""

import paramiko
import os
from pathlib import Path

# 服务器配置
SERVER_HOST = os.getenv("SERVER_HOST", "8.134.33.19")
SERVER_USER = os.getenv("SERVER_USER", "root")
SERVER_PASSWORD = os.getenv("SERVER_PASSWORD")

if not SERVER_PASSWORD:
    print("错误: 必须设置 SERVER_PASSWORD 环境变量")
    sys.exit(1)
PROJECT_DIR = "/opt/yilehang-server"

def run_remote_command(ssh, command, description=""):
    """执行远程命令"""
    if description:
        print(f"\n执行: {description}")
    print(f"命令: {command}")

    stdin, stdout, stderr = ssh.exec_command(command)
    exit_code = stdout.channel.recv_exit_status()

    output = stdout.read().decode('utf-8', errors='ignore')
    error = stderr.read().decode('utf-8', errors='ignore')

    if output:
        print(output)
    if error and exit_code != 0:
        print(f"[ERROR] {error}")

    return exit_code, output, error

def main():
    print("=" * 60)
    print("清理并重新部署服务端模块")
    print("=" * 60)

    # 连接服务器
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        print(f"\n连接到服务器 {SERVER_HOST}...")
        ssh.connect(SERVER_HOST, username=SERVER_USER, password=SERVER_PASSWORD)
        print("[OK] 已连接")

        # 1. 停止并删除所有容器
        print("\n" + "=" * 60)
        print("步骤 1: 清理旧容器")
        print("=" * 60)

        run_remote_command(ssh,
            f"cd {PROJECT_DIR}/deploy/server && docker-compose down -v",
            "停止并删除容器和卷")

        # 2. 删除旧镜像
        run_remote_command(ssh,
            "docker images | grep server | awk '{print $3}' | xargs -r docker rmi -f",
            "删除旧镜像")

        # 3. 清理构建缓存
        run_remote_command(ssh,
            "docker builder prune -af",
            "清理构建缓存")

        # 4. 修改 docker-compose.yml 使用简化构建
        print("\n" + "=" * 60)
        print("步骤 2: 修改 docker-compose.yml")
        print("=" * 60)

        # 读取并修改 docker-compose.yml，移除 version 字段
        compose_content = """services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - backend
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
      interval: 5s
      timeout: 5s
      retries: 5

  api:
    build:
      context: ../../apps/api
      dockerfile: ../../deploy/server/Dockerfile
    environment:
      DATABASE_URL: postgresql+asyncpg://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}
      SECRET_KEY: ${SECRET_KEY}
      DEBUG: ${DEBUG}
      WECHAT_APPID: ${WECHAT_APPID}
      WECHAT_SECRET: ${WECHAT_SECRET}
      ALLOW_WECHAT_LOGIN_WITHOUT_SECRET: ${ALLOW_WECHAT_LOGIN_WITHOUT_SECRET}
      SMTP_HOST: ${SMTP_HOST}
      SMTP_PORT: ${SMTP_PORT}
      SMTP_USER: ${SMTP_USER}
      SMTP_PASSWORD: ${SMTP_PASSWORD}
      SMTP_FROM: ${SMTP_FROM}
      SMTP_USE_SSL: ${SMTP_USE_SSL}
      DEV_PRINT_CODE_ON_SEND_FAIL: ${DEV_PRINT_CODE_ON_SEND_FAIL}
    depends_on:
      postgres:
        condition: service_healthy
    volumes:
      - api_uploads:/app/uploads
    networks:
      - backend
    healthcheck:
      test: ["CMD-SHELL", "python -c 'import urllib.request; urllib.request.urlopen(\"http://localhost:8000/health\")'"]
      interval: 30s
      timeout: 10s
      retries: 3

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - api
    networks:
      - backend
    healthcheck:
      test: ["CMD", "wget", "--quiet", "--tries=1", "--spider", "http://localhost/health"]
      interval: 30s
      timeout: 10s
      retries: 3

volumes:
  postgres_data:
  api_uploads:

networks:
  backend:
    driver: bridge
"""

        # 上传新的 docker-compose.yml
        sftp = ssh.open_sftp()
        remote_file = f"{PROJECT_DIR}/deploy/server/docker-compose.yml"
        with sftp.file(remote_file, 'w') as f:
            f.write(compose_content)
        sftp.close()
        print("[OK] 已更新 docker-compose.yml")

        # 5. 启动服务
        print("\n" + "=" * 60)
        print("步骤 3: 启动服务")
        print("=" * 60)

        run_remote_command(ssh,
            f"cd {PROJECT_DIR}/deploy/server && docker-compose up -d --build",
            "构建并启动服务")

        # 等待服务启动
        print("\n等待服务启动...")
        import time
        time.sleep(15)

        # 6. 初始化数据库
        print("\n" + "=" * 60)
        print("步骤 4: 初始化数据库")
        print("=" * 60)

        run_remote_command(ssh,
            f"cd {PROJECT_DIR}/deploy/server && docker-compose exec -T api python -m scripts.init_db",
            "初始化数据库表")

        run_remote_command(ssh,
            f"cd {PROJECT_DIR}/deploy/server && docker-compose exec -T api python -m scripts.seed_data",
            "创建测试数据")

        run_remote_command(ssh,
            f"cd {PROJECT_DIR}/deploy/server && docker-compose exec -T api python -m scripts.seed_role_permissions",
            "初始化角色权限")

        # 7. 检查服务状态
        print("\n" + "=" * 60)
        print("步骤 5: 检查服务状态")
        print("=" * 60)

        run_remote_command(ssh,
            f"cd {PROJECT_DIR}/deploy/server && docker-compose ps",
            "查看容器状态")

        # 8. 测试 API
        print("\n" + "=" * 60)
        print("步骤 6: 测试 API")
        print("=" * 60)

        run_remote_command(ssh,
            "curl -s http://localhost/health || echo '健康检查失败'",
            "测试健康检查端点")

        print("\n" + "=" * 60)
        print("部署完成!")
        print("=" * 60)
        print(f"\nAPI 地址: http://{SERVER_HOST}")
        print(f"API 文档: http://{SERVER_HOST}/docs")
        print(f"健康检查: http://{SERVER_HOST}/health")
        print("\n查看日志:")
        print(f"  ssh root@{SERVER_HOST}")
        print(f"  cd {PROJECT_DIR}/deploy/server")
        print(f"  docker-compose logs -f")

    except Exception as e:
        print(f"\n[ERROR] 部署失败: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        ssh.close()

    return 0

if __name__ == "__main__":
    exit(main())
