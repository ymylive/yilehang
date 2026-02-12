"""
灏忕▼搴忚繛鎺ユ祴璇曡剼鏈?- 楠岃瘉灏忕▼搴忚兘鍚︽甯歌繛鎺ュ埌鐢熶骇鏈嶅姟鍣?"""
import requests
import json
from datetime import datetime

# 閰嶇疆
API_BASE_URL = "https://rl.cornna.xyz/api/v1"
TEST_ENDPOINTS = {
    "health": "/health",
    "docs": "/docs",
    "openapi": "/openapi.json",
    "auth_login": "/auth/login",
    "bookings": "/bookings",
    "coaches": "/coaches",
    "memberships": "/memberships/cards"
}

def test_connection():
    """娴嬭瘯API杩炴帴"""
    print("=" * 60)
    print("灏忕▼搴廇PI杩炴帴娴嬭瘯")
    print("=" * 60)
    print(f"API鍦板潃: {API_BASE_URL}")
    print(f"娴嬭瘯鏃堕棿: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    results = {}
    success_count = 0
    total_count = len(TEST_ENDPOINTS)

    for name, endpoint in TEST_ENDPOINTS.items():
        url = API_BASE_URL + endpoint
        try:
            response = requests.get(url, timeout=10, verify=False)
            status = response.status_code
            success = 200 <= status < 300

            if success:
                success_count += 1
                status_text = "[OK]"
            else:
                status_text = f"[FAIL {status}]"

            results[name] = {
                "url": url,
                "status": status,
                "success": success
            }

            print(f"{status_text} {name:20} {status}")

        except requests.exceptions.SSLError:
            results[name] = {
                "url": url,
                "error": "SSL璇佷功閿欒",
                "success": False
            }
            print(f"[SSL ERROR] {name:20} SSL璇佷功閿欒")

        except requests.exceptions.ConnectionError:
            results[name] = {
                "url": url,
                "error": "杩炴帴澶辫触",
                "success": False
            }
            print(f"[CONN ERROR] {name:20} 杩炴帴澶辫触")

        except requests.exceptions.Timeout:
            results[name] = {
                "url": url,
                "error": "璇锋眰瓒呮椂",
                "success": False
            }
            print(f"[TIMEOUT] {name:20} 璇锋眰瓒呮椂")

        except Exception as e:
            results[name] = {
                "url": url,
                "error": str(e),
                "success": False
            }
            print(f"[ERROR] {name:20} {str(e)[:30]}")

    print()
    print("=" * 60)
    print(f"Test Results: {success_count}/{total_count} passed")
    print("=" * 60)

    if success_count == total_count:
        print("\n[OK] All endpoints connected successfully, mini-program can connect to server")
        return True
    else:
        print(f"\n[FAIL] {total_count - success_count} endpoints failed")
        print("\nFailed endpoints:")
        for name, result in results.items():
            if not result.get("success"):
                print(f"  - {name}: {result.get('error', 'Unknown error')}")
        return False

def test_login():
    """Test login functionality"""
    print("\n" + "=" * 60)
    print("Login Test")
    print("=" * 60)

    # Test accounts
    test_accounts = [
        {"phone": "13800000001", "password": "parent123", "role": "parent"},
        {"phone": "13800000002", "password": "coach123", "role": "coach"},
        {"phone": "13800000003", "password": "student123", "role": "student"}
    ]

    for account in test_accounts:
        url = f"{API_BASE_URL}/auth/login"
        try:
            response = requests.post(
                url,
                json={"phone": account["phone"], "password": account["password"]},
                timeout=10,
                verify=False
            )

            if response.status_code == 200:
                data = response.json()
                print(f"[OK] {account['role']:10} ({account['phone']}) login success")
                if "access_token" in data:
                    print(f"  Token: {data['access_token'][:20]}...")
            else:
                print(f"[FAIL] {account['role']:10} ({account['phone']}) login failed ({response.status_code})")

        except Exception as e:
            print(f"[ERROR] {account['role']:10} ({account['phone']}) error: {str(e)[:30]}")

def main():
    # 绂佺敤SSL璀﹀憡锛堜粎鐢ㄤ簬娴嬭瘯锛?    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    # 娴嬭瘯杩炴帴
    connection_ok = test_connection()

    # 濡傛灉杩炴帴姝ｅ父锛屾祴璇曠櫥褰?    if connection_ok:
        test_login()

    print("\n" + "=" * 60)
    print("娴嬭瘯瀹屾垚")
    print("=" * 60)

if __name__ == "__main__":
    main()
