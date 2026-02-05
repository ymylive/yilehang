"""
寰俊灏忕▼搴忎笂浼犺剼鏈?- 涓婁紶娴嬭瘯鐗堟湰
闇€瑕侀厤缃井淇″皬绋嬪簭涓婁紶瀵嗛挜
"""
import os
import sys
import json
import subprocess
from pathlib import Path

# 灏忕▼搴忛厤缃?APPS = {
    'client': {
        'name': '涔愯埅鎴愰暱',
        'appid': 'wxdbd150a0458a3c7c',
        'build_dir': 'apps/client/dist/build/mp-weixin',
        'version': '1.0.0',
        'desc': '鏄撲箰鑸稩TS鏅烘収浣撴暀浜戝钩鍙?- 瀛﹀憳/瀹堕暱绔?
    },
    'coach': {
        'name': '鏄撲箰鑸暀缁冪',
        'appid': 'wxdbd150a0458a3c7c',
        'build_dir': 'apps/coach/dist/build/mp-weixin',
        'version': '1.0.0',
        'desc': '鏄撲箰鑸稩TS鏅烘収浣撴暀浜戝钩鍙?- 鏁欑粌绔?
    }
}

PROJECT_ROOT = Path(__file__).parent.parent

def check_wechat_cli():
    """妫€鏌ュ井淇″紑鍙戣€呭伐鍏稢LI鏄惁瀹夎"""
    try:
        result = subprocess.run(['wechatdevtools', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"[寰俊宸ュ叿] 宸插畨瑁? {result.stdout.strip()}")
            return True
    except FileNotFoundError:
        pass

    print("[寰俊宸ュ叿] 鏈壘鍒板井淇″紑鍙戣€呭伐鍏稢LI")
    print("璇锋寜浠ヤ笅姝ラ鎿嶄綔:")
    print("1. 涓嬭浇寰俊寮€鍙戣€呭伐鍏? https://developers.weixin.qq.com/miniprogram/dev/devtools/download.html")
    print("2. 瀹夎鍚庨厤缃瓹LI鐜鍙橀噺")
    print("3. 鎴栬€呮墜鍔ㄥ湪寰俊寮€鍙戣€呭伐鍏蜂腑涓婁紶")
    return False

def upload_with_cli(app_name, app_config):
    """浣跨敤寰俊CLI涓婁紶"""
    build_dir = PROJECT_ROOT / app_config['build_dir']

    if not build_dir.exists():
        print(f"[閿欒] 鏋勫缓鐩綍涓嶅瓨鍦? {build_dir}")
        return False

    print(f"\n[涓婁紶] {app_config['name']} ({app_name})")
    print(f"  鏋勫缓鐩綍: {build_dir}")
    print(f"  鐗堟湰: {app_config['version']}")
    print(f"  鎻忚堪: {app_config['desc']}")

    # 浣跨敤寰俊寮€鍙戣€呭伐鍏稢LI涓婁紶
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
            print(f"[鎴愬姛] {app_config['name']} 涓婁紶鎴愬姛")
            return True
        else:
            print(f"[閿欒] 涓婁紶澶辫触: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print(f"[閿欒] 涓婁紶瓒呮椂")
        return False
    except Exception as e:
        print(f"[閿欒] {e}")
        return False

def generate_upload_guide():
    """鐢熸垚鎵嬪姩涓婁紶鎸囧崡"""
    guide = """
=== 寰俊灏忕▼搴忔墜鍔ㄤ笂浼犳寚鍗?===

鐢变簬寰俊寮€鍙戣€呭伐鍏稢LI闇€瑕佺壒娈婇厤缃紝寤鸿浣跨敤浠ヤ笅鏂瑰紡涓婁紶:

1. 鎵撳紑寰俊寮€鍙戣€呭伐鍏?2. 閫夋嫨"瀵煎叆椤圭洰"
3. 閫夋嫨浠ヤ笅鐩綍涔嬩竴:
   - 瀛﹀憳绔? apps/client/dist/build/mp-weixin
   - 鏁欑粌绔? apps/coach/dist/build/mp-weixin
4. 鐐瑰嚮"涓婁紶"鎸夐挳
5. 濉啓鐗堟湰鍙峰拰鏇存柊璇存槑
6. 鐐瑰嚮"涓婁紶"

涓婁紶鍚庣殑鐗堟湰灏嗘樉绀哄湪寰俊灏忕▼搴忓悗鍙扮殑"娴嬭瘯鐗堟湰"涓€?
=== 鐗堟湰淇℃伅 ===

瀛﹀憳绔?(涔愯埅鎴愰暱):
- 鐗堟湰: 1.0.0
- 鎻忚堪: 鏄撲箰鑸稩TS鏅烘収浣撴暀浜戝钩鍙?- 瀛﹀憳/瀹堕暱绔?- 璺緞: apps/client/dist/build/mp-weixin

鏁欑粌绔?(鏄撲箰鑸暀缁冪):
- 鐗堟湰: 1.0.0
- 鎻忚堪: 鏄撲箰鑸稩TS鏅烘収浣撴暀浜戝钩鍙?- 鏁欑粌绔?- 璺緞: apps/coach/dist/build/mp-weixin

=== 娴嬭瘯姝ラ ===

1. 鍦ㄥ井淇″皬绋嬪簭鍚庡彴璁剧疆娴嬭瘯璐﹀彿
2. 浣跨敤娴嬭瘯璐﹀彿鎵弿浜岀淮鐮佽繘鍏ユ祴璇曠増鏈?3. 娴嬭瘯浠ヤ笅鍔熻兘:
   - 鐧诲綍/娉ㄥ唽
   - 棰勭害璇剧▼
   - 鏌ョ湅璇炬椂鍗?   - 娑堣垂璁板綍
   - 鏁欑粌璇勪环

=== 鍙戝竷姝ラ ===

1. 鍦ㄥ井淇″皬绋嬪簭鍚庡彴鎻愪氦瀹℃牳
2. 绛夊緟瀹℃牳閫氳繃 (閫氬父1-3澶?
3. 瀹℃牳閫氳繃鍚庣偣鍑?鍙戝竷"
4. 灏忕▼搴忓皢鍦ㄥ井淇′腑涓婄嚎
"""
    return guide

def main():
    print("=" * 50)
    print("寰俊灏忕▼搴忎笂浼犲伐鍏?)
    print("=" * 50)

    # 妫€鏌ユ瀯寤烘枃浠?    print("\n[妫€鏌 楠岃瘉鏋勫缓鏂囦欢...")
    all_built = True
    for app_name, app_config in APPS.items():
        build_dir = PROJECT_ROOT / app_config['build_dir']
        if build_dir.exists():
            print(f"  [OK] {app_config['name']}: {build_dir}")
        else:
            print(f"  [FAIL] {app_config['name']}: 鏈壘鍒?)
            all_built = False

    if not all_built:
        print("\n[閿欒] 閮ㄥ垎灏忕▼搴忔湭鏋勫缓锛岃鍏堣繍琛?")
        print("  cd apps/client && pnpm build:mp-weixin")
        print("  cd apps/coach && pnpm build:mp-weixin")
        sys.exit(1)

    # 妫€鏌ュ井淇″伐鍏?    print("\n[妫€鏌 寰俊寮€鍙戣€呭伐鍏?..")
    has_cli = check_wechat_cli()

    if has_cli:
        # 灏濊瘯浣跨敤CLI涓婁紶
        print("\n[涓婁紶] 寮€濮嬩笂浼?..")
        success_count = 0
        for app_name, app_config in APPS.items():
            if upload_with_cli(app_name, app_config):
                success_count += 1

        print(f"\n[瀹屾垚] 鎴愬姛涓婁紶 {success_count}/{len(APPS)} 涓皬绋嬪簭")
    else:
        # 鐢熸垚鎵嬪姩涓婁紶鎸囧崡
        print("\n" + generate_upload_guide())

    # 鐢熸垚涓婁紶淇℃伅鏂囦欢
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

    print(f"\n[淇℃伅] 涓婁紶淇℃伅宸蹭繚瀛樺埌: {info_file}")

if __name__ == "__main__":
    main()
