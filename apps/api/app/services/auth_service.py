"""Authentication services."""
import asyncio
import random
import string
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from typing import Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.core.security import get_password_hash, verify_password, create_access_token
from app.models import User, Student, Coach
from app.models.merchant import Merchant, MerchantUser

logger = logging.getLogger(__name__)

# 微信错误码映射
WECHAT_ERROR_MESSAGES = {
    -1: "微信服务繁忙，请稍后重试",
    40029: "登录凭证已过期，请重试",
    45011: "请求过于频繁，请稍后重试",
    40226: "登录受限，请联系客服",
    40013: "AppID无效",
    40125: "AppSecret无效",
}


class VerificationCodeStore:
    """In-memory verification code store (replace with Redis in production)."""

    def __init__(self) -> None:
        self._codes: dict[str, dict] = {}

    def set_code(self, key: str, code: str, ttl_minutes: int = 5) -> None:
        self._codes[key] = {
            "code": code,
            "expires_at": datetime.utcnow() + timedelta(minutes=ttl_minutes),
        }

    def verify_code(self, key: str, code: str) -> bool:
        stored = self._codes.get(key)
        if not stored:
            return False

        if datetime.utcnow() > stored["expires_at"]:
            del self._codes[key]
            return False

        if stored["code"] != code:
            return False

        del self._codes[key]
        return True

    def get_code(self, key: str) -> Optional[str]:
        """Get stored code (for dev/testing only)."""
        stored = self._codes.get(key)
        if not stored:
            return None
        if datetime.utcnow() > stored["expires_at"]:
            del self._codes[key]
            return None
        return stored["code"]


EMAIL_CODE_STORE = VerificationCodeStore()


