#!/usr/bin/env python3
"""
閮ㄧ讲鑴氭湰 - 浣跨敤涓绘満nginx浠ｇ悊鍒癉ocker API
"""
import paramiko
import os
from pathlib import Path

# 服务器配置
SERVER_HOST = '82.158.88.34'
SERVER_PORT = 22
SERVER_USER = 'root'
SERVER_PASSWORD = 'Qq159741'

# 杩滅▼璺緞
REMOTE_BASE = '/opt/yilehang'
REMOTE_DOCKER = f'{REMOTE_BASE}/docker'

def create_ssh_client():
    """鍒涘缓SSH瀹㈡埛绔?""
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=30)
    return client

def exec_command(client, command, description=""):
    """鎵цSSH鍛戒护"""
    if description:
        print(f"\n=== {description} ===")
    print(f"鎵ц: {command}")
    stdin, stdout, stderr = client.exec_command(command)
    output = stdout.read().decode('utf-8', errors='ignore')
    error = stderr.read().decode('utf-8', errors='ignore')
    if output:
        print(output)
    if error:
        print(f"閿欒: {error}")
    return output, error

def upload_file(sftp, local_path, remote_path):
    """涓婁紶鏂囦欢"""
    print(f"涓婁紶: {local_path} -> {remote_path}")
    sftp.put(local_path, remote_path)

def main():
    print("寮€濮嬮儴缃?..")

    client = create_ssh_client()
    sftp = client.open_sftp()

    try:
        # 1. 涓婁紶鏇存柊鐨刣ocker-compose.prod.yml
        print("\n姝ラ1: 涓婁紶docker-compose.prod.yml")
        local_compose = Path(__file__).parent.parent / 'docker' / 'docker-compose.prod.yml'
        upload_file(sftp, str(local_compose), f'{REMOTE_DOCKER}/docker-compose.prod.yml')

        # 2. 鍒涘缓nginx绔欑偣閰嶇疆
        print("\n姝ラ2: 鍒涘缓nginx绔欑偣閰嶇疆")
        nginx_config = """server {
    listen 80;
    server_name yilehang.cornna.xyz;

    # API浠ｇ悊
    location /api/ {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }

    # 闈欐€佹枃浠?- 灏忕▼搴忓鎴风
    location /client/ {
        alias /opt/yilehang/apps/client/dist/;
        try_files $uri $uri/ /client/index.html;
    }

    # 闈欐€佹枃浠?- 绠＄悊鍚庡彴
    location /admin/ {
        alias /opt/yilehang/apps/admin/dist/;
        try_files $uri $uri/ /admin/index.html;
    }

    # 榛樿棣栭〉
    location / {
        return 301 /client/;
    }
}
"""

        # 鍐欏叆nginx閰嶇疆鏂囦欢
        exec_command(client, f"cat > /etc/nginx/sites-available/yilehang << 'EOF'\n{nginx_config}\nEOF",
                    "鍒涘缓nginx閰嶇疆鏂囦欢")

        # 3. 鍚敤绔欑偣
        print("\n姝ラ3: 鍚敤nginx绔欑偣")
        exec_command(client, "ln -sf /etc/nginx/sites-available/yilehang /etc/nginx/sites-enabled/yilehang",
                    "鍒涘缓绗﹀彿閾炬帴")

        # 4. 娴嬭瘯nginx閰嶇疆
        print("\n姝ラ4: 娴嬭瘯nginx閰嶇疆")
        output, error = exec_command(client, "nginx -t", "娴嬭瘯nginx閰嶇疆")
        if "test is successful" not in output and "test is successful" not in error:
            print("璀﹀憡: nginx閰嶇疆娴嬭瘯澶辫触锛岃妫€鏌ラ厤缃?)
            return

        # 5. 鍋滄Docker nginx瀹瑰櫒
        print("\n姝ラ5: 鍋滄Docker nginx瀹瑰櫒")
        exec_command(client, f"cd {REMOTE_DOCKER} && docker compose -f docker-compose.prod.yml stop nginx && docker compose -f docker-compose.prod.yml rm -f nginx",
                    "鍋滄骞跺垹闄ocker nginx瀹瑰櫒")

        # 6. 閲嶅惎API鏈嶅姟
        print("\n姝ラ6: 閲嶅惎API鏈嶅姟")
        exec_command(client, f"cd {REMOTE_DOCKER} && docker compose -f docker-compose.prod.yml up -d --force-recreate api",
                    "閲嶅惎API鏈嶅姟")

        # 7. 閲嶈浇nginx
        print("\n姝ラ7: 閲嶈浇nginx")
        exec_command(client, "systemctl reload nginx", "閲嶈浇nginx閰嶇疆")

        # 8. 妫€鏌ユ湇鍔＄姸鎬?        print("\n姝ラ8: 妫€鏌ユ湇鍔＄姸鎬?)
        exec_command(client, f"cd {REMOTE_DOCKER} && docker compose -f docker-compose.prod.yml ps", "鏌ョ湅Docker瀹瑰櫒鐘舵€?)
        exec_command(client, "systemctl status nginx --no-pager -l", "鏌ョ湅nginx鐘舵€?)

        print("\n[OK] 閮ㄧ讲瀹屾垚!")
        print(f"API鍦板潃: http://yilehang.cornna.xyz/api/")
        print(f"瀹㈡埛绔? http://yilehang.cornna.xyz/client/")
        print(f"绠＄悊鍚庡彴: http://yilehang.cornna.xyz/admin/")

    except Exception as e:
        print(f"\n鉂?閮ㄧ讲澶辫触: {e}")
        import traceback
        traceback.print_exc()
    finally:
        sftp.close()
        client.close()

if __name__ == '__main__':
    main()
