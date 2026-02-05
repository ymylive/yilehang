"""
约课系统相关数据模型
"""
from datetime import datetime, date, time
from typing import Optional, List
from enum import Enum

from sqlalchemy import String, Integer, Boolean, DateTime, Date, Time, Text, ForeignKey, Numeric, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class CardType(str, Enum):
    """课时卡类型"""
    TIMES = "times"  # 次卡
    DURATION = "duration"  # 时长卡


class MembershipStatus(str, Enum):
    """课时卡状态"""
    ACTIVE = "active"
    EXPIRED = "expired"
    EXHAUSTED = "exhausted"


class BookingStatus(str, Enum):
    """预约状态"""
    PENDING = "pending"  # 待确认
    CONFIRMED = "confirmed"  # 已确认
    CANCELLED = "cancelled"  # 已取消
    COMPLETED = "completed"  # 已完成
    NO_SHOW = "no_show"  # 未到


class TransactionType(str, Enum):
    """交易类型"""
    PURCHASE = "purchase"  # 购买
    CONSUME = "consume"  # 消费
    REFUND = "refund"  # 退款
    GIFT = "gift"  # 赠送
    MANUAL = "manual"  # 手动调整


class MembershipCard(Base):
    """课时卡/套餐表"""
    __tablename__ = "membership_cards"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100))  # 卡名：次卡/月卡/季卡/年卡
    card_type: Mapped[str] = mapped_column(String(20))  # 类型：times(次卡)/duration(时长卡)
    total_times: Mapped[Optional[int]] = mapped_column(Integer)  # 总次数（次卡用）
    duration_days: Mapped[Optional[int]] = mapped_column(Integer)  # 有效天数（时长卡用）
    price: Mapped[float] = mapped_column(Numeric(10, 2))  # 价格
    original_price: Mapped[Optional[float]] = mapped_column(Numeric(10, 2))  # 原价
    course_type: Mapped[Optional[str]] = mapped_column(String(20))  # 适用课程类型：group/private/all
    description: Mapped[Optional[str]] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)  # 排序
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    student_memberships: Mapped[List["StudentMembership"]] = relationship("StudentMembership", back_populates="card")


class StudentMembership(Base):
    """学员课时账户表"""
    __tablename__ = "student_memberships"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    student_id: Mapped[int] = mapped_column(Integer, ForeignKey("students.id"))
    card_id: Mapped[int] = mapped_column(Integer, ForeignKey("membership_cards.id"))
    remaining_times: Mapped[int] = mapped_column(Integer, default=0)  # 剩余次数
    expire_date: Mapped[Optional[date]] = mapped_column(Date)  # 到期日期
    status: Mapped[str] = mapped_column(String(20), default=MembershipStatus.ACTIVE.value)
    purchase_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # 关系
    student: Mapped["Student"] = relationship("Student", back_populates="memberships")
    card: Mapped["MembershipCard"] = relationship("MembershipCard", back_populates="student_memberships")
    transactions: Mapped[List["Transaction"]] = relationship("Transaction", back_populates="membership")
    bookings: Mapped[List["Booking"]] = relationship("Booking", back_populates="membership")


class CoachAvailableSlot(Base):
    """教练可约时段表"""
    __tablename__ = "coach_available_slots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    coach_id: Mapped[int] = mapped_column(Integer, ForeignKey("coaches.id"))
    day_of_week: Mapped[int] = mapped_column(Integer)  # 0-6 周日到周六
    start_time: Mapped[time] = mapped_column(Time)
    end_time: Mapped[time] = mapped_column(Time)
    slot_duration: Mapped[int] = mapped_column(Integer, default=60)  # 每个时段时长（分钟）
    max_students: Mapped[int] = mapped_column(Integer, default=1)  # 最大学员数（私教=1，小班>1）
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # 关系
    coach: Mapped["Coach"] = relationship("Coach", back_populates="available_slots")


