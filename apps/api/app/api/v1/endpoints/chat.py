"""
鑱婂ぉ API
"""
import asyncio
import secrets
from time import monotonic
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect
from sqlalchemy import and_, func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import decode_access_token, fetch_user_from_token, get_current_user
from app.models.chat import Conversation, Message, MessageStatus
from app.models.user import User
from app.schemas.chat import (
    ConversationCreate,
    ConversationListResponse,
    ConversationResponse,
    MessageCreate,
    MessageListResponse,
    MessageResponse,
    UserBrief,
)

router = APIRouter()

# WebSocket 杩炴帴绠＄悊
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
        sockets = [self.active_connections.get(user_id) for user_id in user_ids]
        send_tasks = [socket.send_json(message) for socket in sockets if socket is not None]
        if send_tasks:
            await asyncio.gather(*send_tasks, return_exceptions=True)


manager = ConnectionManager()


class WsTicketStore:
    """Short-lived one-time ticket storage for browser WebSocket auth."""

    def __init__(self):
        self._tickets: Dict[str, tuple[int, float]] = {}

    def issue(self, user_id: int, ttl_seconds: int = 60) -> str:
        ticket = secrets.token_urlsafe(32)
        self._tickets[ticket] = (user_id, monotonic() + ttl_seconds)
        return ticket

    def consume(self, ticket: str) -> Optional[int]:
        now = monotonic()
        expired = [key for key, (_, expires_at) in self._tickets.items() if expires_at <= now]
        for key in expired:
            self._tickets.pop(key, None)

        value = self._tickets.pop(ticket, None)
        if value is None:
            return None

        user_id, expires_at = value
        if expires_at <= now:
            return None
        return user_id


ticket_store = WsTicketStore()


