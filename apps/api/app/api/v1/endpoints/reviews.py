"""
评价管理API端点
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.booking import (
    ReviewCreate, ReviewResponse,
    CoachFeedbackCreate, CoachFeedbackResponse
)
from app.services.booking_service import ReviewService, CoachFeedbackService

router = APIRouter()


@router.post("", response_model=ReviewResponse)
async def create_review(
    data: ReviewCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
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
    current_user: User = Depends(get_current_user)
):
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
    current_user: User = Depends(get_current_user)
):
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
