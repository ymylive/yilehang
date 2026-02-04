"""
用户相关Schema
"""
from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator
import re


class UserBase(BaseModel):
    """用户基础Schema"""
    phone: Optional[str] = None
    nickname: Optional[str] = None
    avatar: Optional[str] = None


class UserCreate(BaseModel):
    """用户注册Schema"""
    phone: str = Field(..., description="手机号")
    password: str = Field(..., min_length=6, max_length=20, description="密码")
    role: str = Field(default="parent", description="角色: parent/student/coach")
    nickname: Optional[str] = Field(None, max_length=50, description="昵称")

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v):
        if not re.match(r'^1[3-9]\d{9}$', v):
            raise ValueError('手机号格式不正确')
        return v

    @field_validator('role')
    @classmethod
    def validate_role(cls, v):
        if v not in ['parent', 'student', 'coach', 'admin']:
            raise ValueError('角色类型不正确')
        return v


class UserLogin(BaseModel):
    """手机号密码登录Schema"""
    phone: str = Field(..., description="手机号")
    password: str = Field(..., description="密码")


class WechatLogin(BaseModel):
    """微信登录Schema"""
    code: str = Field(..., description="微信登录code")
    user_info: Optional[dict] = Field(None, description="微信用户信息")


class WechatPhoneLogin(BaseModel):
    """微信手机号登录Schema"""
    code: str = Field(..., description="微信登录code")
    phone_code: str = Field(..., description="获取手机号的code")


class SmsCodeRequest(BaseModel):
    """发送短信验证码请求"""
    phone: str = Field(..., description="手机号")

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v):
        if not re.match(r'^1[3-9]\d{9}$', v):
            raise ValueError('手机号格式不正确')
        return v


class SmsCodeLogin(BaseModel):
    """短信验证码登录Schema"""
    phone: str = Field(..., description="手机号")
    code: str = Field(..., min_length=4, max_length=6, description="验证码")


class PasswordReset(BaseModel):
    """重置密码Schema"""
    phone: str = Field(..., description="手机号")
    code: str = Field(..., description="验证码")
    new_password: str = Field(..., min_length=6, max_length=20, description="新密码")


class PasswordChange(BaseModel):
    """修改密码Schema"""
    old_password: str = Field(..., description="旧密码")
    new_password: str = Field(..., min_length=6, max_length=20, description="新密码")


class UserUpdate(BaseModel):
    """用户信息更新Schema"""
    nickname: Optional[str] = Field(None, max_length=50)
    avatar: Optional[str] = None


class UserResponse(UserBase):
    """用户响应Schema"""
    id: int
    role: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class UserDetailResponse(UserResponse):
    """用户详情响应Schema"""
    wechat_bindded: bool = False
    student: Optional["StudentResponse"] = None
    coach: Optional["CoachResponse"] = None


class Token(BaseModel):
    """Token响应"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int = Field(default=86400, description="过期时间(秒)")
    user: UserResponse


class TokenRefresh(BaseModel):
    """Token刷新请求"""
    refresh_token: str


# ============ 学员相关 ============

class StudentBase(BaseModel):
    """学员基础Schema"""
    name: str
    gender: Optional[str] = None
    birth_date: Optional[date] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    school: Optional[str] = None
    grade: Optional[str] = None


class StudentCreate(StudentBase):
    """学员创建Schema"""
    parent_id: Optional[int] = None
    coach_id: Optional[int] = None


class StudentRegister(BaseModel):
    """学员注册Schema (家长为孩子注册)"""
    name: str = Field(..., max_length=50, description="学员姓名")
    gender: Optional[str] = Field(None, description="性别: male/female")
    birth_date: Optional[date] = Field(None, description="出生日期")
    phone: Optional[str] = Field(None, description="学员手机号(可选)")


class StudentUpdate(BaseModel):
    """学员更新Schema"""
    name: Optional[str] = None
    gender: Optional[str] = None
    birth_date: Optional[date] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    school: Optional[str] = None
    grade: Optional[str] = None
    coach_id: Optional[int] = None


class StudentResponse(StudentBase):
    """学员响应Schema"""
    id: int
    student_no: str
    remaining_lessons: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class StudentDetailResponse(StudentResponse):
    """学员详情响应"""
    coach_name: Optional[str] = None
    parent_name: Optional[str] = None
    total_lessons: int = 0
    attendance_rate: float = 0.0


# ============ 教练相关 ============

class CoachBase(BaseModel):
    """教练基础Schema"""
    name: str
    certification: Optional[str] = None
    specialty: Optional[str] = None
    hourly_rate: Optional[float] = None


class CoachCreate(CoachBase):
    """教练创建Schema"""
    user_id: int


class CoachRegister(BaseModel):
    """教练注册Schema"""
    phone: str = Field(..., description="手机号")
    password: str = Field(..., min_length=6, description="密码")
    name: str = Field(..., max_length=50, description="姓名")
    specialty: Optional[List[str]] = Field(None, description="专长")
    introduction: Optional[str] = Field(None, description="个人介绍")


class CoachResponse(CoachBase):
    """教练响应Schema"""
    id: int
    coach_no: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class CoachProfileResponse(CoachResponse):
    """教练个人资料响应"""
    avatar: Optional[str] = None
    introduction: Optional[str] = None
    years_of_experience: Optional[int] = None
    total_students: int = 0
    total_lessons: int = 0
    avg_rating: float = 0.0
