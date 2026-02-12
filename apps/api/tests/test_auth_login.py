"""
Tests for authentication login endpoints.

Coverage:
- Account + password login (phone/email/nickname)
- Email verification code send & login
- WeChat login (with and without user_info)
- Error handling (invalid credentials, expired codes, rate limits)
- Edge cases (auto-register on email login, disabled accounts)
"""
from unittest.mock import patch

import pytest
from httpx import AsyncClient

from app.services.auth_service import EMAIL_CODE_STORE

# ============ Account + Password Login ============

class TestAccountLogin:
    """Tests for POST /api/v1/auth/login"""

    @pytest.mark.asyncio
    async def test_login_with_email(self, client: AsyncClient, test_users):
        """Login with email + password succeeds."""
        resp = await client.post(
            "/api/v1/auth/login",
            json={"account": "admin@test.com", "password": "admin123"}
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert data["user"]["email"] == "admin@test.com"
        assert data["user"]["role"] == "admin"

    @pytest.mark.asyncio
    async def test_login_with_phone(self, client: AsyncClient, test_users):
        """Login with phone + password succeeds."""
        resp = await client.post(
            "/api/v1/auth/login",
            json={"account": "13800000000", "password": "admin123"}
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["user"]["phone"] == "13800000000"

    @pytest.mark.asyncio
    async def test_login_with_nickname(self, client: AsyncClient, test_users):
        """Login with nickname + password succeeds."""
        resp = await client.post(
            "/api/v1/auth/login",
            json={"account": "Coach User", "password": "coach123"}
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["user"]["role"] == "coach"

    @pytest.mark.asyncio
    async def test_login_wrong_password(self, client: AsyncClient, test_users):
        """Login with wrong password returns 401."""
        resp = await client.post(
            "/api/v1/auth/login",
            json={"account": "admin@test.com", "password": "wrongpass"}
        )
        assert resp.status_code == 401
        assert "Invalid" in resp.json()["detail"]

    @pytest.mark.asyncio
    async def test_login_nonexistent_account(self, client: AsyncClient, test_users):
        """Login with non-existent account returns 401."""
        resp = await client.post(
            "/api/v1/auth/login",
            json={"account": "nobody@test.com", "password": "pass123"}
        )
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_login_empty_account(self, client: AsyncClient, test_users):
        """Login with empty account returns 401."""
        resp = await client.post(
            "/api/v1/auth/login",
            json={"account": "", "password": "pass123"}
        )
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_login_returns_token_and_user(self, client: AsyncClient, test_users):
        """Login response contains access_token, expires_in, and user object."""
        resp = await client.post(
            "/api/v1/auth/login",
            json={"account": "parent@test.com", "password": "parent123"}
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert "expires_in" in data
        assert "user" in data
        assert data["user"]["id"] is not None


# ============ Email Verification Code ============

class TestEmailCodeSend:
    """Tests for POST /api/v1/auth/login/email/send"""

    @pytest.mark.asyncio
    async def test_send_code_dev_mode(self, client: AsyncClient):
        """Send code in dev mode does not leak verification code."""
        with patch("app.services.auth_service.settings") as mock_settings:
            mock_settings.DEV_PRINT_CODE = True
            mock_settings.SMTP_USER = ""
            mock_settings.SMTP_PASSWORD = ""
            mock_settings.DEV_PRINT_CODE_ON_SEND_FAIL = False

            resp = await client.post(
                "/api/v1/auth/login/email/send",
                json={"email": "test@example.com"}
            )
            assert resp.status_code == 200
            data = resp.json()
            assert data["delivery"] == "dev"
            assert "dev_code" not in data

    @pytest.mark.asyncio
    async def test_send_code_invalid_email(self, client: AsyncClient):
        """Send code with invalid email returns 422."""
        resp = await client.post(
            "/api/v1/auth/login/email/send",
            json={"email": "not-an-email"}
        )
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_send_code_fallback_when_smtp_missing(self, client: AsyncClient):
        """When SMTP credentials are missing, fallback flow does not leak code."""
        with patch("app.services.auth_service.settings") as mock_settings:
            mock_settings.DEV_PRINT_CODE = False
            mock_settings.SMTP_USER = ""
            mock_settings.SMTP_PASSWORD = ""
            mock_settings.DEV_PRINT_CODE_ON_SEND_FAIL = True

            resp = await client.post(
                "/api/v1/auth/login/email/send",
                json={"email": "fallback@example.com"}
            )
            assert resp.status_code == 200
            data = resp.json()
            assert data["delivery"] == "fallback"
            assert "dev_code" not in data


class TestEmailCodeLogin:
    """Tests for POST /api/v1/auth/login/email"""

    @pytest.mark.asyncio
    async def test_email_login_success(self, client: AsyncClient, test_users):
        """Email code login with valid code succeeds."""
        email = "admin@test.com"
        EMAIL_CODE_STORE.set_code(email, "123456")

        resp = await client.post(
            "/api/v1/auth/login/email",
            json={"email": email, "code": "123456"}
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert data["user"]["email"] == email

    @pytest.mark.asyncio
    async def test_email_login_wrong_code(self, client: AsyncClient, test_users):
        """Email code login with wrong code returns 400."""
        email = "admin@test.com"
        EMAIL_CODE_STORE.set_code(email, "123456")

        resp = await client.post(
            "/api/v1/auth/login/email",
            json={"email": email, "code": "999999"}
        )
        assert resp.status_code == 400
        assert "Invalid" in resp.json()["detail"]

    @pytest.mark.asyncio
    async def test_email_login_expired_code(self, client: AsyncClient, test_users):
        """Email code login with expired code returns 400."""
        email = "admin@test.com"
        EMAIL_CODE_STORE.set_code(email, "123456", ttl_minutes=0)

        resp = await client.post(
            "/api/v1/auth/login/email",
            json={"email": email, "code": "123456"}
        )
        assert resp.status_code == 400

    @pytest.mark.asyncio
    async def test_email_login_no_code_stored(self, client: AsyncClient, test_users):
        """Email code login without sending code first returns 400."""
        resp = await client.post(
            "/api/v1/auth/login/email",
            json={"email": "nocode@test.com", "code": "123456"}
        )
        assert resp.status_code == 400

    @pytest.mark.asyncio
    async def test_email_login_auto_register(self, client: AsyncClient, db_session):
        """Email code login for new user requires registration first."""
        new_email = "newuser@example.com"
        EMAIL_CODE_STORE.set_code(new_email, "654321")

        resp = await client.post(
            "/api/v1/auth/login/email",
            json={"email": new_email, "code": "654321"}
        )
        assert resp.status_code == 404
        assert resp.json()["detail"] == "USER_NOT_REGISTERED"

    @pytest.mark.asyncio
    async def test_email_login_code_consumed(self, client: AsyncClient, test_users):
        """Verification code is consumed after successful login (single use)."""
        email = "admin@test.com"
        EMAIL_CODE_STORE.set_code(email, "111111")

        # First login succeeds
        resp1 = await client.post(
            "/api/v1/auth/login/email",
            json={"email": email, "code": "111111"}
        )
        assert resp1.status_code == 200

        # Second login with same code fails
        resp2 = await client.post(
            "/api/v1/auth/login/email",
            json={"email": email, "code": "111111"}
        )
        assert resp2.status_code == 400


# ============ WeChat Login ============

class TestRegisterWithRole:
    """Tests for POST /api/v1/auth/register/with-role"""

    @pytest.mark.asyncio
    async def test_register_with_role_requires_explicit_role(self, client: AsyncClient):
        """Role is mandatory to avoid implicit parent registration bypass."""
        resp = await client.post(
            "/api/v1/auth/register/with-role",
            json={"wechat_openid": "wx_missing_role"},
        )
        assert resp.status_code == 400
        assert resp.json()["detail"] == "Role is required"


class TestWechatLogin:
    """Tests for POST /api/v1/auth/login/wechat"""

    @pytest.mark.asyncio
    async def test_wechat_login_new_user(self, client: AsyncClient, db_session):
        """WeChat login for new openid requires role selection first."""
        with patch("app.services.auth_service.WechatService.code2session") as mock_c2s:
            mock_c2s.return_value = {"openid": "wx_test_openid_001", "session_key": "sk"}

            resp = await client.post(
                "/api/v1/auth/login/wechat",
                json={
                    "code": "mock_wx_code",
                    "device_id": "dev-123"
                }
            )
            assert resp.status_code == 409
            detail = resp.json()["detail"]
            assert detail["code"] == "WECHAT_ROLE_REQUIRED"
            assert detail["wechat_openid"] == "wx_test_openid_001"

    @pytest.mark.asyncio
    async def test_wechat_login_with_user_info(self, client: AsyncClient, db_session):
        """WeChat login with user_info still requires role selection for first login."""
        with patch("app.services.auth_service.WechatService.code2session") as mock_c2s:
            mock_c2s.return_value = {"openid": "wx_test_openid_002", "session_key": "sk"}

            resp = await client.post(
                "/api/v1/auth/login/wechat",
                json={
                    "code": "mock_wx_code",
                    "user_info": {"nickName": "TestUser", "avatarUrl": "https://example.com/avatar.jpg"},
                    "device_id": "dev-123"
                }
            )
            assert resp.status_code == 409
            detail = resp.json()["detail"]
            assert detail["code"] == "WECHAT_ROLE_REQUIRED"
            assert detail["wechat_openid"] == "wx_test_openid_002"
            assert detail["nickname"] == "TestUser"

    @pytest.mark.asyncio
    async def test_wechat_login_without_user_info(self, client: AsyncClient, db_session):
        """WeChat login without user_info requires role selection on first login."""
        with patch("app.services.auth_service.WechatService.code2session") as mock_c2s:
            mock_c2s.return_value = {"openid": "wx_test_openid_003", "session_key": "sk"}

            resp = await client.post(
                "/api/v1/auth/login/wechat",
                json={
                    "code": "mock_wx_code",
                    "device_id": "dev-123"
                }
            )
            assert resp.status_code == 409
            detail = resp.json()["detail"]
            assert detail["code"] == "WECHAT_ROLE_REQUIRED"
            assert detail["wechat_openid"] == "wx_test_openid_003"

    @pytest.mark.asyncio
    async def test_wechat_login_legacy_placeholder_user_requires_role_selection(
        self,
        client: AsyncClient,
        db_session
    ):
        """Legacy placeholder WeChat users must complete role selection."""
        from app.models import User

        legacy_user = User(
            role="parent",
            nickname="微信用户",
            wechat_openid="wx_legacy_placeholder",
            status="active",
        )
        db_session.add(legacy_user)
        await db_session.commit()

        with patch("app.services.auth_service.WechatService.code2session") as mock_c2s:
            mock_c2s.return_value = {"openid": "wx_legacy_placeholder", "session_key": "sk"}

            resp = await client.post(
                "/api/v1/auth/login/wechat",
                json={"code": "legacy_code", "device_id": "dev-legacy"},
            )
            assert resp.status_code == 409
            detail = resp.json()["detail"]
            assert detail["code"] == "WECHAT_ROLE_REQUIRED"
            assert detail["wechat_openid"] == "wx_legacy_placeholder"

    @pytest.mark.asyncio
    async def test_wechat_login_existing_user(self, client: AsyncClient, db_session):
        """WeChat login with existing openid returns same user."""
        with patch("app.services.auth_service.WechatService.code2session") as mock_c2s:
            mock_c2s.return_value = {"openid": "wx_returning_user", "session_key": "sk"}

            register_resp = await client.post(
                "/api/v1/auth/register/with-role",
                json={
                    "wechat_openid": "wx_returning_user",
                    "role": "parent",
                    "nickname": "ReturningUser"
                }
            )
            assert register_resp.status_code == 200
            registered_user_id = register_resp.json()["user"]["id"]

            # First login - returns registered user
            resp1 = await client.post(
                "/api/v1/auth/login/wechat",
                json={"code": "code1", "device_id": "dev-1"}
            )
            assert resp1.status_code == 200
            user_id_1 = resp1.json()["user"]["id"]
            assert user_id_1 == registered_user_id

            # Second login - returns same user
            resp2 = await client.post(
                "/api/v1/auth/login/wechat",
                json={"code": "code2", "device_id": "dev-1"}
            )
            assert resp2.status_code == 200
            user_id_2 = resp2.json()["user"]["id"]

            assert user_id_1 == user_id_2

    @pytest.mark.asyncio
    async def test_wechat_login_code2session_failure(self, client: AsyncClient):
        """WeChat login fails gracefully when code2session fails."""
        with patch("app.services.auth_service.WechatService.code2session") as mock_c2s:
            mock_c2s.side_effect = Exception("登录凭证已过期，请重试")

            resp = await client.post(
                "/api/v1/auth/login/wechat",
                json={"code": "expired_code", "device_id": "dev-1"}
            )
            assert resp.status_code == 400
            assert "登录凭证已过期" in resp.json()["detail"]

    @pytest.mark.asyncio
    async def test_wechat_login_no_openid(self, client: AsyncClient):
        """WeChat login fails when code2session returns no openid."""
        with patch("app.services.auth_service.WechatService.code2session") as mock_c2s:
            mock_c2s.return_value = {"session_key": "sk"}  # no openid

            resp = await client.post(
                "/api/v1/auth/login/wechat",
                json={"code": "bad_code", "device_id": "dev-1"}
            )
            assert resp.status_code == 400
            assert "WeChat" in resp.json()["detail"]


# ============ Disabled Account ============

class TestDisabledAccount:
    """Tests for login with disabled accounts."""

    @pytest.mark.asyncio
    async def test_login_disabled_account(self, client: AsyncClient, db_session):
        """Login to disabled account returns 403."""
        from app.core.security import get_password_hash
        from app.models import User

        disabled_user = User(
            email="disabled@test.com",
            password_hash=get_password_hash("pass123"),
            role="parent",
            nickname="Disabled",
            status="disabled"
        )
        db_session.add(disabled_user)
        await db_session.commit()

        resp = await client.post(
            "/api/v1/auth/login",
            json={"account": "disabled@test.com", "password": "pass123"}
        )
        assert resp.status_code == 403
        assert "disabled" in resp.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_email_login_disabled_account(self, client: AsyncClient, db_session):
        """Email code login to disabled account returns 403."""
        from app.core.security import get_password_hash
        from app.models import User

        disabled_user = User(
            email="disabled2@test.com",
            password_hash=get_password_hash("pass123"),
            role="parent",
            nickname="Disabled2",
            status="disabled"
        )
        db_session.add(disabled_user)
        await db_session.commit()

        EMAIL_CODE_STORE.set_code("disabled2@test.com", "123456")

        resp = await client.post(
            "/api/v1/auth/login/email",
            json={"email": "disabled2@test.com", "code": "123456"}
        )
        assert resp.status_code == 403


# ============ VerificationCodeStore Unit Tests ============

class TestVerificationCodeStore:
    """Unit tests for in-memory verification code store."""

    def test_set_and_verify(self):
        """Set code then verify succeeds."""
        store = EMAIL_CODE_STORE
        store.set_code("unit@test.com", "999999")
        assert store.verify_code("unit@test.com", "999999") is True

    def test_verify_wrong_code(self):
        """Verify with wrong code fails."""
        store = EMAIL_CODE_STORE
        store.set_code("unit2@test.com", "111111")
        assert store.verify_code("unit2@test.com", "000000") is False

    def test_code_consumed_after_verify(self):
        """Code is deleted after successful verification."""
        store = EMAIL_CODE_STORE
        store.set_code("unit3@test.com", "222222")
        assert store.verify_code("unit3@test.com", "222222") is True
        assert store.verify_code("unit3@test.com", "222222") is False

    def test_expired_code(self):
        """Expired code fails verification."""
        store = EMAIL_CODE_STORE
        store.set_code("unit4@test.com", "333333", ttl_minutes=0)
        assert store.verify_code("unit4@test.com", "333333") is False

    def test_get_code_dev(self):
        """get_code returns stored code for dev use."""
        store = EMAIL_CODE_STORE
        store.set_code("unit5@test.com", "444444")
        assert store.get_code("unit5@test.com") == "444444"

    def test_get_code_nonexistent(self):
        """get_code returns None for non-existent key."""
        store = EMAIL_CODE_STORE
        assert store.get_code("nonexistent@test.com") is None

    def test_rate_limit(self):
        """Rate limit blocks after max attempts."""
        store = EMAIL_CODE_STORE
        key = "rate_test_login"
        # Clear any existing rate limit data
        store._rate_limit.pop(key, None)

        for _ in range(3):
            allowed, _ = store.check_rate_limit(key, max_attempts=3, window_minutes=5)
            assert allowed is True

        allowed, seconds = store.check_rate_limit(key, max_attempts=3, window_minutes=5)
        assert allowed is False
        assert seconds is not None
        assert seconds >= 0
