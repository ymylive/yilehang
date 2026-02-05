"""
閮ㄧ讲鑴氭湰 - 鐢ㄤ簬灏嗛」鐩儴缃插埌VPS鏈嶅姟鍣?"""
import argparse
import subprocess
import sys
from pathlib import Path


def run_command(cmd: str, check: bool = True) -> subprocess.CompletedProcess:
    """鎵ц鍛戒护"""
    print(f"鎵ц: {cmd}")
    return subprocess.run(cmd, shell=True, check=check)


def deploy(host: str, user: str, password: str, port: int = 22):
    """閮ㄧ讲鍒版湇鍔″櫒"""
    print(f"寮€濮嬮儴缃插埌 {user}@{host}:{port}")

    # 椤圭洰鏍圭洰褰?    project_root = Path(__file__).parent.parent

    # 鏋勫缓鍓嶇
    print("\n=== 鏋勫缓鍓嶇 ===")
    run_command("pnpm build:client", check=False)
    run_command("pnpm build:admin", check=False)

    # 浣跨敤sshpass杩涜SSH鎿嶄綔
    ssh_cmd = f"sshpass -p '{password}' ssh -o StrictHostKeyChecking=no -p {port} {user}@{host}"

    # 鍒涘缓杩滅▼鐩綍
    print("\n=== 鍒涘缓杩滅▼鐩綍 ===")
    run_command(f"{ssh_cmd} 'mkdir -p /opt/yilehang'")

    # 鍚屾鏂囦欢
    print("\n=== 鍚屾鏂囦欢 ===")
    rsync_cmd = f"sshpass -p '{password}' rsync -avz --exclude 'node_modules' --exclude '__pycache__' --exclude '.git' -e 'ssh -o StrictHostKeyChecking=no -p {port}' {project_root}/ {user}@{host}:/opt/yilehang/"
    run_command(rsync_cmd)

    # 鍦ㄦ湇鍔″櫒涓婃墽琛岄儴缃插懡浠?    print("\n=== 鍚姩鏈嶅姟 ===")
    remote_commands = """
    cd /opt/yilehang
    docker-compose -f docker/docker-compose.prod.yml down
    docker-compose -f docker/docker-compose.prod.yml up -d --build
    """
    run_command(f"{ssh_cmd} '{remote_commands}'")

    print("\n=== 閮ㄧ讲瀹屾垚 ===")
    print(f"API鍦板潃: http://{host}:8000")
    print(f"绠＄悊鍚庡彴: http://{host}:3000")


def main():
    parser = argparse.ArgumentParser(description="鏄撲箰鑸儴缃茶剼鏈?)
    parser.add_argument("--host", required=True, help="鏈嶅姟鍣↖P鍦板潃")
    parser.add_argument("--user", default="root", help="SSH鐢ㄦ埛鍚?)
    parser.add_argument("--password", required=True, help="SSH瀵嗙爜")
    parser.add_argument("--port", type=int, default=22, help="SSH绔彛")

    args = parser.parse_args()

    try:
        deploy(args.host, args.user, args.password, args.port)
    except subprocess.CalledProcessError as e:
        print(f"閮ㄧ讲澶辫触: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