class Booking(Base):
    """预约记录表"""
    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    student_id: Mapped[int] = mapped_column(Integer, ForeignKey("students.id"))
    coach_id: Mapped[int] = mapped_column(Integer, ForeignKey("coaches.id"))
    schedule_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("schedules.id"))  # 关联排课
    booking_date: Mapped[date] = mapped_column(Date)
    start_time: Mapped[time] = mapped_column(Time)
    end_time: Mapped[time] = mapped_column(Time)
    course_type: Mapped[str] = mapped_column(String(20), default="private")  # private/group
    status: Mapped[str] = mapped_column(String(20), default=BookingStatus.PENDING.value)
    cancel_reason: Mapped[Optional[str]] = mapped_column(Text)
    cancelled_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    cancelled_by: Mapped[Optional[int]] = mapped_column(Integer)  # 取消人ID
    membership_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("student_memberships.id"))  # 扣费的课时卡
    remark: Mapped[Optional[str]] = mapped_column(Text)  # 备注
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    student: Mapped["Student"] = relationship("Student", back_populates="bookings")
    coach: Mapped["Coach"] = relationship("Coach", back_populates="bookings")
    schedule: Mapped[Optional["Schedule"]] = relationship("Schedule", back_populates="bookings")
    membership: Mapped[Optional["StudentMembership"]] = relationship("StudentMembership", back_populates="bookings")
    review: Mapped[Optional["Review"]] = relationship("Review", back_populates="booking", uselist=False)
    coach_feedback: Mapped[Optional["CoachFeedback"]] = relationship("CoachFeedback", back_populates="booking", uselist=False)
    transactions: Mapped[List["Transaction"]] = relationship("Transaction", back_populates="booking")


class Transaction(Base):
    """消费记录表"""
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    student_id: Mapped[int] = mapped_column(Integer, ForeignKey("students.id"))
    type: Mapped[str] = mapped_column(String(20))  # purchase/consume/refund/gift/manual
    amount: Mapped[Optional[float]] = mapped_column(Numeric(10, 2))  # 金额
    times_change: Mapped[int] = mapped_column(Integer, default=0)  # 课时变动
    membership_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("student_memberships.id"))
    booking_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("bookings.id"))
    description: Mapped[Optional[str]] = mapped_column(Text)
    operator_id: Mapped[Optional[int]] = mapped_column(Integer)  # 操作人ID
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # 关系
    membership: Mapped[Optional["StudentMembership"]] = relationship("StudentMembership", back_populates="transactions")
    booking: Mapped[Optional["Booking"]] = relationship("Booking", back_populates="transactions")


class Review(Base):
    """评价表"""
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    booking_id: Mapped[int] = mapped_column(Integer, ForeignKey("bookings.id"), unique=True)
    student_id: Mapped[int] = mapped_column(Integer, ForeignKey("students.id"))
    coach_id: Mapped[int] = mapped_column(Integer, ForeignKey("coaches.id"))
    rating: Mapped[int] = mapped_column(Integer)  # 1-5星
    content: Mapped[Optional[str]] = mapped_column(Text)
    tags: Mapped[Optional[str]] = mapped_column(Text)  # JSON存储标签：专业、耐心、准时等
    is_anonymous: Mapped[bool] = mapped_column(Boolean, default=False)
    coach_reply: Mapped[Optional[str]] = mapped_column(Text)  # 教练回复
    coach_reply_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # 关系
    booking: Mapped["Booking"] = relationship("Booking", back_populates="review")
    student: Mapped["Student"] = relationship("Student", back_populates="reviews")
    coach: Mapped["Coach"] = relationship("Coach", back_populates="reviews")


class CoachFeedback(Base):
    """教练反馈表"""
    __tablename__ = "coach_feedbacks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    booking_id: Mapped[int] = mapped_column(Integer, ForeignKey("bookings.id"))
    coach_id: Mapped[int] = mapped_column(Integer, ForeignKey("coaches.id"))
    student_id: Mapped[int] = mapped_column(Integer, ForeignKey("students.id"))
    performance_rating: Mapped[Optional[int]] = mapped_column(Integer)  # 1-5表现评分
    content: Mapped[str] = mapped_column(Text)  # 学习反馈内容
    suggestions: Mapped[Optional[str]] = mapped_column(Text)  # 改进建议
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # 关系
    booking: Mapped["Booking"] = relationship("Booking", back_populates="coach_feedback")
    student: Mapped["Student"] = relationship("Student", back_populates="coach_feedbacks")
    coach: Mapped["Coach"] = relationship("Coach", back_populates="feedbacks")


# 需要在 user.py 和 course.py 中添加反向关系
# 这里通过字符串引用来避免循环导入
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.models.user import Student, Coach
    from app.models.course import Schedule