class AuthService:
    """Authentication service."""

    @staticmethod
    def generate_student_no() -> str:
        """Generate student number."""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        random_str = ''.join(random.choices(string.digits, k=4))
        return f"S{timestamp}{random_str}"

    @staticmethod
    def generate_coach_no() -> str:
        """Generate coach number."""
        timestamp = datetime.now().strftime('%Y%m%d')
        random_str = ''.join(random.choices(string.digits, k=4))
        return f"C{timestamp}{random_str}"

    @staticmethod
    def generate_verification_code() -> str:
        """Generate 6-digit verification code."""
        return ''.join(random.choices(string.digits, k=6))

    @staticmethod
    async def get_user_by_phone(db: AsyncSession, phone: str) -> Optional[User]:
        """Get user by phone number."""
        result = await db.execute(select(User).where(User.phone == phone))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
        """Get user by email address."""
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_by_nickname(db: AsyncSession, nickname: str) -> Optional[User]:
        """Get user by nickname (username)."""
        nickname = (nickname or "").strip()
        if not nickname:
            return None
        result = await db.execute(select(User).where(User.nickname == nickname))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_by_openid(db: AsyncSession, openid: str) -> Optional[User]:
        """Get user by WeChat openid."""
        result = await db.execute(select(User).where(User.wechat_openid == openid))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
        """Get user by id."""
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def create_user(
        db: AsyncSession,
        password: str,
        role: str = "parent",
        nickname: Optional[str] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        openid: Optional[str] = None
    ) -> User:
        """Create user."""
        if nickname:
            default_name = nickname
        elif email:
            default_name = email.split("@")[0]
        elif phone:
            default_name = f"User{phone[-4:]}"
        else:
            default_name = "NewUser"

        user = User(
            email=email if email else None,
            phone=phone if phone else None,
            password_hash=get_password_hash(password) if password else None,
            role=role,
            nickname=nickname or default_name,
            wechat_openid=openid,
            status="active"
        )
        db.add(user)
        await db.flush()
        await db.refresh(user)
        return user

    @staticmethod
    async def create_student_profile(
        db: AsyncSession,
        user_id: int,
        name: str,
        gender: Optional[str] = None,
        birth_date=None,
        parent_id: Optional[int] = None
    ) -> Student:
        """Create student profile."""
        student = Student(
            user_id=user_id,
            student_no=AuthService.generate_student_no(),
            name=name,
            gender=gender,
            birth_date=birth_date,
            parent_id=parent_id,
            status="active"
        )
        db.add(student)
        await db.flush()
        await db.refresh(student)
        return student

    @staticmethod
    async def create_coach_profile(
        db: AsyncSession,
        user_id: int,
        name: str,
        specialty: Optional[str] = None,
        introduction: Optional[str] = None
    ) -> Coach:
        """Create coach profile."""
        coach = Coach(
            user_id=user_id,
            coach_no=AuthService.generate_coach_no(),
            name=name,
            specialty=specialty,
            introduction=introduction,
            status="active"
        )
        db.add(coach)
        await db.flush()
        await db.refresh(coach)
        return coach

    @staticmethod
    async def create_merchant_profile(
        db: AsyncSession,
        user_id: int,
        name: str
    ) -> Merchant:
        """Create merchant profile and link user."""
        from app.models.merchant import MerchantStatus
        merchant = Merchant(
            name=name,
            category="其他",
            status=MerchantStatus.PENDING,
            is_featured=False
        )
        db.add(merchant)
        await db.flush()

        merchant_user = MerchantUser(
            merchant_id=merchant.id,
            user_id=user_id,
            role="owner",
            is_active=True
        )
        db.add(merchant_user)
        await db.flush()
        await db.refresh(merchant)
        return merchant

    @staticmethod
    def create_token(user: User) -> Tuple[str, int]:
        """Create access token."""
        expires_in = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        access_token = create_access_token(
            data={"sub": str(user.id), "role": user.role},
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        return access_token, expires_in

    @staticmethod
    async def authenticate_user(db: AsyncSession, account: str, password: str) -> Optional[User]:
        """Verify account + password. Account can be phone / email / nickname."""
        account = (account or "").strip()
        if not account:
            return None

        user = None
        if "@" in account:
            user = await AuthService.get_user_by_email(db, account)
        elif account.isdigit() and len(account) >= 6:
            user = await AuthService.get_user_by_phone(db, account)

        if not user:
            user = await AuthService.get_user_by_nickname(db, account)

        if not user:
            return None
        if not user.password_hash:
            return None
        if not verify_password(password, user.password_hash):
            return None
        return user

    @staticmethod
    async def update_password(db: AsyncSession, user: User, new_password: str) -> User:
        """Update password."""
        user.password_hash = get_password_hash(new_password)
        user.updated_at = datetime.utcnow()
        await db.flush()
        return user

    @staticmethod
    async def bind_wechat(db: AsyncSession, user: User, openid: str) -> User:
        """Bind WeChat openid to user."""
        user.wechat_openid = openid
        user.updated_at = datetime.utcnow()
        await db.flush()
        return user


class WechatService:
    """WeChat service."""

    _access_token: Optional[str] = None
    _access_token_expires_at: Optional[datetime] = None
    _access_token_lock = asyncio.Lock()

    @staticmethod
    def _ensure_wechat_config() -> None:
        """Ensure WeChat app credentials are configured."""
        if not settings.WECHAT_APPID:
            raise Exception("WECHAT_APPID is not configured")
        if not settings.WECHAT_SECRET:
            raise Exception("WECHAT_SECRET is not configured")

    @staticmethod
    async def code2session(code: str, device_id: Optional[str] = None) -> dict:
        """Get WeChat session info by code."""
        if not settings.WECHAT_SECRET:
            if not settings.ALLOW_WECHAT_LOGIN_WITHOUT_SECRET:
                WechatService._ensure_wechat_config()
            else:
                if not device_id:
                    raise Exception("WECHAT_SECRET not configured and device_id is missing")
                fallback_openid = f"dev_openid_{device_id}"
                logger.warning("[WeChat][DEV-FALLBACK] using fallback openid: %s", fallback_openid)
                return {"openid": fallback_openid, "session_key": "dev-fallback"}
        else:
            WechatService._ensure_wechat_config()

        if not code:
            raise Exception("WeChat login code is empty")

        import httpx
        url = "https://api.weixin.qq.com/sns/jscode2session"
        params = {
            "appid": settings.WECHAT_APPID,
            "secret": settings.WECHAT_SECRET,
            "js_code": code,
            "grant_type": "authorization_code"
        }

        logger.info(f"[WeChat] Calling code2session API with code: {code[:8]}...")

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, params=params)
                data = response.json()
        except httpx.TimeoutException:
            logger.error("[WeChat] code2session request timeout")
            raise Exception("微信服务请求超时，请稍后重试")
        except httpx.RequestError as e:
            logger.error(f"[WeChat] code2session request error: {e}")
            raise Exception("微信服务请求失败，请检查网络连接")

        if "errcode" in data and data["errcode"] != 0:
            errcode = data["errcode"]
            errmsg = WECHAT_ERROR_MESSAGES.get(errcode, data.get('errmsg', '未知错误'))
            logger.error(f"[WeChat] code2session failed: errcode={errcode}, errmsg={data.get('errmsg')}")
            raise Exception(errmsg)

        logger.info(f"[WeChat] code2session success, openid: {data.get('openid', '')[:8]}...")
        return data

    @staticmethod
    async def get_phone_number(code: str, access_token: str) -> str:
        """Get user phone number via code."""
        if code.startswith("dev_phone:"):
            phone = code.split(":", 1)[1]
            if not phone:
                raise Exception("开发模式手机号为空")
            return phone

        if not code:
            raise Exception("WeChat phone code is empty")
        if not access_token:
            raise Exception("WeChat access token is empty")

        import httpx
        url = f"https://api.weixin.qq.com/wxa/business/getuserphonenumber?access_token={access_token}"

        logger.info("[WeChat] Calling getuserphonenumber API...")

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(url, json={"code": code})
                data = response.json()
        except httpx.TimeoutException:
            logger.error("[WeChat] getuserphonenumber request timeout")
            raise Exception("微信服务请求超时，请稍后重试")
        except httpx.RequestError as e:
            logger.error(f"[WeChat] getuserphonenumber request error: {e}")
            raise Exception("微信服务请求失败，请检查网络连接")

        if data.get("errcode", 0) != 0:
            errcode = data.get("errcode")
            errmsg = WECHAT_ERROR_MESSAGES.get(errcode, data.get('errmsg', '未知错误'))
            logger.error(f"[WeChat] getuserphonenumber failed: errcode={errcode}, errmsg={data.get('errmsg')}")
            raise Exception(f"获取手机号失败: {errmsg}")

        phone_info = data.get("phone_info", {})
        phone = phone_info.get("phoneNumber", "")
        logger.info(f"[WeChat] getuserphonenumber success, phone: {phone[:3]}****{phone[-4:] if len(phone) >= 7 else ''}")
        return phone

    @classmethod
    async def get_access_token(cls) -> str:
        """Get WeChat access token."""
        cls._ensure_wechat_config()

        now = datetime.utcnow()
        if (
            cls._access_token
            and cls._access_token_expires_at
            and now < cls._access_token_expires_at
        ):
            return cls._access_token

        async with cls._access_token_lock:
            now = datetime.utcnow()
            if (
                cls._access_token
                and cls._access_token_expires_at
                and now < cls._access_token_expires_at
            ):
                return cls._access_token

            import httpx
            url = "https://api.weixin.qq.com/cgi-bin/token"
            params = {
                "grant_type": "client_credential",
                "appid": settings.WECHAT_APPID,
                "secret": settings.WECHAT_SECRET
            }

            logger.info("[WeChat] Calling get_access_token API...")

            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    response = await client.get(url, params=params)
                    data = response.json()
            except httpx.TimeoutException:
                logger.error("[WeChat] get_access_token request timeout")
                raise Exception("WeChat service request timeout, please retry")
            except httpx.RequestError as e:
                logger.error(f"[WeChat] get_access_token request error: {e}")
                raise Exception("WeChat service request failed, please check network")

            if "errcode" in data and data["errcode"] != 0:
                errcode = data["errcode"]
                errmsg = WECHAT_ERROR_MESSAGES.get(errcode, data.get('errmsg', 'unknown error'))
                logger.error(f"[WeChat] get_access_token failed: errcode={errcode}, errmsg={data.get('errmsg')}")
                raise Exception(f"Failed to fetch access_token: {errmsg}")

            access_token = data.get("access_token")
            if not access_token:
                raise Exception("Failed to fetch access_token: empty token")

            expires_in = int(data.get("expires_in", 7200))
            safe_ttl = max(expires_in - 120, 60)
            cls._access_token = access_token
            cls._access_token_expires_at = datetime.utcnow() + timedelta(seconds=safe_ttl)

            logger.info("[WeChat] get_access_token success")
            return access_token



