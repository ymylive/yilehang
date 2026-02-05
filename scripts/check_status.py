"""妫€鏌ユ湇鍔＄姸鎬?""
import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect("82.158.88.34", username="root", password="Qq159741", timeout=30)

def run(cmd):
    print(f">>> {cmd}")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=60)
    print(stdout.read().decode('utf-8', errors='ignore'))
    print(stderr.read().decode('utf-8', errors='ignore'))

print("=== Docker瀹瑰櫒鐘舵€?===")
run("docker ps -a")

print("\n=== API鏃ュ織 ===")
run("docker logs yilehang-api --tail 30 2>&1")

print("\n=== 妫€鏌ョ鍙?===")
run("netstat -tlnp | grep 8088")

print("\n=== 娴嬭瘯鏈湴璁块棶 ===")
run("curl -s http://localhost:8088/ | head -3")

client.close()
