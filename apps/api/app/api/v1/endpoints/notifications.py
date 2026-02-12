"""
通知 API
"""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import fetch_user_from_token, get_current_user
from app.models.notification import Notification
from app.schemas.notification import (
    NotificationListResponse,
    NotificationReadRequest,
    NotificationResponse,
)

router = APIRouter()


@router.get("", response_model=NotificationListResponse)
async def get_notifications(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    type: Optional[str] = None,
    is_read: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
    current_user_data: dict = Depends(get_current_user),
):
    """Fetch user model"""
    current_user = await fetch_user_from_token(db, current_user_data)

    """获取通知列表"""
    query = select(Notification).where(Notification.user_id == current_user.id)

    if type:
        query = query.where(Notification.type == type)
    if is_read is not None:
        query = query.where(Notification.is_read == is_read)

    # 获取总数
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query) or 0

    # 获取未读数
    unread_query = select(func.count()).where(
        Notification.user_id == current_user.id,
        Notification.is_read.is_(False),
    )
    unread_count = await db.scalar(unread_query) or 0

    # 获取列表
    query = query.order_by(Notification.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    notifications = result.scalars().all()

    return NotificationListResponse(
        items=[NotificationResponse.model_validate(n) for n in notifications],
        total=total,
        unread_count=unread_count,
    )


@router.put("/{notification_id}/read", response_model=NotificationResponse)
async def mark_notification_read(
    notification_id: int,
    db: AsyncSession = Depends(get_db),
    current_user_data: dict = Depends(get_current_user),
):
    """Fetch user model"""
    current_user = await fetch_user_from_token(db, current_user_data)

    """标记单条通知已读"""
    query = select(Notification).where(
        Notification.id == notification_id,
        Notification.user_id == current_user.id,
    )
    result = await db.execute(query)
    notification = result.scalar_one_or_none()

    if not notification:
        raise HTTPException(status_code=404, detail="通知不存在")

    notification.is_read = True
    await db.commit()
    await db.refresh(notification)

    return NotificationResponse.model_validate(notification)


@router.put("/read-all")
async def mark_all_read(
    request: Optional[NotificationReadRequest] = None,
    db: AsyncSession = Depends(get_db),
    current_user_data: dict = Depends(get_current_user),
):
    """Fetch user model"""
    current_user = await fetch_user_from_token(db, current_user_data)

    """标记全部已读或批量标记已读"""
    query = update(Notification).where(
        Notification.user_id == current_user.id,
        Notification.is_read.is_(False),
    )

    if request and request.notification_ids:
        query = query.where(Notification.id.in_(request.notification_ids))

    query = query.values(is_read=True)
    await db.execute(query)
    await db.commit()

    return {"message": "已标记为已读"}


@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: int,
    db: AsyncSession = Depends(get_db),
    current_user_data: dict = Depends(get_current_user),
):
    """Fetch user model"""
    current_user = await fetch_user_from_token(db, current_user_data)

    """删除通知"""
    query = select(Notification).where(
        Notification.id == notification_id,
        Notification.user_id == current_user.id,
    )
    result = await db.execute(query)
    notification = result.scalar_one_or_none()

    if not notification:
        raise HTTPException(status_code=404, detail="通知不存在")

    await db.delete(notification)
    await db.commit()

    return {"message": "删除成功"}
