"""
聊天相关 Schema
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class UserBrief(BaseModel):
    """用户简要信息"""

    id: int
    nickname: Optional[str] = None
    avatar: Optional[str] = None
    role: str

    model_config = ConfigDict(from_attributes=True)


class MessageBase(BaseModel):
    """消息基础模型"""

    type: str = "text"  # text, image, voice
    content: str


class MessageCreate(MessageBase):
    """创建消息"""

    reply_to_id: Optional[int] = None


class MessageResponse(MessageBase):
    """消息响应"""

    id: int
    conversation_id: int
    sender_id: int
    sender: Optional[UserBrief] = None
    reply_to_id: Optional[int] = None
    status: str
    is_deleted: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MessageListResponse(BaseModel):
    """消息列表响应"""

    items: List[MessageResponse]
    total: int
    has_more: bool


class ConversationBase(BaseModel):
    """会话基础模型"""

    type: str = "private"  # private, group


class ConversationCreate(ConversationBase):
    """创建会话"""

    participant_id: int  # 对方用户ID
    student_id: Optional[int] = None  # 关联学员ID（家长-教练聊天时）


class ConversationResponse(ConversationBase):
    """会话响应"""

    id: int
    participant1_id: int
    participant2_id: int
    student_id: Optional[int] = None
    last_message: Optional[MessageResponse] = None
    last_message_at: Optional[datetime] = None
    unread_count: int = 0
    other_user: Optional[UserBrief] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ConversationListResponse(BaseModel):
    """会话列表响应"""

    items: List[ConversationResponse]
    total: int
