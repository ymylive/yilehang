"""
用户相关数据模型
"""
from datetime import datetime, date
from typing import Optional, List
from enum import Enum

from sqlalchemy import String, Integer, Boolean, DateTime, Date, Text, ForeignKey, ARRAY, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class UserRole(str, Enum):
    """用户角色"""
    ADMIN = "admin"
    COACH = "coach"
    PARENT = "parent"
    STUDENT = "student"


class UserStatus(str, Enum):
    """用户状态"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    BANNED = "banned"


class User(Base):
    """用户表"""
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    phone: Mapped[Optional[str]] = mapped_column(String(20), unique=True, index=True)
    password_hash: Mapped[Optional[str]] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(20), default=UserRole.PARENT.value)
    wechat_openid: Mapped[Optional[str]] = mapped_column(String(100), unique=True, index=True)
    avatar: Mapped[Optional[str]] = mapped_column(String(500))
    nickname: Mapped[Optional[str]] = mapped_column(String(50))
    status: Mapped[str] = mapped_column(String(20), default=UserStatus.ACTIVE.value)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    student: Mapped[Optional["Student"]] = relationship("Student", back_populates="user", uselist=False)
    coach: Mapped[Optional["Coach"]] = relationship("Coach", back_populates="user", uselist=False)


class Student(Base):
    """学员表"""
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"))
    student_no: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(50))
    gender: Mapped[Optional[str]] = mapped_column(String(10))
    birth_date: Mapped[Optional[date]] = mapped_column(Date)
    height: Mapped[Optional[float]] = mapped_column(Numeric(5, 2))  # 身高cm
    weight: Mapped[Optional[float]] = mapped_column(Numeric(5, 2))  # 体重kg
    school: Mapped[Optional[str]] = mapped_column(String(100))
    grade: Mapped[Optional[str]] = mapped_column(String(20))
    parent_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"))
    coach_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("coaches.id"))
    remaining_lessons: Mapped[int] = mapped_column(Integer, default=0)  # 剩余课时
    status: Mapped[str] = mapped_column(String(20), default="active")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    user: Mapped[Optional["User"]] = relationship("User", back_populates="student", foreign_keys=[user_id])
    coach: Mapped[Optional["Coach"]] = relationship("Coach", back_populates="students")
    fitness_tests: Mapped[List["FitnessTest"]] = relationship("FitnessTest", back_populates="student")
    training_sessions: Mapped[List["TrainingSession"]] = relationship("TrainingSession", back_populates="student")


class Coach(Base):
    """教练表"""
    __tablename__ = "coaches"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), unique=True)
    coach_no: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(50))
    certification: Mapped[Optional[str]] = mapped_column(Text)  # JSON存储证书列表
    specialty: Mapped[Optional[str]] = mapped_column(Text)  # JSON存储专长列表
    hourly_rate: Mapped[Optional[float]] = mapped_column(Numeric(10, 2))
    status: Mapped[str] = mapped_column(String(20), default="active")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    user: Mapped["User"] = relationship("User", back_populates="coach")
    students: Mapped[List["Student"]] = relationship("Student", back_populates="coach")
    schedules: Mapped[List["Schedule"]] = relationship("Schedule", back_populates="coach")


class ParentStudentRelation(Base):
    """家长-学员关联表"""
    __tablename__ = "parent_student_relations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    parent_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    student_id: Mapped[int] = mapped_column(Integer, ForeignKey("students.id"))
    relation: Mapped[str] = mapped_column(String(20))  # 父亲/母亲/其他
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