def user_to_brief(user: User) -> UserBrief:
    """Convert user model to a lightweight response schema."""
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
    current_user_data: dict = Depends(get_current_user),
):
    """Fetch user model"""
    current_user = await fetch_user_from_token(db, current_user_data)

    """鑾峰彇浼氳瘽鍒楄〃"""
    query = select(Conversation).where(
        or_(
            Conversation.participant1_id == current_user.id,
            Conversation.participant2_id == current_user.id,
        )
    )

    # 鑾峰彇鎬绘暟
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query) or 0

    # 鑾峰彇鍒楄〃
    query = (
        query.order_by(Conversation.last_message_at.desc().nullslast())
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(query)
    conversations = result.scalars().all()

    conversation_ids = [conv.id for conv in conversations]
    other_user_ids = {
        conv.participant2_id if conv.participant1_id == current_user.id else conv.participant1_id
        for conv in conversations
    }
    last_message_ids = {conv.last_message_id for conv in conversations if conv.last_message_id}

    users_map = {}
    if other_user_ids:
        users_result = await db.execute(select(User).where(User.id.in_(other_user_ids)))
        users_map = {user.id: user for user in users_result.scalars().all()}

    unread_counts = {}
    if conversation_ids:
        unread_result = await db.execute(
            select(Message.conversation_id, func.count().label("count"))
            .where(
                Message.conversation_id.in_(conversation_ids),
                Message.sender_id != current_user.id,
                Message.status != MessageStatus.READ.value,
            )
            .group_by(Message.conversation_id)
        )
        unread_counts = {
            conversation_id: unread_count
            for conversation_id, unread_count in unread_result.all()
        }

    last_messages_map = {}
    if last_message_ids:
        last_messages_result = await db.execute(
            select(Message).where(Message.id.in_(last_message_ids))
        )
        last_messages_map = {
            message.id: message for message in last_messages_result.scalars().all()
        }

    items = []
    for conv in conversations:
        other_user_id = (
            conv.participant2_id
            if conv.participant1_id == current_user.id
            else conv.participant1_id
        )
        other_user = users_map.get(other_user_id)
        unread_count = unread_counts.get(conv.id, 0)

        # 鑾峰彇鏈€鍚庝竴鏉℃秷鎭?        last_message = None
        if conv.last_message_id:
            last_msg = last_messages_map.get(conv.last_message_id)
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
    current_user_data: dict = Depends(get_current_user),
):
    """Fetch user model"""
    current_user = await fetch_user_from_token(db, current_user_data)

    """Create a conversation or return the existing one."""
    # 妫€鏌ュ鏂圭敤鎴锋槸鍚﹀瓨鍦?
    other_user_query = select(User).where(User.id == data.participant_id)
    other_user_result = await db.execute(other_user_query)
    other_user = other_user_result.scalar_one_or_none()

    if not other_user:
        raise HTTPException(status_code=404, detail="Not found")

    # 鏌ユ壘鐜版湁浼氳瘽
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
        # 鍒涘缓鏂颁細璇?
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
    current_user_data: dict = Depends(get_current_user),
):
    """Fetch user model"""
    current_user = await fetch_user_from_token(db, current_user_data)

    """鑾峰彇娑堟伅鍒楄〃"""
    # 楠岃瘉浼氳瘽鏉冮檺
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
        raise HTTPException(status_code=404, detail="Not found")

    # 鑾峰彇娑堟伅鎬绘暟
    count_query = select(func.count()).where(
        Message.conversation_id == conversation_id,
        Message.is_deleted.is_(False),
    )
    total = await db.scalar(count_query) or 0

    # 鑾峰彇娑堟伅鍒楄〃
    query = select(Message).where(
        Message.conversation_id == conversation_id,
        Message.is_deleted.is_(False),
    ).order_by(Message.created_at.desc()).offset(skip).limit(limit)

    result = await db.execute(query)
    messages = result.scalars().all()

    # 鏍囪娑堟伅涓哄凡璇?
    await db.execute(
        update(Message).where(
            Message.conversation_id == conversation_id,
            Message.sender_id != current_user.id,
            Message.status != MessageStatus.READ.value,
        ).values(status=MessageStatus.READ.value)
    )
    await db.commit()

    sender_ids = {msg.sender_id for msg in messages}
    senders_map = {}
    if sender_ids:
        senders_result = await db.execute(select(User).where(User.id.in_(sender_ids)))
        senders_map = {sender.id: sender for sender in senders_result.scalars().all()}

    items = []
    for msg in messages:
        sender = senders_map.get(msg.sender_id)

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
    current_user_data: dict = Depends(get_current_user),
):
    """Fetch user model"""
    current_user = await fetch_user_from_token(db, current_user_data)

    """Send a message to the target conversation."""
    # 楠岃瘉浼氳瘽鏉冮檺
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
        raise HTTPException(status_code=404, detail="Not found")

    # 鍒涘缓娑堟伅
    message = Message(
        conversation_id=conversation_id,
        sender_id=current_user.id,
        type=data.type,
        content=data.content,
        reply_to_id=data.reply_to_id,
    )
    db.add(message)
    await db.flush()

    # 鏇存柊浼氳瘽鏈€鍚庢秷鎭?
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

    # 閫氳繃 WebSocket 鎺ㄩ€佹秷鎭粰瀵规柟
    other_user_id = (
        conversation.participant2_id
        if conversation.participant1_id == current_user.id
        else conversation.participant1_id
    )
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
    current_user_data: dict = Depends(get_current_user),
):
    """Fetch user model"""
    current_user = await fetch_user_from_token(db, current_user_data)

    """鏍囪娑堟伅宸茶"""
    query = select(Message).where(Message.id == message_id)
    result = await db.execute(query)
    message = result.scalar_one_or_none()

    if not message:
        raise HTTPException(status_code=404, detail="Not found")

    # 楠岃瘉鏉冮檺
    conv_query = select(Conversation).where(
        Conversation.id == message.conversation_id,
        or_(
            Conversation.participant1_id == current_user.id,
            Conversation.participant2_id == current_user.id,
        )
    )
    conv_result = await db.execute(conv_query)
    if not conv_result.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="Permission denied")

    message.status = MessageStatus.READ.value
    await db.commit()

    return {"message": "宸叉爣璁颁负宸茶"}


@router.post("/ws-ticket")
async def create_websocket_ticket(
    db: AsyncSession = Depends(get_db),
    current_user_data: dict = Depends(get_current_user),
):
    """Create a short-lived one-time ticket for browser WebSocket auth."""
    current_user = await fetch_user_from_token(db, current_user_data)
    ticket = ticket_store.issue(current_user.id)
    return {"ticket": ticket, "expires_in": 60}


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    ticket: Optional[str] = Query(default=None),
):
    """WebSocket connection endpoint."""
    user_id: Optional[int] = None
    auth_header = websocket.headers.get("authorization")
    if auth_header:
        parts = auth_header.strip().split(" ", 1)
        if len(parts) == 2 and parts[0].lower() == "bearer":
            try:
                payload = decode_access_token(parts[1].strip())
                sub = payload.get("sub") if payload else None
                if sub is not None:
                    user_id = int(sub)
            except Exception:
                user_id = None

    if user_id is None and ticket:
        ticket_user_id = ticket_store.consume(ticket)
        if ticket_user_id is not None:
            user_id = int(ticket_user_id)

    if user_id is None:
        await websocket.close(code=4001)
        return

    await manager.connect(websocket, user_id)

    try:
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        manager.disconnect(user_id)

