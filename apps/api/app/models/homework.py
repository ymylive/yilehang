"""
作业相关数据模型
"""
from datetime import datetime, date
from typing import Optional, List

from sqlalchemy import String, Integer, DateTime, Date, ForeignKey, Numeric, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class HomeworkTemplate(Base):
    """作业模板表"""
    __tablename__ = "homework_templates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(100))
    description: Mapped[Optional[str]] = mapped_column(Text)
    exercise_type: Mapped[str] = mapped_column(String(50))  # 运动类型
    target_reps: Mapped[int] = mapped_column(Integer)  # 目标次数
    points: Mapped[int] = mapped_column(Integer, default=10)  # 积分奖励
    difficulty: Mapped[str] = mapped_column(String(20), default="normal")  # easy/normal/hard
    video_demo_url: Mapped[Optional[str]] = mapped_column(String(500))  # 示范视频
    status: Mapped[str] = mapped_column(String(20), default="active")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # 关系
    assignments: Mapped[List["HomeworkAssignment"]] = relationship("HomeworkAssignment", back_populates="template")


class HomeworkAssignment(Base):
    """作业分配表"""
    __tablename__ = "homework_assignments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    template_id: Mapped[int] = mapped_column(Integer, ForeignKey("homework_templates.id"))
    student_id: Mapped[int] = mapped_column(Integer, ForeignKey("students.id"))
    coach_id: Mapped[int] = mapped_column(Integer, ForeignKey("coaches.id"))
    due_date: Mapped[date] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(20), default="pending")  # pending/submitted/graded/expired
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    template: Mapped["HomeworkTemplate"] = relationship("HomeworkTemplate", back_populates="assignments")
    submission: Mapped[Optional["HomeworkSubmission"]] = relationship("HomeworkSubmission", back_populates="assignment", uselist=False)


class HomeworkSubmission(Base):
    """作业提交表"""
    __tablename__ = "homework_submissions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    assignment_id: Mapped[int] = mapped_column(Integer, ForeignKey("homework_assignments.id"), unique=True)
    video_url: Mapped[str] = mapped_column(String(500))
    reps_completed: Mapped[int] = mapped_column(Integer, default=0)
    ai_score: Mapped[Optional[float]] = mapped_column(Numeric(5, 2))  # AI评分
    coach_score: Mapped[Optional[float]] = mapped_column(Numeric(5, 2))  # 教练评分
    feedback: Mapped[Optional[str]] = mapped_column(Text)  # 教练反馈
    points_earned: Mapped[int] = mapped_column(Integer, default=0)  # 获得积分
    submitted_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    graded_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # 关系
    assignment: Mapped["HomeworkAssignment"] = relationship("HomeworkAssignment", back_populates="submission")
