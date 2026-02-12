"""
User-related schemas.
"""
import re
from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class UserBase(BaseModel):
    """Base user schema."""
    phone: Optional[str] = None
    email: Optional[str] = None
    nickname: Optional[str] = None
    avatar: Optional[str] = None


class UserCreate(BaseModel):
    """User registration schema (email + code + password)."""
    email: str = Field(..., description="Email address")
    password: str = Field(..., min_length=6, max_length=20, description="Password")
    role: str = Field(default="parent", description="Role: parent/student/coach")
    nickname: Optional[str] = Field(None, max_length=50, description="Nickname")
    phone: Optional[str] = Field(None, description="Phone number (optional profile field)")

    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', v):
            raise ValueError('Invalid email format')
        return v

    @field_validator('role')
    @classmethod
    def validate_role(cls, v):
        if v not in ['parent', 'student', 'coach', 'merchant', 'admin']:
            raise ValueError('Invalid role')
        return v


class UserLogin(BaseModel):
    """Account + password login schema."""
    account: Optional[str] = Field(None, description="Phone or email")
    phone: Optional[str] = Field(None, description="Phone number (compatibility)")
    email: Optional[str] = Field(None, description="Email (compatibility)")
    password: str = Field(..., description="Password")


class WechatLogin(BaseModel):
    """WeChat login schema."""
    code: str = Field(..., description="WeChat login code")
    user_info: Optional[dict] = Field(None, description="WeChat user info")
    device_id: Optional[str] = Field(None, description="Stable device id for dev fallback")


class WechatPhoneLogin(BaseModel):
    """WeChat phone quick login schema."""
    code: str = Field(..., description="WeChat login code")
    phone_code: str = Field(..., description="Phone number code")
    device_id: Optional[str] = Field(None, description="Stable device id for dev fallback")


class EmailCodeRequest(BaseModel):
    """Send email verification code request."""
    email: str = Field(..., description="Email address")

    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', v):
            raise ValueError('Invalid email format')
        return v


class EmailCodeLogin(BaseModel):
    """Email code login schema."""
    email: str = Field(..., description="Email address")
    code: str = Field(..., min_length=4, max_length=6, description="Verification code")


class EmailRegister(BaseModel):
    """Email code registration schema."""
    email: str = Field(..., description="Email address")
    code: str = Field(..., min_length=4, max_length=6, description="Verification code")
    password: str = Field(..., min_length=6, max_length=20, description="Password")
    role: str = Field(default="parent", description="Role: parent/student/coach")
    nickname: Optional[str] = Field(None, max_length=50, description="Nickname")
    phone: Optional[str] = Field(None, description="Phone number (optional)")

    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', v):
            raise ValueError('Invalid email format')
        return v

    @field_validator('role')
    @classmethod
    def validate_role(cls, v):
        if v not in ['parent', 'student', 'coach', 'merchant', 'admin']:
            raise ValueError('Invalid role')
        return v


class PasswordReset(BaseModel):
    """Reset password schema (via email code)."""
    email: str = Field(..., description="Email address")
    code: str = Field(..., description="Verification code")
    new_password: str = Field(..., min_length=6, max_length=20, description="New password")


class PasswordChange(BaseModel):
    """Change password schema."""
    old_password: str = Field(..., description="Old password")
    new_password: str = Field(..., min_length=6, max_length=20, description="New password")


class UserUpdate(BaseModel):
    """Update user schema."""
    nickname: Optional[str] = Field(None, max_length=50)
    avatar: Optional[str] = None
    phone: Optional[str] = Field(None, description="Phone number")


class UserResponse(UserBase):
    """User response schema."""
    id: int
    role: str
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserDetailResponse(UserResponse):
    """User detail response."""
    wechat_bindded: bool = False
    student: Optional["StudentResponse"] = None
    coach: Optional["CoachResponse"] = None


class Token(BaseModel):
    """Token response."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int = Field(default=86400, description="Expires in seconds")
    user: UserResponse


class TokenRefresh(BaseModel):
    """Token refresh request."""
    refresh_token: str


# ============ Student-related ============

class StudentBase(BaseModel):
    """Student base schema."""
    name: str
    gender: Optional[str] = None
    birth_date: Optional[date] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    school: Optional[str] = None
    grade: Optional[str] = None


class StudentCreate(StudentBase):
    """Student create schema."""
    parent_id: Optional[int] = None
    coach_id: Optional[int] = None


class StudentRegister(BaseModel):
    """Student registration schema (parent registers child)."""
    name: str = Field(..., max_length=50, description="Student name")
    gender: Optional[str] = Field(None, description="Gender: male/female")
    birth_date: Optional[date] = Field(None, description="Birth date")
    phone: Optional[str] = Field(None, description="Student phone (optional)")


class StudentUpdate(BaseModel):
    """Student update schema."""
    name: Optional[str] = None
    gender: Optional[str] = None
    birth_date: Optional[date] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    school: Optional[str] = None
    grade: Optional[str] = None
    coach_id: Optional[int] = None


class StudentResponse(StudentBase):
    """Student response schema."""
    id: int
    student_no: str
    remaining_lessons: int
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class StudentDetailResponse(StudentResponse):
    """Student detail response."""
    coach_name: Optional[str] = None
    parent_name: Optional[str] = None
    total_lessons: int = 0
    attendance_rate: float = 0.0


# ============ Coach-related ============

class CoachBase(BaseModel):
    """Coach base schema."""
    name: str
    certification: Optional[str] = None
    specialty: Optional[str] = None
    hourly_rate: Optional[float] = None


class CoachCreate(CoachBase):
    """Coach create schema."""
    user_id: int


class CoachRegister(BaseModel):
    """Coach registration schema."""
    email: str = Field(..., description="Email address")
    password: str = Field(..., min_length=6, description="Password")
    name: str = Field(..., max_length=50, description="Name")
    phone: Optional[str] = Field(None, description="Phone number (optional)")
    specialty: Optional[List[str]] = Field(None, description="Specialties")
    introduction: Optional[str] = Field(None, description="Introduction")


class CoachResponse(CoachBase):
    """Coach response schema."""
    id: int
    coach_no: str
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CoachProfileResponse(CoachResponse):
    """Coach profile response."""
    avatar: Optional[str] = None
    introduction: Optional[str] = None
    years_of_experience: Optional[int] = None
    total_students: int = 0
    total_lessons: int = 0
    avg_rating: float = 0.0
