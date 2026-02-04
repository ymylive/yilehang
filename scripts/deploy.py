"""
部署脚本 - 用于将项目部署到VPS服务器
"""
import argparse
import subprocess
import sys
from pathlib import Path


def run_command(cmd: str, check: bool = True) -> subprocess.CompletedProcess:
    """执行命令"""
    print(f"执行: {cmd}")
    return subprocess.run(cmd, shell=True, check=check)


def deploy(host: str, user: str, password: str, port: int = 22):
    """部署到服务器"""
    print(f"开始部署到 {user}@{host}:{port}")

    # 项目根目录
    project_root = Path(__file__).parent.parent

    # 构建前端
    print("\n=== 构建前端 ===")
    run_command("pnpm build:client", check=False)
    run_command("pnpm build:admin", check=False)

    # 使用sshpass进行SSH操作
    ssh_cmd = f"sshpass -p '{password}' ssh -o StrictHostKeyChecking=no -p {port} {user}@{host}"

    # 创建远程目录
    print("\n=== 创建远程目录 ===")
    run_command(f"{ssh_cmd} 'mkdir -p /opt/yilehang'")

    # 同步文件
    print("\n=== 同步文件 ===")
    rsync_cmd = f"sshpass -p '{password}' rsync -avz --exclude 'node_modules' --exclude '__pycache__' --exclude '.git' -e 'ssh -o StrictHostKeyChecking=no -p {port}' {project_root}/ {user}@{host}:/opt/yilehang/"
    run_command(rsync_cmd)

    # 在服务器上执行部署命令
    print("\n=== 启动服务 ===")
    remote_commands = """
    cd /opt/yilehang
    docker-compose -f docker/docker-compose.prod.yml down
    docker-compose -f docker/docker-compose.prod.yml up -d --build
    """
    run_command(f"{ssh_cmd} '{remote_commands}'")

    print("\n=== 部署完成 ===")
    print(f"API地址: http://{host}:8000")
    print(f"管理后台: http://{host}:3000")


def main():
    parser = argparse.ArgumentParser(description="易乐航部署脚本")
    parser.add_argument("--host", required=True, help="服务器IP地址")
    parser.add_argument("--user", default="root", help="SSH用户名")
    parser.add_argument("--password", required=True, help="SSH密码")
    parser.add_argument("--port", type=int, default=22, help="SSH端口")

    args = parser.parse_args()

    try:
        deploy(args.host, args.user, args.password, args.port)
    except subprocess.CalledProcessError as e:
        print(f"部署失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
