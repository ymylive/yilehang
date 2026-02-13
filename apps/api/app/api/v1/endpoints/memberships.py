"""
课时卡管理API端点
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.endpoints.bookings import get_student_id_for_user
from app.core.database import get_db
from app.core.security import fetch_user_from_token, get_current_user
from app.models.booking import Transaction
from app.schemas.booking import (
    MembershipCardCreate,
    MembershipCardResponse,
    MembershipCardUpdate,
    MembershipRechargeRequest,
    StudentMembershipResponse,
    TransactionResponse,
)
from app.services.booking_service import BookingService, MembershipCardService

router = APIRouter()


# ==================== 学员端API ====================


@router.get("", response_model=List[StudentMembershipResponse])
async def get_my_memberships(
    db: AsyncSession = Depends(get_db), current_user_data: dict = Depends(get_current_user)
):
    """Fetch user model"""
    current_user = await fetch_user_from_token(db, current_user_data)

    """获取我的课时卡列表"""
    student_id = await get_student_id_for_user(current_user, db)
    service = BookingService(db)

    memberships = await service.get_student_memberships(student_id)

    return [
        StudentMembershipResponse(
            id=m.id,
            student_id=m.student_id,
            card_id=m.card_id,
            remaining_times=m.remaining_times,
            expire_date=m.expire_date,
            status=m.status,
            purchase_date=m.purchase_date,
            card=MembershipCardResponse(
                id=m.card.id,
                name=m.card.name,
                card_type=m.card.card_type,
                total_times=m.card.total_times,
                duration_days=m.card.duration_days,
                price=float(m.card.price),
                original_price=float(m.card.original_price) if m.card.original_price else None,
                course_type=m.card.course_type,
                description=m.card.description,
                is_active=m.card.is_active,
                sort_order=m.card.sort_order,
                created_at=m.card.created_at,
            )
            if m.card
            else None,
        )
        for m in memberships
    ]


@router.get("/transactions", response_model=List[TransactionResponse])
async def get_my_transactions(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user_data: dict = Depends(get_current_user),
):
    """Fetch user model"""
    current_user = await fetch_user_from_token(db, current_user_data)

    """获取我的消费记录"""
    student_id = await get_student_id_for_user(current_user, db)

    result = await db.execute(
        select(Transaction)
        .where(Transaction.student_id == student_id)
        .order_by(Transaction.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    transactions = result.scalars().all()

    return [
        TransactionResponse(
            id=t.id,
            student_id=t.student_id,
            type=t.type,
            amount=float(t.amount) if t.amount else None,
            times_change=t.times_change,
            membership_id=t.membership_id,
            booking_id=t.booking_id,
            description=t.description,
            created_at=t.created_at,
        )
        for t in transactions
    ]


# ==================== 管理端API ====================


@router.get("/cards", response_model=List[MembershipCardResponse])
async def get_membership_cards(
    db: AsyncSession = Depends(get_db), current_user_data: dict = Depends(get_current_user)
):
    """Fetch user model"""
    await fetch_user_from_token(db, current_user_data)

    """获取所有课时卡类型"""
    service = MembershipCardService(db)
    cards = await service.get_active_cards()

    return [
        MembershipCardResponse(
            id=c.id,
            name=c.name,
            card_type=c.card_type,
            total_times=c.total_times,
            duration_days=c.duration_days,
            price=float(c.price),
            original_price=float(c.original_price) if c.original_price else None,
            course_type=c.course_type,
            description=c.description,
            is_active=c.is_active,
            sort_order=c.sort_order,
            created_at=c.created_at,
        )
        for c in cards
    ]


@router.post("/cards", response_model=MembershipCardResponse)
async def create_membership_card(
    data: MembershipCardCreate,
    db: AsyncSession = Depends(get_db),
    current_user_data: dict = Depends(get_current_user),
):
    """Fetch user model"""
    current_user = await fetch_user_from_token(db, current_user_data)

    """创建课时卡类型（管理员）"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="权限不足")

    service = MembershipCardService(db)
    card = await service.create_card(data)

    return MembershipCardResponse(
        id=card.id,
        name=card.name,
        card_type=card.card_type,
        total_times=card.total_times,
        duration_days=card.duration_days,
        price=float(card.price),
        original_price=float(card.original_price) if card.original_price else None,
        course_type=card.course_type,
        description=card.description,
        is_active=card.is_active,
        sort_order=card.sort_order,
        created_at=card.created_at,
    )


@router.put("/cards/{card_id}", response_model=MembershipCardResponse)
async def update_membership_card(
    card_id: int,
    data: MembershipCardUpdate,
    db: AsyncSession = Depends(get_db),
    current_user_data: dict = Depends(get_current_user),
):
    """Fetch user model"""
    current_user = await fetch_user_from_token(db, current_user_data)

    """更新课时卡类型（管理员）"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="权限不足")

    service = MembershipCardService(db)
    try:
        card = await service.update_card(card_id, data)
        return MembershipCardResponse(
            id=card.id,
            name=card.name,
            card_type=card.card_type,
            total_times=card.total_times,
            duration_days=card.duration_days,
            price=float(card.price),
            original_price=float(card.original_price) if card.original_price else None,
            course_type=card.course_type,
            description=card.description,
            is_active=card.is_active,
            sort_order=card.sort_order,
            created_at=card.created_at,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/recharge", response_model=StudentMembershipResponse)
async def recharge_membership(
    data: MembershipRechargeRequest,
    db: AsyncSession = Depends(get_db),
    current_user_data: dict = Depends(get_current_user),
):
    """Fetch user model"""
    current_user = await fetch_user_from_token(db, current_user_data)

    """管理员手动充值课时"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="权限不足")

    service = BookingService(db)
    try:
        membership = await service.recharge_membership(data, current_user.id)
        return StudentMembershipResponse(
            id=membership.id,
            student_id=membership.student_id,
            card_id=membership.card_id,
            remaining_times=membership.remaining_times,
            expire_date=membership.expire_date,
            status=membership.status,
            purchase_date=membership.purchase_date,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
