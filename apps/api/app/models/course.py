"""
课程相关数据模型
"""
from datetime import datetime
from typing import Optional, List
from enum import Enum

from sqlalchemy import String, Integer, DateTime, ForeignKey, Numeric, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class CourseType(str, Enum):
    """课程类型"""
    GROUP = "group"  # 团课
    PRIVATE = "private"  # 私教
    TRIAL = "trial"  # 体验课


class CourseCategory(str, Enum):
    """课程分类"""
    BASKETBALL = "basketball"
    FOOTBALL = "football"
    SWIMMING = "swimming"
    TAEKWONDO = "taekwondo"
    DANCE = "dance"
    GYMNASTICS = "gymnastics"
    TRACK_FIELD = "track_field"
    OTHER = "other"


class Course(Base):
    """课程表"""
    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100))
    code: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    type: Mapped[str] = mapped_column(String(20), default=CourseType.GROUP.value)
    category: Mapped[str] = mapped_column(String(50))
    description: Mapped[Optional[str]] = mapped_column(Text)
    duration: Mapped[int] = mapped_column(Integer, default=60)  # 课程时长(分钟)
    max_students: Mapped[int] = mapped_column(Integer, default=20)
    price: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    status: Mapped[str] = mapped_column(String(20), default="active")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    schedules: Mapped[List["Schedule"]] = relationship("Schedule", back_populates="course")


class Venue(Base):
    """场地表"""
    __tablename__ = "venues"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100))
    address: Mapped[Optional[str]] = mapped_column(String(255))
    capacity: Mapped[int] = mapped_column(Integer, default=50)
    status: Mapped[str] = mapped_column(String(20), default="active")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # 关系
    schedules: Mapped[List["Schedule"]] = relationship("Schedule", back_populates="venue")


class Schedule(Base):
    """排课表"""
    __tablename__ = "schedules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    course_id: Mapped[int] = mapped_column(Integer, ForeignKey("courses.id"))
    coach_id: Mapped[int] = mapped_column(Integer, ForeignKey("coaches.id"))
    venue_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("venues.id"))
    start_time: Mapped[datetime] = mapped_column(DateTime)
    end_time: Mapped[datetime] = mapped_column(DateTime)
    capacity: Mapped[int] = mapped_column(Integer, default=20)
    enrolled_count: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(20), default="scheduled")  # scheduled/ongoing/completed/cancelled
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    course: Mapped["Course"] = relationship("Course", back_populates="schedules")
    coach: Mapped["Coach"] = relationship("Coach", back_populates="schedules")
    venue: Mapped[Optional["Venue"]] = relationship("Venue", back_populates="schedules")
    attendances: Mapped[List["Attendance"]] = relationship("Attendance", back_populates="schedule")


class Attendance(Base):
    """考勤表"""
    __tablename__ = "attendances"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    schedule_id: Mapped[int] = mapped_column(Integer, ForeignKey("schedules.id"))
    student_id: Mapped[int] = mapped_column(Integer, ForeignKey("students.id"))
    check_in_time: Mapped[Optional[datetime]] = mapped_column(DateTime)
    check_in_method: Mapped[Optional[str]] = mapped_column(String(20))  # qrcode/manual/face
    status: Mapped[str] = mapped_column(String(20), default="enrolled")  # enrolled/checked_in/absent/leave
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # 关系
    schedule: Mapped["Schedule"] = relationship("Schedule", back_populates="attendances")
