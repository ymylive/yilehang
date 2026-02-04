"""
用户相关Schema
"""
from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, Field


class UserBase(BaseModel):
    """用户基础Schema"""
    phone: Optional[str] = None
    nickname: Optional[str] = None
    avatar: Optional[str] = None


class UserCreate(BaseModel):
    """用户创建Schema"""
    phone: str
    password: str
    role: str = "parent"


class UserLogin(BaseModel):
    """用户登录Schema"""
    phone: str
    password: str


class WechatLogin(BaseModel):
    """微信登录Schema"""
    code: str


class UserResponse(UserBase):
    """用户响应Schema"""
    id: int
    role: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    """Token响应"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


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


class CoachBase(BaseModel):
    """教练基础Schema"""
    name: str
    certification: Optional[str] = None
    specialty: Optional[str] = None
    hourly_rate: Optional[float] = None


class CoachCreate(CoachBase):
    """教练创建Schema"""
    user_id: int


class CoachResponse(CoachBase):
    """教练响应Schema"""
    id: int
    coach_no: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
