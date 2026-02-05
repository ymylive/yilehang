"""Authentication services."""
import random
import string
import json
import httpx
from datetime import datetime, timedelta
from typing import Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.core.security import get_password_hash, verify_password, create_access_token
from app.models import User, Student, Coach

try:
    from alibabacloud_dysmsapi20170525.client import Client as DysmsapiClient
    from alibabacloud_tea_openapi import models as open_api_models
    ALIYUN_SMS_AVAILABLE = True
except ImportError:
    ALIYUN_SMS_AVAILABLE = False


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


SMS_CODE_STORE = VerificationCodeStore()


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
    def generate_sms_code() -> str:
        """Generate SMS verification code."""
        return ''.join(random.choices(string.digits, k=6))

    @staticmethod
    async def get_user_by_phone(db: AsyncSession, phone: str) -> Optional[User]:
        """Get user by phone number."""
        result = await db.execute(select(User).where(User.phone == phone))
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
        phone: str,
        password: str,
        role: str = "parent",
        nickname: Optional[str] = None,
        openid: Optional[str] = None
    ) -> User:
        """Create user."""
        default_name = f"User{phone[-4:]}" if phone else "NewUser"
        user = User(
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
    def create_token(user: User) -> Tuple[str, int]:
        """Create access token."""
        expires_in = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        access_token = create_access_token(
            data={"sub": str(user.id), "role": user.role},
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        return access_token, expires_in

    @staticmethod
    async def authenticate_user(db: AsyncSession, phone: str, password: str) -> Optional[User]:
        """Verify phone + password."""
        user = await AuthService.get_user_by_phone(db, phone)
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

    @staticmethod
    async def code2session(code: str) -> dict:
        """Get WeChat session info by code."""
        url = "https://api.weixin.qq.com/sns/jscode2session"
        params = {
            "appid": settings.WECHAT_APPID,
            "secret": settings.WECHAT_SECRET,
            "js_code": code,
            "grant_type": "authorization_code"
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            data = response.json()

        if "errcode" in data and data["errcode"] != 0:
            raise Exception(f"WeChat login failed: {data.get('errmsg', 'Unknown error')}")

        return data

    @staticmethod
    async def get_phone_number(code: str, access_token: str) -> str:
        """Get user phone number via code."""
        url = f"https://api.weixin.qq.com/wxa/business/getuserphonenumber?access_token={access_token}"

        async with httpx.AsyncClient() as client:
            response = await client.post(url, json={"code": code})
            data = response.json()

        if data.get("errcode", 0) != 0:
            raise Exception(f"Get phone failed: {data.get('errmsg', 'Unknown error')}")

        phone_info = data.get("phone_info", {})
        return phone_info.get("phoneNumber", "")

    @staticmethod
    async def get_access_token() -> str:
        """Get WeChat access token."""
        url = "https://api.weixin.qq.com/cgi-bin/token"
        params = {
            "grant_type": "client_credential",
            "appid": settings.WECHAT_APPID,
            "secret": settings.WECHAT_SECRET
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            data = response.json()

        if "errcode" in data and data["errcode"] != 0:
            raise Exception(f"Get access_token failed: {data.get('errmsg', 'Unknown error')}")

        return data["access_token"]


class SmsService:
    """SMS service."""

    @staticmethod
    async def send_code(phone: str) -> bool:
        """Send SMS verification code."""
        code = AuthService.generate_sms_code()
        SMS_CODE_STORE.set_code(phone, code)

        # Aliyun SMS integration
        if ALIYUN_SMS_AVAILABLE and settings.ALIYUN_ACCESS_KEY_ID:
            try:
                config = open_api_models.Config(
                    access_key_id=settings.ALIYUN_ACCESS_KEY_ID,
                    access_key_secret=settings.ALIYUN_ACCESS_KEY_SECRET,
                    endpoint="dysmsapi.aliyuncs.com"
                )
                client = DysmsapiClient(config)

                from alibabacloud_dysmsapi20170525 import models as dysmsapi_models
                request = dysmsapi_models.SendSmsRequest(
                    phone_numbers=phone,
                    sign_name=settings.ALIYUN_SMS_SIGN_NAME,
                    template_code=settings.ALIYUN_SMS_TEMPLATE_CODE,
                    template_param=json.dumps({"code": code})
                )

                await client.send_sms_async(request)
                return True
            except Exception as e:
                print(f"[SMS] Aliyun send failed: {str(e)}")
                return False
        else:
            # Dev fallback: print code
            print(f"[SMS] Code sent to {phone}: {code}")
            return True

    @staticmethod
    async def verify_code(phone: str, code: str) -> bool:
        """Verify SMS code."""
        return SMS_CODE_STORE.verify_code(phone, code)
