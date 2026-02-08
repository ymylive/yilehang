"""
聊天 API
"""
import json
from typing import Optional, List, Dict
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, and_, update

from app.core.database import get_db
from app.core.security import get_current_user, decode_access_token
from app.models.user import User
from app.models.chat import Conversation, Message, MessageReadStatus, MessageStatus
from app.schemas.chat import (
    ConversationCreate, ConversationResponse, ConversationListResponse,
    MessageCreate, MessageResponse, MessageListResponse,
    UserBrief,
)

router = APIRouter()

# WebSocket 连接管理
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, WebSocket] = {}

    async def connect(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: int):
        if user_id in self.active_connections:
            del self.active_connections[user_id]

    async def send_personal_message(self, message: dict, user_id: int):
        if user_id in self.active_connections:
            await self.active_connections[user_id].send_json(message)

    async def broadcast_to_conversation(self, message: dict, user_ids: List[int]):
        for user_id in user_ids:
            await self.send_personal_message(message, user_id)


manager = ConnectionManager()


def user_to_brief(user: User) -> UserBrief:
    """转换用户为简要信息"""
    return UserBrief(
        id=user.id,
        nickname=user.nickname,
        avatar=user.avatar,
        role=user.role,
    )


@router.get("/conversations", response_model=ConversationListResponse)
async def get_conversations(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取会话列表"""
    query = select(Conversation).where(
        or_(
            Conversation.participant1_id == current_user.id,
            Conversation.participant2_id == current_user.id,
        )
    )

    # 获取总数
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query) or 0

    # 获取列表
    query = query.order_by(Conversation.last_message_at.desc().nullslast()).offset(skip).limit(limit)
    result = await db.execute(query)
    conversations = result.scalars().all()

    items = []
    for conv in conversations:
        # 获取对方用户信息
        other_user_id = conv.participant2_id if conv.participant1_id == current_user.id else conv.participant1_id
        other_user_query = select(User).where(User.id == other_user_id)
        other_user_result = await db.execute(other_user_query)
        other_user = other_user_result.scalar_one_or_none()

        # 获取未读消息数
        unread_query = select(func.count()).where(
            Message.conversation_id == conv.id,
            Message.sender_id != current_user.id,
            Message.status != MessageStatus.READ.value,
        )
        unread_count = await db.scalar(unread_query) or 0

        # 获取最后一条消息
        last_message = None
        if conv.last_message_id:
            msg_query = select(Message).where(Message.id == conv.last_message_id)
            msg_result = await db.execute(msg_query)
            last_msg = msg_result.scalar_one_or_none()
            if last_msg:
                last_message = MessageResponse(
                    id=last_msg.id,
                    conversation_id=last_msg.conversation_id,
                    sender_id=last_msg.sender_id,
                    type=last_msg.type,
                    content=last_msg.content,
                    reply_to_id=last_msg.reply_to_id,
                    status=last_msg.status,
                    is_deleted=last_msg.is_deleted,
                    created_at=last_msg.created_at,
                )

        items.append(ConversationResponse(
            id=conv.id,
            type=conv.type,
            participant1_id=conv.participant1_id,
            participant2_id=conv.participant2_id,
            student_id=conv.student_id,
            last_message=last_message,
            last_message_at=conv.last_message_at,
            unread_count=unread_count,
            other_user=user_to_brief(other_user) if other_user else None,
            created_at=conv.created_at,
        ))

    return ConversationListResponse(items=items, total=total)


@router.post("/conversations", response_model=ConversationResponse)
async def create_or_get_conversation(
    data: ConversationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """创建或获取会话"""
    # 检查对方用户是否存在
    other_user_query = select(User).where(User.id == data.participant_id)
    other_user_result = await db.execute(other_user_query)
    other_user = other_user_result.scalar_one_or_none()

    if not other_user:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 查找现有会话
    existing_query = select(Conversation).where(
        or_(
            and_(
                Conversation.participant1_id == current_user.id,
                Conversation.participant2_id == data.participant_id,
            ),
            and_(
                Conversation.participant1_id == data.participant_id,
                Conversation.participant2_id == current_user.id,
            ),
        )
    )
    if data.student_id:
        existing_query = existing_query.where(Conversation.student_id == data.student_id)

    result = await db.execute(existing_query)
    conversation = result.scalar_one_or_none()

    if not conversation:
        # 创建新会话
        conversation = Conversation(
            type=data.type,
            participant1_id=current_user.id,
            participant2_id=data.participant_id,
            student_id=data.student_id,
        )
        db.add(conversation)
        await db.commit()
        await db.refresh(conversation)

    return ConversationResponse(
        id=conversation.id,
        type=conversation.type,
        participant1_id=conversation.participant1_id,
        participant2_id=conversation.participant2_id,
        student_id=conversation.student_id,
        last_message=None,
        last_message_at=conversation.last_message_at,
        unread_count=0,
        other_user=user_to_brief(other_user),
        created_at=conversation.created_at,
    )


@router.get("/conversations/{conversation_id}/messages", response_model=MessageListResponse)
async def get_messages(
    conversation_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取消息列表"""
    # 验证会话权限
    conv_query = select(Conversation).where(
        Conversation.id == conversation_id,
        or_(
            Conversation.participant1_id == current_user.id,
            Conversation.participant2_id == current_user.id,
        )
    )
    conv_result = await db.execute(conv_query)
    conversation = conv_result.scalar_one_or_none()

    if not conversation:
        raise HTTPException(status_code=404, detail="会话不存在")

    # 获取消息总数
    count_query = select(func.count()).where(
        Message.conversation_id == conversation_id,
        Message.is_deleted == False,
    )
    total = await db.scalar(count_query) or 0

    # 获取消息列表
    query = select(Message).where(
        Message.conversation_id == conversation_id,
        Message.is_deleted == False,
    ).order_by(Message.created_at.desc()).offset(skip).limit(limit)

    result = await db.execute(query)
    messages = result.scalars().all()

    # 标记消息为已读
    await db.execute(
        update(Message).where(
            Message.conversation_id == conversation_id,
            Message.sender_id != current_user.id,
            Message.status != MessageStatus.READ.value,
        ).values(status=MessageStatus.READ.value)
    )
    await db.commit()

    items = []
    for msg in messages:
        # 获取发送者信息
        sender_query = select(User).where(User.id == msg.sender_id)
        sender_result = await db.execute(sender_query)
        sender = sender_result.scalar_one_or_none()

        items.append(MessageResponse(
            id=msg.id,
            conversation_id=msg.conversation_id,
            sender_id=msg.sender_id,
            sender=user_to_brief(sender) if sender else None,
            type=msg.type,
            content=msg.content,
            reply_to_id=msg.reply_to_id,
            status=msg.status,
            is_deleted=msg.is_deleted,
            created_at=msg.created_at,
        ))

    return MessageListResponse(
        items=items,
        total=total,
        has_more=skip + limit < total,
    )


@router.post("/conversations/{conversation_id}/messages", response_model=MessageResponse)
async def send_message(
    conversation_id: int,
    data: MessageCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """发送消息"""
    # 验证会话权限
    conv_query = select(Conversation).where(
        Conversation.id == conversation_id,
        or_(
            Conversation.participant1_id == current_user.id,
            Conversation.participant2_id == current_user.id,
        )
    )
    conv_result = await db.execute(conv_query)
    conversation = conv_result.scalar_one_or_none()

    if not conversation:
        raise HTTPException(status_code=404, detail="会话不存在")

    # 创建消息
    message = Message(
        conversation_id=conversation_id,
        sender_id=current_user.id,
        type=data.type,
        content=data.content,
        reply_to_id=data.reply_to_id,
    )
    db.add(message)
    await db.flush()

    # 更新会话最后消息
    conversation.last_message_id = message.id
    conversation.last_message_at = message.created_at
    await db.commit()
    await db.refresh(message)

    response = MessageResponse(
        id=message.id,
        conversation_id=message.conversation_id,
        sender_id=message.sender_id,
        sender=user_to_brief(current_user),
        type=message.type,
        content=message.content,
        reply_to_id=message.reply_to_id,
        status=message.status,
        is_deleted=message.is_deleted,
        created_at=message.created_at,
    )

    # 通过 WebSocket 推送消息给对方
    other_user_id = conversation.participant2_id if conversation.participant1_id == current_user.id else conversation.participant1_id
    await manager.send_personal_message(
        {
            "type": "new_message",
            "data": response.model_dump(mode="json"),
        },
        other_user_id,
    )

    return response


@router.put("/messages/{message_id}/read")
async def mark_message_read(
    message_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """标记消息已读"""
    query = select(Message).where(Message.id == message_id)
    result = await db.execute(query)
    message = result.scalar_one_or_none()

    if not message:
        raise HTTPException(status_code=404, detail="消息不存在")

    # 验证权限
    conv_query = select(Conversation).where(
        Conversation.id == message.conversation_id,
        or_(
            Conversation.participant1_id == current_user.id,
            Conversation.participant2_id == current_user.id,
        )
    )
    conv_result = await db.execute(conv_query)
    if not conv_result.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="无权限")

    message.status = MessageStatus.READ.value
    await db.commit()

    return {"message": "已标记为已读"}


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(...),
):
    """WebSocket 连接"""
    # 验证 token
    try:
        payload = decode_access_token(token)
        user_id = payload.get("sub")
        if not user_id:
            await websocket.close(code=4001)
            return
    except Exception:
        await websocket.close(code=4001)
        return

    await manager.connect(websocket, int(user_id))

    try:
        while True:
            data = await websocket.receive_text()
            # 处理心跳
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        manager.disconnect(int(user_id))
