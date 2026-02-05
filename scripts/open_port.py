"""开放防火墙端口"""
import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect("8.134.33.19", username="root", password="Qq159741", timeout=30)

def run(cmd):
    print(f">>> {cmd}")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=60)
    out = stdout.read().decode('utf-8', errors='ignore')
    err = stderr.read().decode('utf-8', errors='ignore')
    if out:
        print(out)
    if err:
        print(err)

print("=== 检查防火墙状态 ===")
run("ufw status 2>/dev/null || iptables -L INPUT -n | head -10")

print("\n=== 开放8088端口 ===")
run("ufw allow 8088/tcp 2>/dev/null || iptables -I INPUT -p tcp --dport 8088 -j ACCEPT")

print("\n=== 检查阿里云安全组提示 ===")
print("注意: 如果是阿里云服务器，还需要在阿里云控制台的安全组中开放8088端口")

print("\n=== 测试API ===")
run("curl -s http://localhost:8088/docs | head -5")

client.close()
print("\n部署完成!")
print("访问地址: http://8.134.33.19:8088/")
print("API文档: http://8.134.33.19:8088/docs")
print("\n如果无法访问，请在阿里云控制台安全组中添加入站规则: TCP 8088端口")
