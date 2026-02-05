"""检查服务状态"""
import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect("8.134.33.19", username="root", password="Qq159741", timeout=30)

def run(cmd):
    print(f">>> {cmd}")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=60)
    print(stdout.read().decode('utf-8', errors='ignore'))
    print(stderr.read().decode('utf-8', errors='ignore'))

print("=== Docker容器状态 ===")
run("docker ps -a")

print("\n=== API日志 ===")
run("docker logs yilehang-api --tail 30 2>&1")

print("\n=== 检查端口 ===")
run("netstat -tlnp | grep 8088")

print("\n=== 测试本地访问 ===")
run("curl -s http://localhost:8088/ | head -3")

client.close()
