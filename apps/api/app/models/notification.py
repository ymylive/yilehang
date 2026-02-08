"""
通知数据模型
"""
from datetime import datetime
from typing import Optional
from enum import Enum

from sqlalchemy import String, Integer, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class NotificationType(str, Enum):
    """通知类型"""
    BOOKING = "booking"      # 预约相关
    REMINDER = "reminder"    # 课程提醒
    FEEDBACK = "feedback"    # 教练反馈
    SYSTEM = "system"        # 系统通知
    CHAT = "chat"            # 聊天消息


class Notification(Base):
    """通知表"""
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), index=True)
    type: Mapped[str] = mapped_column(String(20), default=NotificationType.SYSTEM.value)
    title: Mapped[str] = mapped_column(String(100))
    content: Mapped[str] = mapped_column(Text)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    related_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    related_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # 关系
    user: Mapped["User"] = relationship("User", backref="notifications")
