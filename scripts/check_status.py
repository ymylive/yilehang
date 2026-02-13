"""妫€鏌ユ湇鍔＄姸鎬?""
import paramiko
import os
import sys

SERVER_HOST = os.getenv("SERVER_HOST", "82.158.88.34")
SERVER_USER = os.getenv("SERVER_USER", "root")
SERVER_PASSWORD = os.getenv("SERVER_PASSWORD")

if not SERVER_PASSWORD:
    print("错误: 必须设置 SERVER_PASSWORD 环境变量")
    sys.exit(1)

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(SERVER_HOST, username=SERVER_USER, password=SERVER_PASSWORD, timeout=30)

def run(cmd):
    print(f">>> {cmd}")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=60)
    print(stdout.read().decode('utf-8', errors='ignore'))
    print(stderr.read().decode('utf-8', errors='ignore'))

print("=== Docker瀹瑰櫒鐘舵€?===")
run("docker ps -a")

print("\n=== API鏃ュ織 ===")
run("docker logs renling-api --tail 30 2>&1")

print("\n=== 妫€鏌ョ鍙?===")
run("netstat -tlnp | grep 8088")

print("\n=== 娴嬭瘯鏈湴璁块棶 ===")
run("curl -s http://localhost:8088/ | head -3")

client.close()
