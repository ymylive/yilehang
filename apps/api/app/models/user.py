"""
用户相关数据模型
"""

from datetime import date, datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.booking import (
        Booking,
        CoachAvailableSlot,
        CoachFeedback,
        Review,
        StudentMembership,
    )
    from app.models.course import Schedule
    from app.models.energy import EnergyAccount
    from app.models.growth import FitnessTest, TrainingSession
    from app.models.rbac import Role


def utc_now_naive() -> datetime:
    """UTC now as naive datetime, matching TIMESTAMP WITHOUT TIME ZONE columns."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


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
    email: Mapped[Optional[str]] = mapped_column(String(100), unique=True, index=True)
    password_hash: Mapped[Optional[str]] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(20), default=UserRole.PARENT.value)
    wechat_openid: Mapped[Optional[str]] = mapped_column(String(100), unique=True, index=True)
    avatar: Mapped[Optional[str]] = mapped_column(String(500))
    nickname: Mapped[Optional[str]] = mapped_column(String(50))
    status: Mapped[str] = mapped_column(String(20), default=UserStatus.ACTIVE.value)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now_naive)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=utc_now_naive,
        onupdate=utc_now_naive,
    )

    # 关系
    student: Mapped[Optional["Student"]] = relationship(
        "Student", back_populates="user", uselist=False, foreign_keys="[Student.user_id]"
    )
    coach: Mapped[Optional["Coach"]] = relationship("Coach", back_populates="user", uselist=False)
    roles: Mapped[List["Role"]] = relationship(
        "Role", secondary="user_roles", back_populates="users"
    )


class Student(Base):
    """学员表"""

    __tablename__ = "students"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    student_no: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(50))
    phone: Mapped[Optional[str]] = mapped_column(String(20))  # 学员手机号
    gender: Mapped[Optional[str]] = mapped_column(String(10))
    birth_date: Mapped[Optional[date]] = mapped_column(Date)
    age: Mapped[Optional[int]] = mapped_column(Integer)  # 年龄
    height: Mapped[Optional[float]] = mapped_column(Numeric(5, 2))  # 身高cm
    weight: Mapped[Optional[float]] = mapped_column(Numeric(5, 2))  # 体重kg
    school: Mapped[Optional[str]] = mapped_column(String(100))
    grade: Mapped[Optional[str]] = mapped_column(String(20))
    parent_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"))
    coach_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("coaches.id"))
    remaining_lessons: Mapped[int] = mapped_column(Integer, default=0)  # 剩余课时
    status: Mapped[str] = mapped_column(String(20), default="active")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now_naive)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=utc_now_naive,
        onupdate=utc_now_naive,
    )

    # 关系
    user: Mapped["User"] = relationship("User", back_populates="student", foreign_keys=[user_id])
    coach: Mapped[Optional["Coach"]] = relationship("Coach", back_populates="students")
    fitness_tests: Mapped[List["FitnessTest"]] = relationship(
        "FitnessTest", back_populates="student"
    )
    training_sessions: Mapped[List["TrainingSession"]] = relationship(
        "TrainingSession", back_populates="student"
    )
    # 约课系统关系
    memberships: Mapped[List["StudentMembership"]] = relationship(
        "StudentMembership", back_populates="student"
    )
    bookings: Mapped[List["Booking"]] = relationship("Booking", back_populates="student")
    reviews: Mapped[List["Review"]] = relationship("Review", back_populates="student")
    coach_feedbacks: Mapped[List["CoachFeedback"]] = relationship(
        "CoachFeedback", back_populates="student"
    )
    # 能量系统关系
    energy_account: Mapped[Optional["EnergyAccount"]] = relationship(
        "EnergyAccount", back_populates="student", uselist=False
    )


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
    commission_rate: Mapped[Optional[float]] = mapped_column(Numeric(5, 2))  # 提成比例
    introduction: Mapped[Optional[str]] = mapped_column(Text)  # 个人介绍
    certificates: Mapped[Optional[str]] = mapped_column(Text)  # JSON存储证书图片URL
    avatar: Mapped[Optional[str]] = mapped_column(String(500))  # 教练头像
    years_of_experience: Mapped[Optional[int]] = mapped_column(Integer)  # 从业年限
    status: Mapped[str] = mapped_column(String(20), default="active")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now_naive)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=utc_now_naive,
        onupdate=utc_now_naive,
    )

    # 关系
    user: Mapped["User"] = relationship("User", back_populates="coach")
    students: Mapped[List["Student"]] = relationship("Student", back_populates="coach")
    schedules: Mapped[List["Schedule"]] = relationship("Schedule", back_populates="coach")
    # 约课系统关系
    available_slots: Mapped[List["CoachAvailableSlot"]] = relationship(
        "CoachAvailableSlot", back_populates="coach"
    )
    bookings: Mapped[List["Booking"]] = relationship("Booking", back_populates="coach")
    reviews: Mapped[List["Review"]] = relationship("Review", back_populates="coach")
    feedbacks: Mapped[List["CoachFeedback"]] = relationship("CoachFeedback", back_populates="coach")


class ParentStudentRelation(Base):
    """家长-学员关联表"""

    __tablename__ = "parent_student_relations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    parent_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    student_id: Mapped[int] = mapped_column(Integer, ForeignKey("students.id"))
    relation: Mapped[str] = mapped_column(String(20))  # 父亲/母亲/其他
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now_naive)
