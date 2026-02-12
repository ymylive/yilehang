#!/usr/bin/env python3
"""
部署脚本 - 包含SSL证书申请和服务部署
"""
import os
import sys
import subprocess
from pathlib import Path

def run_cmd(cmd, check=True, cwd=None):
    """执行命令"""
    print(f"执行: {cmd}")
    result = subprocess.run(cmd, shell=True, check=check, cwd=cwd,
                          capture_output=True, text=True)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    return result

def get_server_info():
    """获取服务器信息"""
    server_ip = input("请输入服务器IP: ").strip()
    server_user = input("请输入SSH用户名 [root]: ").strip() or "root"
    server_port = input("请输入SSH端口 [22]: ").strip() or "22"
    return server_ip, server_user, server_port

def install_acme_sh(server_ip, server_user, server_port):
    """安装acme.sh"""
    print("\n=== 安装acme.sh ===")
    cmd = f'ssh -p {server_port} {server_user}@{server_ip} "curl https://get.acme.sh | sh -s email=admin@rl.cornna.xyz"'
    run_cmd(cmd, check=False)

def apply_ssl_cert(server_ip, server_user, server_port, domain):
    """申请SSL证书"""
    print(f"\n=== 申请SSL证书: {domain} ===")

    # 获取Cloudflare API信息
    cf_email = input("请输入Cloudflare邮箱: ").strip()
    cf_key = input("请输入Cloudflare Global API Key: ").strip()

    # 设置环境变量并申请证书
    cmd = f'''ssh -p {server_port} {server_user}@{server_ip} "
export CF_Email='{cf_email}'
export CF_Key='{cf_key}'
~/.acme.sh/acme.sh --issue --dns dns_cf -d {domain}
"'''
    run_cmd(cmd)

def deploy_services(server_ip, server_user, server_port):
    """部署服务"""
    print("\n=== 部署服务 ===")

    # 上传配置文件
    print("上传配置文件...")
    run_cmd(f'scp -P {server_port} deploy/server/nginx-ssl.conf {server_user}@{server_ip}:/root/yilehang/deploy/server/')
    run_cmd(f'scp -P {server_port} deploy/server/docker-compose-ssl.yml {server_user}@{server_ip}:/root/yilehang/deploy/server/')
    run_cmd(f'scp -P {server_port} deploy/server/Dockerfile {server_user}@{server_ip}:/root/yilehang/deploy/server/')

    # 上传后端代码
    print("上传后端代码...")
    run_cmd(f'scp -P {server_port} -r apps/api {server_user}@{server_ip}:/root/yilehang/apps/')

    # 停止旧服务
    print("停止旧服务...")
    cmd = f'ssh -p {server_port} {server_user}@{server_ip} "cd /root/yilehang/deploy/server && docker-compose down"'
    run_cmd(cmd, check=False)

    # 启动新服务
    print("启动新服务...")
    cmd = f'ssh -p {server_port} {server_user}@{server_ip} "cd /root/yilehang/deploy/server && docker-compose -f docker-compose-ssl.yml up -d --build"'
    run_cmd(cmd)

    # 检查服务状态
    print("检查服务状态...")
    cmd = f'ssh -p {server_port} {server_user}@{server_ip} "cd /root/yilehang/deploy/server && docker-compose -f docker-compose-ssl.yml ps"'
    run_cmd(cmd)

def main():
    print("=== 韧翎成长计划服务器部署脚本 (含SSL) ===\n")

    # 获取服务器信息
    server_ip, server_user, server_port = get_server_info()
    domain = "rl.cornna.xyz"

    # 询问是否需要申请SSL证书
    need_ssl = input("\n是否需要申请SSL证书? (y/n) [y]: ").strip().lower() or "y"

    if need_ssl == "y":
        # 安装acme.sh
        install_acme = input("是否需要安装acme.sh? (y/n) [n]: ").strip().lower() or "n"
        if install_acme == "y":
            install_acme_sh(server_ip, server_user, server_port)

        # 申请SSL证书
        apply_ssl_cert(server_ip, server_user, server_port, domain)

    # 部署服务
    deploy_confirm = input("\n是否开始部署服务? (y/n) [y]: ").strip().lower() or "y"
    if deploy_confirm == "y":
        deploy_services(server_ip, server_user, server_port)
        print(f"\n✅ 部署完成! 服务地址: https://{domain}")
    else:
        print("取消部署")

if __name__ == "__main__":
    main()
