"""
微信小程序上传脚本 - 上传测试版本
需要配置微信小程序上传密钥
"""
import os
import sys
import json
import subprocess
from pathlib import Path

# 小程序配置
APPS = {
    'client': {
        'name': '乐航成长',
        'appid': 'wxdbd150a0458a3c7c',
        'build_dir': 'apps/client/dist/build/mp-weixin',
        'version': '1.0.0',
        'desc': '易乐航·ITS智慧体教云平台 - 学员/家长端'
    },
    'coach': {
        'name': '易乐航教练端',
        'appid': 'wxdbd150a0458a3c7c',
        'build_dir': 'apps/coach/dist/build/mp-weixin',
        'version': '1.0.0',
        'desc': '易乐航·ITS智慧体教云平台 - 教练端'
    }
}

PROJECT_ROOT = Path(__file__).parent.parent

def check_wechat_cli():
    """检查微信开发者工具CLI是否安装"""
    try:
        result = subprocess.run(['wechatdevtools', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"[微信工具] 已安装: {result.stdout.strip()}")
            return True
    except FileNotFoundError:
        pass

    print("[微信工具] 未找到微信开发者工具CLI")
    print("请按以下步骤操作:")
    print("1. 下载微信开发者工具: https://developers.weixin.qq.com/miniprogram/dev/devtools/download.html")
    print("2. 安装后配置CLI环境变量")
    print("3. 或者手动在微信开发者工具中上传")
    return False

def upload_with_cli(app_name, app_config):
    """使用微信CLI上传"""
    build_dir = PROJECT_ROOT / app_config['build_dir']

    if not build_dir.exists():
        print(f"[错误] 构建目录不存在: {build_dir}")
        return False

    print(f"\n[上传] {app_config['name']} ({app_name})")
    print(f"  构建目录: {build_dir}")
    print(f"  版本: {app_config['version']}")
    print(f"  描述: {app_config['desc']}")

    # 使用微信开发者工具CLI上传
    cmd = [
        'wechatdevtools',
        'upload',
        '--project', str(build_dir),
        '--version', app_config['version'],
        '--desc', app_config['desc']
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        if result.returncode == 0:
            print(f"[成功] {app_config['name']} 上传成功")
            return True
        else:
            print(f"[错误] 上传失败: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print(f"[错误] 上传超时")
        return False
    except Exception as e:
        print(f"[错误] {e}")
        return False

def generate_upload_guide():
    """生成手动上传指南"""
    guide = """
=== 微信小程序手动上传指南 ===

由于微信开发者工具CLI需要特殊配置，建议使用以下方式上传:

1. 打开微信开发者工具
2. 选择"导入项目"
3. 选择以下目录之一:
   - 学员端: apps/client/dist/build/mp-weixin
   - 教练端: apps/coach/dist/build/mp-weixin
4. 点击"上传"按钮
5. 填写版本号和更新说明
6. 点击"上传"

上传后的版本将显示在微信小程序后台的"测试版本"中。

=== 版本信息 ===

学员端 (乐航成长):
- 版本: 1.0.0
- 描述: 易乐航·ITS智慧体教云平台 - 学员/家长端
- 路径: apps/client/dist/build/mp-weixin

教练端 (易乐航教练端):
- 版本: 1.0.0
- 描述: 易乐航·ITS智慧体教云平台 - 教练端
- 路径: apps/coach/dist/build/mp-weixin

=== 测试步骤 ===

1. 在微信小程序后台设置测试账号
2. 使用测试账号扫描二维码进入测试版本
3. 测试以下功能:
   - 登录/注册
   - 预约课程
   - 查看课时卡
   - 消费记录
   - 教练评价

=== 发布步骤 ===

1. 在微信小程序后台提交审核
2. 等待审核通过 (通常1-3天)
3. 审核通过后点击"发布"
4. 小程序将在微信中上线
"""
    return guide

def main():
    print("=" * 50)
    print("微信小程序上传工具")
    print("=" * 50)

    # 检查构建文件
    print("\n[检查] 验证构建文件...")
    all_built = True
    for app_name, app_config in APPS.items():
        build_dir = PROJECT_ROOT / app_config['build_dir']
        if build_dir.exists():
            print(f"  [OK] {app_config['name']}: {build_dir}")
        else:
            print(f"  [FAIL] {app_config['name']}: 未找到")
            all_built = False

    if not all_built:
        print("\n[错误] 部分小程序未构建，请先运行:")
        print("  cd apps/client && pnpm build:mp-weixin")
        print("  cd apps/coach && pnpm build:mp-weixin")
        sys.exit(1)

    # 检查微信工具
    print("\n[检查] 微信开发者工具...")
    has_cli = check_wechat_cli()

    if has_cli:
        # 尝试使用CLI上传
        print("\n[上传] 开始上传...")
        success_count = 0
        for app_name, app_config in APPS.items():
            if upload_with_cli(app_name, app_config):
                success_count += 1

        print(f"\n[完成] 成功上传 {success_count}/{len(APPS)} 个小程序")
    else:
        # 生成手动上传指南
        print("\n" + generate_upload_guide())

    # 生成上传信息文件
    upload_info = {
        'timestamp': __import__('datetime').datetime.now().isoformat(),
        'apps': APPS,
        'build_dirs': {
            app_name: str(PROJECT_ROOT / app_config['build_dir'])
            for app_name, app_config in APPS.items()
        }
    }

    info_file = PROJECT_ROOT / 'upload_info.json'
    with open(info_file, 'w', encoding='utf-8') as f:
        json.dump(upload_info, f, ensure_ascii=False, indent=2)

    print(f"\n[信息] 上传信息已保存到: {info_file}")

if __name__ == "__main__":
    main()