class EmailService:
    """Email verification service."""

    @staticmethod
    def _normalize_smtp_password(raw_password: Optional[str]) -> str:
        """Gmail app passwords are often copied with spaces; remove them safely."""
        return (raw_password or "").replace(" ", "").strip()

    @staticmethod
    async def send_code_with_detail(email: str) -> dict:
        """Send verification code with delivery detail for client hints."""
        code = AuthService.generate_verification_code()
        EMAIL_CODE_STORE.set_code(email, code)

        result = {
            "success": True,
            "delivery": "smtp",
            "dev_code": None,
            "message": "Verification code sent"
        }

        if settings.DEV_PRINT_CODE:
            logger.info("[EMAIL][DEV] Verification code for %s: %s", email, code)
            result["delivery"] = "dev"
            result["dev_code"] = code
            result["message"] = "Verification code generated (dev mode)"
            return result

        smtp_user = (settings.SMTP_USER or "").strip()
        smtp_password = EmailService._normalize_smtp_password(settings.SMTP_PASSWORD)

        if not smtp_user or not smtp_password:
            logger.error("[EMAIL] SMTP credentials are missing")
            if settings.DEV_PRINT_CODE_ON_SEND_FAIL:
                logger.warning("[EMAIL][FALLBACK] Verification code for %s: %s", email, code)
                result["delivery"] = "fallback"
                result["dev_code"] = code
                result["message"] = "SMTP unavailable, dev fallback code generated"
                return result
            return {
                "success": False,
                "delivery": "smtp",
                "dev_code": None,
                "message": "Failed to send verification code"
            }

        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = "易乐航 - 邮箱验证码"
            msg["From"] = settings.SMTP_FROM or smtp_user
            msg["To"] = email

            html_body = f"""
            <div style="max-width:480px;margin:0 auto;padding:32px;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;">
                <h2 style="color:#FF8800;margin-bottom:8px;">易乐航</h2>
                <p style="color:#666;font-size:14px;">您的登录验证码如下：</p>
                <div style="background:#FFF7ED;border:1px solid #FFE0B5;border-radius:12px;padding:24px;text-align:center;margin:16px 0;">
                    <span style="font-size:36px;font-weight:700;letter-spacing:8px;color:#FF8800;">{code}</span>
                </div>
                <p style="color:#999;font-size:12px;">验证码 5 分钟内有效，请勿泄露给他人。</p>
            </div>
            """
            msg.attach(MIMEText(html_body, "html", "utf-8"))

            def _send() -> None:
                if settings.SMTP_USE_SSL:
                    server = smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT, timeout=20)
                else:
                    server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=20)
                    server.ehlo()
                    server.starttls()
                    server.ehlo()

                try:
                    server.login(smtp_user, smtp_password)
                    server.sendmail(msg["From"], [email], msg.as_string())
                finally:
                    server.quit()

            await asyncio.to_thread(_send)
            logger.info("[EMAIL] Verification code sent to %s", email)
            return result
        except Exception:
            logger.exception("[EMAIL] Send failed")
            if settings.DEV_PRINT_CODE_ON_SEND_FAIL:
                logger.warning("[EMAIL][FALLBACK] Verification code for %s: %s", email, code)
                result["delivery"] = "fallback"
                result["dev_code"] = code
                result["message"] = "SMTP send failed, dev fallback code generated"
                return result
            return {
                "success": False,
                "delivery": "smtp",
                "dev_code": None,
                "message": "Failed to send verification code"
            }

    @staticmethod
    async def send_code(email: str) -> bool:
        """Send email verification code."""
        result = await EmailService.send_code_with_detail(email)
        return bool(result.get("success"))

    @staticmethod
    async def verify_code(email: str, code: str) -> bool:
        """Verify email code."""
        return EMAIL_CODE_STORE.verify_code(email, code)
