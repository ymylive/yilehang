"""
聊天数据模型
"""

from datetime import datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import Student, User


class ConversationType(str, Enum):
    """会话类型"""

    PRIVATE = "private"  # 私聊
    GROUP = "group"  # 群聊


class MessageType(str, Enum):
    """消息类型"""

    TEXT = "text"
    IMAGE = "image"
    VOICE = "voice"
    FILE = "file"


class MessageStatus(str, Enum):
    """消息状态"""

    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"


class Conversation(Base):
    """会话表"""

    __tablename__ = "conversations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    type: Mapped[str] = mapped_column(String(20), default=ConversationType.PRIVATE.value)
    participant1_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), index=True)
    participant2_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), index=True)
    student_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("students.id"), nullable=True
    )
    last_message_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    last_message_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )

    # 关系
    participant1: Mapped["User"] = relationship("User", foreign_keys=[participant1_id])
    participant2: Mapped["User"] = relationship("User", foreign_keys=[participant2_id])
    student: Mapped[Optional["Student"]] = relationship("Student")
    messages: Mapped[List["Message"]] = relationship(
        "Message", back_populates="conversation", order_by="Message.created_at.desc()"
    )


class Message(Base):
    """消息表"""

    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    conversation_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("conversations.id"), index=True
    )
    sender_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), index=True)
    type: Mapped[str] = mapped_column(String(20), default=MessageType.TEXT.value)
    content: Mapped[str] = mapped_column(Text)
    reply_to_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("messages.id"), nullable=True
    )
    status: Mapped[str] = mapped_column(String(20), default=MessageStatus.SENT.value)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )

    # 关系
    conversation: Mapped["Conversation"] = relationship("Conversation", back_populates="messages")
    sender: Mapped["User"] = relationship("User")
    reply_to: Mapped[Optional["Message"]] = relationship("Message", remote_side=[id])


class MessageReadStatus(Base):
    """消息已读状态表"""

    __tablename__ = "message_read_status"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    message_id: Mapped[int] = mapped_column(Integer, ForeignKey("messages.id"), index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), index=True)
    read_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    # 关系
    message: Mapped["Message"] = relationship("Message")
    user: Mapped["User"] = relationship("User")
