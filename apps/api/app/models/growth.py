"""
成长档案相关数据模型
"""

from datetime import date, datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Date, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import Student


class MetricType(str, Enum):
    """体测指标类型(五维能力)"""

    SPEED = "speed"  # 速度
    AGILITY = "agility"  # 灵敏
    ENDURANCE = "endurance"  # 耐力
    STRENGTH = "strength"  # 力量
    FLEXIBILITY = "flexibility"  # 柔韧


class FitnessTest(Base):
    """体测记录表"""

    __tablename__ = "fitness_tests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    student_id: Mapped[int] = mapped_column(Integer, ForeignKey("students.id"))
    test_date: Mapped[date] = mapped_column(Date)
    tester_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("coaches.id"))
    height: Mapped[Optional[float]] = mapped_column(Numeric(5, 2))
    weight: Mapped[Optional[float]] = mapped_column(Numeric(5, 2))
    bmi: Mapped[Optional[float]] = mapped_column(Numeric(4, 2))
    notes: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )

    # 关系
    student: Mapped["Student"] = relationship("Student", back_populates="fitness_tests")
    metrics: Mapped[List["FitnessMetric"]] = relationship("FitnessMetric", back_populates="test")


class FitnessMetric(Base):
    """体测指标表"""

    __tablename__ = "fitness_metrics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    test_id: Mapped[int] = mapped_column(Integer, ForeignKey("fitness_tests.id"))
    metric_type: Mapped[str] = mapped_column(String(20))  # 五维类型
    metric_name: Mapped[str] = mapped_column(String(50))  # 具体指标名称
    value: Mapped[float] = mapped_column(Numeric(10, 2))  # 原始值
    score: Mapped[Optional[float]] = mapped_column(Numeric(5, 2))  # 得分
    national_percentile: Mapped[Optional[float]] = mapped_column(Numeric(5, 2))  # 全国百分位
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )

    # 关系
    test: Mapped["FitnessTest"] = relationship("FitnessTest", back_populates="metrics")


class TrainingSession(Base):
    """AI训练记录表"""

    __tablename__ = "training_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    student_id: Mapped[int] = mapped_column(Integer, ForeignKey("students.id"))
    exercise_type: Mapped[str] = mapped_column(String(50))  # 运动类型
    duration: Mapped[int] = mapped_column(Integer)  # 训练时长(秒)
    reps_count: Mapped[int] = mapped_column(Integer, default=0)  # 完成次数
    accuracy_score: Mapped[Optional[float]] = mapped_column(Numeric(5, 2))  # 动作准确度
    calories_burned: Mapped[Optional[float]] = mapped_column(Numeric(6, 2))  # 消耗卡路里
    video_url: Mapped[Optional[str]] = mapped_column(String(500))  # 训练视频
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )

    # 关系
    student: Mapped["Student"] = relationship("Student", back_populates="training_sessions")
