"""
通知相关 Schema
"""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class NotificationBase(BaseModel):
    """通知基础模型"""
    type: str
    title: str
    content: str
    related_id: Optional[int] = None
    related_type: Optional[str] = None


class NotificationCreate(NotificationBase):
    """创建通知"""
    user_id: int


class NotificationResponse(NotificationBase):
    """通知响应"""
    id: int
    user_id: int
    is_read: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class NotificationListResponse(BaseModel):
    """通知列表响应"""
    items: List[NotificationResponse]
    total: int
    unread_count: int


class NotificationReadRequest(BaseModel):
    """标记已读请求"""
    notification_ids: Optional[List[int]] = None  # 为空则标记全部已读
