"""
评价管理API端点
"""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import fetch_user_from_token, get_current_user
from app.schemas.booking import (
    CoachFeedbackCreate,
    CoachFeedbackResponse,
    ReviewCreate,
    ReviewResponse,
)
from app.services.booking_service import CoachFeedbackService, ReviewService

router = APIRouter()


@router.post("", response_model=ReviewResponse)
async def create_review(
    data: ReviewCreate,
    db: AsyncSession = Depends(get_db),
    current_user_data: dict = Depends(get_current_user)
):
    """Fetch user model"""
    current_user = await fetch_user_from_token(db, current_user_data)

    """提交评价"""
    from app.api.v1.endpoints.bookings import get_student_id_for_user

    student_id = await get_student_id_for_user(current_user, db)
    service = ReviewService(db)

    try:
        review = await service.create_review(data, student_id)
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


# ==================== 教练反馈 ====================

@router.post("/feedbacks", response_model=CoachFeedbackResponse)
async def create_coach_feedback(
    data: CoachFeedbackCreate,
    db: AsyncSession = Depends(get_db),
    current_user_data: dict = Depends(get_current_user)
):
    """Fetch user model"""
    current_user = await fetch_user_from_token(db, current_user_data)

    """教练提交学习反馈"""
    if current_user.role != "coach":
        raise HTTPException(status_code=403, detail="仅教练可访问")

    coach = current_user.coach
    if not coach:
        raise HTTPException(status_code=400, detail="未找到教练信息")

    service = CoachFeedbackService(db)
    try:
        feedback = await service.create_feedback(data, coach.id)
        return CoachFeedbackResponse(
            id=feedback.id,
            booking_id=feedback.booking_id,
            coach_id=feedback.coach_id,
            student_id=feedback.student_id,
            performance_rating=feedback.performance_rating,
            content=feedback.content,
            suggestions=feedback.suggestions,
            created_at=feedback.created_at
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/feedbacks/my", response_model=List[CoachFeedbackResponse])
async def get_my_feedbacks(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user_data: dict = Depends(get_current_user)
):
    """Fetch user model"""
    current_user = await fetch_user_from_token(db, current_user_data)

    """获取我收到的教练反馈"""
    from app.api.v1.endpoints.bookings import get_student_id_for_user

    student_id = await get_student_id_for_user(current_user, db)
    service = CoachFeedbackService(db)

    feedbacks, total = await service.get_student_feedbacks(student_id, page, page_size)

    return [
        CoachFeedbackResponse(
            id=f.id,
            booking_id=f.booking_id,
            coach_id=f.coach_id,
            student_id=f.student_id,
            performance_rating=f.performance_rating,
            content=f.content,
            suggestions=f.suggestions,
            created_at=f.created_at
        )
        for f in feedbacks
    ]


@router.get("/coach/my", response_model=dict)
async def get_my_coach_reviews(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user_data: dict = Depends(get_current_user)
):
    """Fetch user model"""
    current_user = await fetch_user_from_token(db, current_user_data)

    """获取当前教练的所有评价"""
    if current_user.role != "coach":
        raise HTTPException(status_code=403, detail="仅教练可访问")

    coach = current_user.coach
    if not coach:
        raise HTTPException(status_code=400, detail="未找到教练信息")

    service = ReviewService(db)
    reviews, total, avg_rating = await service.get_coach_reviews(coach.id, page, page_size)

    import json
    return {
        "items": [
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
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
        "avg_rating": avg_rating
    }


@router.get("/feedbacks", response_model=dict)
async def get_coach_feedbacks(
    student_id: Optional[int] = Query(None, description="按学员ID过滤"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user_data: dict = Depends(get_current_user)
):
    """Fetch user model"""
    current_user = await fetch_user_from_token(db, current_user_data)

    """获取教练反馈列表"""
    if current_user.role != "coach":
        raise HTTPException(status_code=403, detail="仅教练可访问")

    coach = current_user.coach
    if not coach:
        raise HTTPException(status_code=400, detail="未找到教练信息")

    from app.models.booking import CoachFeedback

    query = select(CoachFeedback).where(CoachFeedback.coach_id == coach.id)

    if student_id:
        query = query.where(CoachFeedback.student_id == student_id)

    query = query.order_by(CoachFeedback.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    feedbacks = result.scalars().all()

    count_query = (
        select(func.count())
        .select_from(CoachFeedback)
        .where(CoachFeedback.coach_id == coach.id)
    )
    if student_id:
        count_query = count_query.where(CoachFeedback.student_id == student_id)

    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    return {
        "items": [
            CoachFeedbackResponse(
                id=f.id,
                booking_id=f.booking_id,
                coach_id=f.coach_id,
                student_id=f.student_id,
                performance_rating=f.performance_rating,
                content=f.content,
                suggestions=f.suggestions,
                created_at=f.created_at
            )
            for f in feedbacks
        ],
        "total": total,
        "page": page,
        "page_size": page_size
    }
