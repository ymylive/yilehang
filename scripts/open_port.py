"""寮€鏀鹃槻鐏绔彛"""
import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect("82.158.88.34", username="root", password="Qq159741", timeout=30)

def run(cmd):
    print(f">>> {cmd}")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=60)
    out = stdout.read().decode('utf-8', errors='ignore')
    err = stderr.read().decode('utf-8', errors='ignore')
    if out:
        print(out)
    if err:
        print(err)

print("=== 妫€鏌ラ槻鐏鐘舵€?===")
run("ufw status 2>/dev/null || iptables -L INPUT -n | head -10")

print("\n=== 寮€鏀?088绔彛 ===")
run("ufw allow 8088/tcp 2>/dev/null || iptables -I INPUT -p tcp --dport 8088 -j ACCEPT")

print("\n=== 妫€鏌ラ樋閲屼簯瀹夊叏缁勬彁绀?===")
print("娉ㄦ剰: 濡傛灉鏄樋閲屼簯鏈嶅姟鍣紝杩橀渶瑕佸湪闃块噷浜戞帶鍒跺彴鐨勫畨鍏ㄧ粍涓紑鏀?088绔彛")

print("\n=== 娴嬭瘯API ===")
run("curl -s http://localhost:8088/docs | head -5")

client.close()
print("\n閮ㄧ讲瀹屾垚!")
print("璁块棶鍦板潃: http://82.158.88.34:8088/")
print("API鏂囨。: http://82.158.88.34:8088/docs")
print("\n濡傛灉鏃犳硶璁块棶锛岃鍦ㄩ樋閲屼簯鎺у埗鍙板畨鍏ㄧ粍涓坊鍔犲叆绔欒鍒? TCP 8088绔彛")
