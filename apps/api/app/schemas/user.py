"""
User-related schemas.
"""
from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator
import re


class UserBase(BaseModel):
    """Base user schema."""
    phone: Optional[str] = None
    nickname: Optional[str] = None
    avatar: Optional[str] = None


class UserCreate(BaseModel):
    """User registration schema."""
    phone: str = Field(..., description="Phone number")
    password: str = Field(..., min_length=6, max_length=20, description="Password")
    role: str = Field(default="parent", description="Role: parent/student/coach")
    nickname: Optional[str] = Field(None, max_length=50, description="Nickname")

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v):
        if not re.match(r'^1[3-9]\d{9}$', v):
            raise ValueError('Invalid phone format')
        return v

    @field_validator('role')
    @classmethod
    def validate_role(cls, v):
        if v not in ['parent', 'student', 'coach', 'admin']:
            raise ValueError('Invalid role')
        return v


class UserLogin(BaseModel):
    """Phone + password login schema."""
    phone: str = Field(..., description="Phone number")
    password: str = Field(..., description="Password")


class WechatLogin(BaseModel):
    """WeChat login schema."""
    code: str = Field(..., description="WeChat login code")
    user_info: Optional[dict] = Field(None, description="WeChat user info")


class WechatPhoneLogin(BaseModel):
    """WeChat phone quick login schema."""
    code: str = Field(..., description="WeChat login code")
    phone_code: str = Field(..., description="Phone number code")


class SmsCodeRequest(BaseModel):
    """Send SMS verification code request."""
    phone: str = Field(..., description="Phone number")

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v):
        if not re.match(r'^1[3-9]\d{9}$', v):
            raise ValueError('Invalid phone format')
        return v


class SmsCodeLogin(BaseModel):
    """SMS code login schema."""
    phone: str = Field(..., description="Phone number")
    code: str = Field(..., min_length=4, max_length=6, description="Verification code")


class SmsRegister(BaseModel):
    """SMS code registration schema."""
    phone: str = Field(..., description="Phone number")
    code: str = Field(..., min_length=4, max_length=6, description="Verification code")
    password: str = Field(..., min_length=6, max_length=20, description="Password")
    role: str = Field(default="parent", description="Role: parent/student/coach")
    nickname: Optional[str] = Field(None, max_length=50, description="Nickname")

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v):
        if not re.match(r'^1[3-9]\d{9}$', v):
            raise ValueError('Invalid phone format')
        return v

    @field_validator('role')
    @classmethod
    def validate_role(cls, v):
        if v not in ['parent', 'student', 'coach', 'admin']:
            raise ValueError('Invalid role')
        return v


class PasswordReset(BaseModel):
    """Reset password schema."""
    phone: str = Field(..., description="Phone number")
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


class UserResponse(UserBase):
    """User response schema."""
    id: int
    role: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


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

    class Config:
        from_attributes = True


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
    phone: str = Field(..., description="Phone number")
    password: str = Field(..., min_length=6, description="Password")
    name: str = Field(..., max_length=50, description="Name")
    specialty: Optional[List[str]] = Field(None, description="Specialties")
    introduction: Optional[str] = Field(None, description="Introduction")


class CoachResponse(CoachBase):
    """Coach response schema."""
    id: int
    coach_no: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class CoachProfileResponse(CoachResponse):
    """Coach profile response."""
    avatar: Optional[str] = None
    introduction: Optional[str] = None
    years_of_experience: Optional[int] = None
    total_students: int = 0
    total_lessons: int = 0
    avg_rating: float = 0.0
