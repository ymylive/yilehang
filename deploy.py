#!/usr/bin/env python3
"""
易乐航部署脚本 - 部署到远程服务器
"""
import subprocess
import sys

# 服务器配置
SERVER_HOST = "8.134.33.19"
SERVER_USER = "root"
SERVER_PASSWORD = "Qq159741"
DOMAIN = "yilehang.cornna.xyz"
PROJECT_DIR = "/opt/yilehang"

def run_ssh_command(command):
    """通过 SSH 执行远程命令"""
    ssh_cmd = f'sshpass -p "{SERVER_PASSWORD}" ssh -o StrictHostKeyChecking=no {SERVER_USER}@{SERVER_HOST} "{command}"'
    print(f"执行: {command}")
    result = subprocess.run(ssh_cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"错误: {result.stderr}")
    else:
        print(result.stdout)
    return result.returncode == 0

def upload_files():
    """上传项目文件到服务器"""
    print("\n=== 上传项目文件 ===")
    rsync_cmd = f'sshpass -p "{SERVER_PASSWORD}" rsync -avz --exclude "node_modules" --exclude ".git" --exclude "dist" --exclude "__pycache__" --exclude "*.pyc" -e "ssh -o StrictHostKeyChecking=no" . {SERVER_USER}@{SERVER_HOST}:{PROJECT_DIR}/'
    result = subprocess.run(rsync_cmd, shell=True)
    return result.returncode == 0

def main():
    print("=== 易乐航部署脚本 ===")
    print(f"目标服务器: {SERVER_HOST}")
    print(f"域名: {DOMAIN}")

    # 1. 检查 sshpass 是否安装
    if subprocess.run("where sshpass", shell=True, capture_output=True).returncode != 0:
        print("\n错误: 需要安装 sshpass")
        print("Windows 用户请使用 WSL 或手动部署")
        sys.exit(1)

    # 2. 创建项目目录
    print("\n=== 创建项目目录 ===")
    run_ssh_command(f"mkdir -p {PROJECT_DIR}")

    # 3. 上传文件
    if not upload_files():
        print("文件上传失败")
        sys.exit(1)

    # 4. 安装 Docker
    print("\n=== 检查 Docker ===")
    run_ssh_command("docker --version || curl -fsSL https://get.docker.com | sh")
    run_ssh_command("docker-compose --version || curl -L https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m) -o /usr/local/bin/docker-compose && chmod +x /usr/local/bin/docker-compose")

    # 5. 创建 .env 文件
    print("\n=== 创建环境变量文件 ===")
    env_content = f"""POSTGRES_PASSWORD=yilehang2024
SECRET_KEY=your-secret-key-change-in-production
WECHAT_APPID=wxdbd150a0458a3c7c
WECHAT_SECRET=
DOMAIN={DOMAIN}
"""
    run_ssh_command(f"cd {PROJECT_DIR}/docker && cat > .env << 'EOF'\n{env_content}\nEOF")

    # 6. 构建前端
    print("\n=== 构建统一小程序 ===")
    run_ssh_command(f"cd {PROJECT_DIR} && command -v pnpm || npm install -g pnpm")
    run_ssh_command(f"cd {PROJECT_DIR}/apps/unified-miniapp && pnpm install && pnpm run build:mp-weixin")

    # 7. 启动 Docker 容器
    print("\n=== 启动 Docker 容器 ===")
    run_ssh_command(f"cd {PROJECT_DIR}/docker && docker-compose -f docker-compose.prod.yml down")
    run_ssh_command(f"cd {PROJECT_DIR}/docker && docker-compose -f docker-compose.prod.yml up -d --build")

    # 8. 初始化数据库
    print("\n=== 初始化数据库 ===")
    run_ssh_command(f"cd {PROJECT_DIR}/docker && docker-compose -f docker-compose.prod.yml exec -T api python -m scripts.init_db")
    run_ssh_command(f"cd {PROJECT_DIR}/docker && docker-compose -f docker-compose.prod.yml exec -T api python -m scripts.seed_data")

    # 9. 检查服务状态
    print("\n=== 检查服务状态 ===")
    run_ssh_command(f"cd {PROJECT_DIR}/docker && docker-compose -f docker-compose.prod.yml ps")

    print("\n=== 部署完成 ===")
    print(f"API 地址: http://{SERVER_HOST}:8001")
    print(f"前端地址: http://{DOMAIN} (需配置 DNS)")
    print("\n请配置域名 DNS:")
    print(f"  A 记录: {DOMAIN} -> {SERVER_HOST}")

if __name__ == "__main__":
    main()
