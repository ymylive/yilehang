"""
能量支票系统数据模型
"""

from datetime import datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import Student


class EnergyTransactionType(str, Enum):
    """能量交易类型"""

    EARN = "earn"  # 获取
    SPEND = "spend"  # 消费
    EXPIRE = "expire"  # 过期
    ADJUST = "adjust"  # 手动调整
    REFUND = "refund"  # 退还


class EnergySourceType(str, Enum):
    """能量来源类型"""

    TRAINING = "training"  # 完成训练
    CHECKIN = "checkin"  # 签到
    FITNESS_TEST = "fitness_test"  # 完成体测
    ACHIEVEMENT = "achievement"  # 获得成就
    REVIEW = "review"  # 评价课程
    REFERRAL = "referral"  # 推荐好友
    ACTIVITY = "activity"  # 活动奖励
    MANUAL = "manual"  # 手动发放


class EnergyRule(Base):
    """能量积分规则表"""

    __tablename__ = "energy_rules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100))  # 规则名称
    code: Mapped[str] = mapped_column(String(50), unique=True, index=True)  # 规则代码
    source_type: Mapped[str] = mapped_column(String(30))  # 来源类型
    points: Mapped[int] = mapped_column(Integer)  # 基础积分值
    multiplier: Mapped[float] = mapped_column(Numeric(5, 2), default=1.0)  # 倍率
    daily_limit: Mapped[Optional[int]] = mapped_column(Integer)  # 每日上限
    weekly_limit: Mapped[Optional[int]] = mapped_column(Integer)  # 每周上限
    monthly_limit: Mapped[Optional[int]] = mapped_column(Integer)  # 每月上限
    description: Mapped[Optional[str]] = mapped_column(Text)  # 规则说明
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class EnergyAccount(Base):
    """能量账户表"""

    __tablename__ = "energy_accounts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    student_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("students.id"), unique=True, index=True
    )
    balance: Mapped[int] = mapped_column(Integer, default=0)  # 当前余额
    total_earned: Mapped[int] = mapped_column(Integer, default=0)  # 累计获取
    total_spent: Mapped[int] = mapped_column(Integer, default=0)  # 累计消费
    level: Mapped[int] = mapped_column(Integer, default=1)  # 能量等级
    version: Mapped[int] = mapped_column(Integer, default=0)  # 乐观锁版本号
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # 关系
    student: Mapped["Student"] = relationship("Student", back_populates="energy_account")
    transactions: Mapped[List["EnergyTransaction"]] = relationship(
        "EnergyTransaction", back_populates="account"
    )


class EnergyTransaction(Base):
    """能量交易记录表"""

    __tablename__ = "energy_transactions"
    __table_args__ = (Index("ix_energy_transactions_student_created", "student_id", "created_at"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    account_id: Mapped[int] = mapped_column(Integer, ForeignKey("energy_accounts.id"), index=True)
    student_id: Mapped[int] = mapped_column(Integer, ForeignKey("students.id"), index=True)
    type: Mapped[str] = mapped_column(String(20))  # earn/spend/expire/adjust/refund
    source_type: Mapped[Optional[str]] = mapped_column(String(30))  # 来源类型
    amount: Mapped[int] = mapped_column(Integer)  # 变动数量（正数获取，负数消费）
    balance_after: Mapped[int] = mapped_column(Integer)  # 变动后余额
    rule_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("energy_rules.id")
    )  # 关联规则
    reference_type: Mapped[Optional[str]] = mapped_column(String(50))  # 关联业务类型
    reference_id: Mapped[Optional[int]] = mapped_column(Integer)  # 关联业务ID
    description: Mapped[Optional[str]] = mapped_column(String(200))  # 描述
    operator_id: Mapped[Optional[int]] = mapped_column(Integer)  # 操作人ID（手动调整时）
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )

    # 关系
    account: Mapped["EnergyAccount"] = relationship("EnergyAccount", back_populates="transactions")
    rule: Mapped[Optional["EnergyRule"]] = relationship("EnergyRule")


# 能量等级配置
ENERGY_LEVELS = {
    1: {"name": "新手", "min_points": 0, "icon": "🌱"},
    2: {"name": "初级", "min_points": 100, "icon": "🌿"},
    3: {"name": "中级", "min_points": 500, "icon": "🌳"},
    4: {"name": "高级", "min_points": 1500, "icon": "⭐"},
    5: {"name": "精英", "min_points": 3000, "icon": "🏆"},
    6: {"name": "大师", "min_points": 6000, "icon": "👑"},
}
