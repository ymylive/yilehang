"""
预约管理API端点
"""
from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User, Student
from app.schemas.booking import (
    BookingCreate, BookingResponse, BookingListResponse,
    BookingCancelRequest, BookingRescheduleRequest
)
from app.services.booking_service import BookingService

router = APIRouter()


async def get_student_id_for_user(user: User, db: AsyncSession) -> int:
    """获取用户关联的学员ID"""
    from sqlalchemy import select
    from app.models.user import ParentStudentRelation

    if user.role == "student" and user.student:
        return user.student.id

    # 家长用户，获取主要关联的学员
    result = await db.execute(
        select(ParentStudentRelation)
        .where(
            ParentStudentRelation.parent_id == user.id,
            ParentStudentRelation.is_primary == True
        )
    )
    relation = result.scalar_one_or_none()
    if relation:
        return relation.student_id

    # 获取第一个关联的学员
    result = await db.execute(
        select(Student).where(Student.parent_id == user.id)
    )
    student = result.scalar_one_or_none()
    if student:
        return student.id

    raise HTTPException(status_code=400, detail="未找到关联的学员")


@router.get("", response_model=BookingListResponse)
async def get_my_bookings(
    status: Optional[str] = Query(None, description="预约状态筛选"),
    start_date: Optional[date] = Query(None, description="开始日期"),
    end_date: Optional[date] = Query(None, description="结束日期"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取我的预约列表"""
    student_id = await get_student_id_for_user(current_user, db)
    service = BookingService(db)

    bookings, total = await service.get_student_bookings(
        student_id=student_id,
        status=status,
        start_date=start_date,
        end_date=end_date,
        page=page,
        page_size=page_size
    )

    # 转换为响应格式
    items = []
    for booking in bookings:
        item = BookingResponse(
            id=booking.id,
            student_id=booking.student_id,
            coach_id=booking.coach_id,
            schedule_id=booking.schedule_id,
            booking_date=booking.booking_date,
            start_time=booking.start_time,
            end_time=booking.end_time,
            course_type=booking.course_type,
            status=booking.status,
            cancel_reason=booking.cancel_reason,
            cancelled_at=booking.cancelled_at,
            remark=booking.remark,
            created_at=booking.created_at,
            student_name=booking.student.name if booking.student else None,
            coach_name=booking.coach.name if booking.coach else None,
            course_name=booking.schedule.course.name if booking.schedule and booking.schedule.course else None
        )
        items.append(item)

    return BookingListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size
    )


@router.post("", response_model=BookingResponse)
async def create_booking(
    data: BookingCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建预约"""
    student_id = data.student_id
    if not student_id:
        student_id = await get_student_id_for_user(current_user, db)

    service = BookingService(db)

    try:
        booking = await service.create_booking(data, student_id)
        return BookingResponse(
            id=booking.id,
            student_id=booking.student_id,
            coach_id=booking.coach_id,
            schedule_id=booking.schedule_id,
            booking_date=booking.booking_date,
            start_time=booking.start_time,
            end_time=booking.end_time,
            course_type=booking.course_type,
            status=booking.status,
            cancel_reason=booking.cancel_reason,
            cancelled_at=booking.cancelled_at,
            remark=booking.remark,
            created_at=booking.created_at
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{booking_id}", response_model=BookingResponse)
async def get_booking(
    booking_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取预约详情"""
    service = BookingService(db)
    booking = await service.get_booking(booking_id)

    if not booking:
        raise HTTPException(status_code=404, detail="预约不存在")

    return BookingResponse(
        id=booking.id,
        student_id=booking.student_id,
        coach_id=booking.coach_id,
        schedule_id=booking.schedule_id,
        booking_date=booking.booking_date,
        start_time=booking.start_time,
        end_time=booking.end_time,
        course_type=booking.course_type,
        status=booking.status,
        cancel_reason=booking.cancel_reason,
        cancelled_at=booking.cancelled_at,
        remark=booking.remark,
        created_at=booking.created_at,
        student_name=booking.student.name if booking.student else None,
        coach_name=booking.coach.name if booking.coach else None,
        course_name=booking.schedule.course.name if booking.schedule and booking.schedule.course else None
    )


@router.put("/{booking_id}/cancel", response_model=BookingResponse)
async def cancel_booking(
    booking_id: int,
    data: BookingCancelRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """取消预约"""
    service = BookingService(db)

    try:
        booking = await service.cancel_booking(booking_id, current_user.id, data)
        return BookingResponse(
            id=booking.id,
            student_id=booking.student_id,
            coach_id=booking.coach_id,
            schedule_id=booking.schedule_id,
            booking_date=booking.booking_date,
            start_time=booking.start_time,
            end_time=booking.end_time,
            course_type=booking.course_type,
            status=booking.status,
            cancel_reason=booking.cancel_reason,
            cancelled_at=booking.cancelled_at,
            remark=booking.remark,
            created_at=booking.created_at
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{booking_id}/reschedule", response_model=BookingResponse)
async def reschedule_booking(
    booking_id: int,
    data: BookingRescheduleRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """改期预约"""
    service = BookingService(db)

    try:
        booking = await service.reschedule_booking(booking_id, data)
        return BookingResponse(
            id=booking.id,
            student_id=booking.student_id,
            coach_id=booking.coach_id,
            schedule_id=booking.schedule_id,
            booking_date=booking.booking_date,
            start_time=booking.start_time,
            end_time=booking.end_time,
            course_type=booking.course_type,
            status=booking.status,
            cancel_reason=booking.cancel_reason,
            cancelled_at=booking.cancelled_at,
            remark=booking.remark,
            created_at=booking.created_at
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
