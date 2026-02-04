"""
教练相关API端点（扩展）
"""
from datetime import date, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User, Coach
from app.models.booking import Booking, Review, BookingStatus
from app.schemas.booking import (
    CoachDetailResponse, CoachAvailableSlotsResponse, CoachAvailableTimeSlot,
    CoachSlotCreate, CoachSlotUpdate, CoachSlotResponse,
    ReviewResponse, CoachReplyRequest
)
from app.services.booking_service import BookingService, ReviewService

router = APIRouter()


@router.get("", response_model=List[CoachDetailResponse])
async def get_coaches(
    specialty: Optional[str] = Query(None, description="专长筛选"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """获取教练列表"""
    query = select(Coach).where(Coach.status == "active")

    if specialty:
        query = query.where(Coach.specialty.contains(specialty))

    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    coaches = result.scalars().all()

    response = []
    for coach in coaches:
        # 获取统计信息
        # 学员数
        student_count = await db.execute(
            select(func.count()).select_from(
                select(Booking.student_id)
                .where(Booking.coach_id == coach.id)
                .distinct()
                .subquery()
            )
        )
        total_students = student_count.scalar() or 0

        # 课程数
        lesson_count = await db.execute(
            select(func.count()).where(
                Booking.coach_id == coach.id,
                Booking.status == BookingStatus.COMPLETED.value
            )
        )
        total_lessons = lesson_count.scalar() or 0

        # 评分
        rating_result = await db.execute(
            select(func.avg(Review.rating), func.count(Review.id))
            .where(Review.coach_id == coach.id)
        )
        rating_row = rating_result.one()
        avg_rating = float(rating_row[0]) if rating_row[0] else 0.0
        review_count = rating_row[1] or 0

        import json
        response.append(CoachDetailResponse(
            id=coach.id,
            coach_no=coach.coach_no,
            name=coach.name,
            avatar=coach.avatar,
            specialty=json.loads(coach.specialty) if coach.specialty else None,
            introduction=coach.introduction,
            certificates=json.loads(coach.certificates) if coach.certificates else None,
            years_of_experience=coach.years_of_experience,
            hourly_rate=float(coach.hourly_rate) if coach.hourly_rate else None,
            total_students=total_students,
            total_lessons=total_lessons,
            avg_rating=round(avg_rating, 1),
            review_count=review_count
        ))

    return response


@router.get("/{coach_id}", response_model=CoachDetailResponse)
async def get_coach_detail(
    coach_id: int,
    db: AsyncSession = Depends(get_db)
):
    """获取教练详情"""
    coach = await db.get(Coach, coach_id)
    if not coach:
        raise HTTPException(status_code=404, detail="教练不存在")

    # 获取统计信息
    student_count = await db.execute(
        select(func.count()).select_from(
            select(Booking.student_id)
            .where(Booking.coach_id == coach.id)
            .distinct()
            .subquery()
        )
    )
    total_students = student_count.scalar() or 0

    lesson_count = await db.execute(
        select(func.count()).where(
            Booking.coach_id == coach.id,
            Booking.status == BookingStatus.COMPLETED.value
        )
    )
    total_lessons = lesson_count.scalar() or 0

    rating_result = await db.execute(
        select(func.avg(Review.rating), func.count(Review.id))
        .where(Review.coach_id == coach.id)
    )
    rating_row = rating_result.one()
    avg_rating = float(rating_row[0]) if rating_row[0] else 0.0
    review_count = rating_row[1] or 0

    import json
    return CoachDetailResponse(
        id=coach.id,
        coach_no=coach.coach_no,
        name=coach.name,
        avatar=coach.avatar,
        specialty=json.loads(coach.specialty) if coach.specialty else None,
        introduction=coach.introduction,
        certificates=json.loads(coach.certificates) if coach.certificates else None,
        years_of_experience=coach.years_of_experience,
        hourly_rate=float(coach.hourly_rate) if coach.hourly_rate else None,
        total_students=total_students,
        total_lessons=total_lessons,
        avg_rating=round(avg_rating, 1),
        review_count=review_count
    )


@router.get("/{coach_id}/available-slots", response_model=CoachAvailableSlotsResponse)
async def get_coach_available_slots(
    coach_id: int,
    start_date: Optional[date] = Query(None, description="开始日期"),
    end_date: Optional[date] = Query(None, description="结束日期"),
    db: AsyncSession = Depends(get_db)
):
    """获取教练可约时段"""
    coach = await db.get(Coach, coach_id)
    if not coach:
        raise HTTPException(status_code=404, detail="教练不存在")

    if not start_date:
        start_date = date.today()
    if not end_date:
        end_date = start_date + timedelta(days=7)

    service = BookingService(db)
    slots = await service.get_coach_available_times(coach_id, start_date, end_date)

    return CoachAvailableSlotsResponse(
        coach_id=coach_id,
        coach_name=coach.name,
        slots=slots
    )


@router.get("/{coach_id}/reviews", response_model=List[ReviewResponse])
async def get_coach_reviews(
    coach_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """获取教练评价列表"""
    service = ReviewService(db)
    reviews, total, avg_rating = await service.get_coach_reviews(coach_id, page, page_size)

    import json
    return [
        ReviewResponse(
            id=r.id,
            booking_id=r.booking_id,
            student_id=r.student_id,
            coach_id=r.coach_id,
            rating=r.rating,
            content=r.content,
            tags=json.loads(r.tags) if r.tags else None,
            is_anonymous=r.is_anonymous,
            coach_reply=r.coach_reply,
            coach_reply_at=r.coach_reply_at,
            created_at=r.created_at,
            student_name="匿名用户" if r.is_anonymous else None
        )
        for r in reviews
    ]


# ==================== 教练端API ====================

@router.get("/me/slots", response_model=List[CoachSlotResponse])
async def get_my_slots(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取我的可约时段配置"""
    if current_user.role != "coach":
        raise HTTPException(status_code=403, detail="仅教练可访问")

    coach = current_user.coach
    if not coach:
        raise HTTPException(status_code=400, detail="未找到教练信息")

    service = BookingService(db)
    slots = await service.get_coach_slots(coach.id)

    return [
        CoachSlotResponse(
            id=s.id,
            coach_id=s.coach_id,
            day_of_week=s.day_of_week,
            start_time=s.start_time,
            end_time=s.end_time,
            slot_duration=s.slot_duration,
            max_students=s.max_students,
            is_active=s.is_active,
            created_at=s.created_at
        )
        for s in slots
    ]


@router.post("/me/slots", response_model=CoachSlotResponse)
async def create_my_slot(
    data: CoachSlotCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建我的可约时段"""
    if current_user.role != "coach":
        raise HTTPException(status_code=403, detail="仅教练可访问")

    coach = current_user.coach
    if not coach:
        raise HTTPException(status_code=400, detail="未找到教练信息")

    service = BookingService(db)
    slot = await service.create_coach_slot(coach.id, data)

    return CoachSlotResponse(
        id=slot.id,
        coach_id=slot.coach_id,
        day_of_week=slot.day_of_week,
        start_time=slot.start_time,
        end_time=slot.end_time,
        slot_duration=slot.slot_duration,
        max_students=slot.max_students,
        is_active=slot.is_active,
        created_at=slot.created_at
    )


@router.put("/me/slots/{slot_id}", response_model=CoachSlotResponse)
async def update_my_slot(
    slot_id: int,
    data: CoachSlotUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新我的可约时段"""
    if current_user.role != "coach":
        raise HTTPException(status_code=403, detail="仅教练可访问")

    service = BookingService(db)
    try:
        slot = await service.update_coach_slot(slot_id, data)
        return CoachSlotResponse(
            id=slot.id,
            coach_id=slot.coach_id,
            day_of_week=slot.day_of_week,
            start_time=slot.start_time,
            end_time=slot.end_time,
            slot_duration=slot.slot_duration,
            max_students=slot.max_students,
            is_active=slot.is_active,
            created_at=slot.created_at
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/me/slots/{slot_id}")
async def delete_my_slot(
    slot_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除我的可约时段"""
    if current_user.role != "coach":
        raise HTTPException(status_code=403, detail="仅教练可访问")

    service = BookingService(db)
    if not await service.delete_coach_slot(slot_id):
        raise HTTPException(status_code=404, detail="时段不存在")

    return {"message": "删除成功"}


@router.post("/me/reviews/{review_id}/reply", response_model=ReviewResponse)
async def reply_to_review(
    review_id: int,
    data: CoachReplyRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """回复评价"""
    if current_user.role != "coach":
        raise HTTPException(status_code=403, detail="仅教练可访问")

    coach = current_user.coach
    if not coach:
        raise HTTPException(status_code=400, detail="未找到教练信息")

    service = ReviewService(db)
    try:
        review = await service.reply_review(review_id, coach.id, data.reply)
        import json
        return ReviewResponse(
            id=review.id,
            booking_id=review.booking_id,
            student_id=review.student_id,
            coach_id=review.coach_id,
            rating=review.rating,
            content=review.content,
            tags=json.loads(review.tags) if review.tags else None,
            is_anonymous=review.is_anonymous,
            coach_reply=review.coach_reply,
            coach_reply_at=review.coach_reply_at,
            created_at=review.created_at
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
