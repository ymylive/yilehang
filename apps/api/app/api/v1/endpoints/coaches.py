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


# ==================== 教练个人资料 ====================

@router.get("/me/profile")
async def get_my_profile(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """获取教练个人资料"""
    if current_user["role"] != "coach":
        raise HTTPException(status_code=403, detail="仅教练可访问")

    result = await db.execute(
        select(Coach).where(Coach.user_id == current_user["user_id"])
    )
    coach = result.scalar_one_or_none()
    if not coach:
        raise HTTPException(status_code=404, detail="未找到教练信息")

    # 获取用户信息
    user = await db.get(User, current_user["user_id"])

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
    return {
        "id": coach.id,
        "user_id": coach.user_id,
        "coach_no": coach.coach_no,
        "name": coach.name,
        "phone": user.phone if user else None,
        "avatar": coach.avatar or (user.avatar if user else None),
        "specialty": coach.specialty.split(",") if coach.specialty else [],
        "introduction": coach.introduction,
        "certification": json.loads(coach.certification) if coach.certification else [],
        "certificates": json.loads(coach.certificates) if coach.certificates else [],
        "years_of_experience": coach.years_of_experience,
        "hourly_rate": float(coach.hourly_rate) if coach.hourly_rate else None,
        "commission_rate": float(coach.commission_rate) if coach.commission_rate else None,
        "status": coach.status,
        "total_students": total_students,
        "total_lessons": total_lessons,
        "avg_rating": round(avg_rating, 1),
        "review_count": review_count,
        "created_at": coach.created_at
    }


@router.put("/me/profile")
async def update_my_profile(
    data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """更新教练个人资料"""
    if current_user["role"] != "coach":
        raise HTTPException(status_code=403, detail="仅教练可访问")

    result = await db.execute(
        select(Coach).where(Coach.user_id == current_user["user_id"])
    )
    coach = result.scalar_one_or_none()
    if not coach:
        raise HTTPException(status_code=404, detail="未找到教练信息")

    # 可更新的字段
    import json
    if "name" in data:
        coach.name = data["name"]
    if "avatar" in data:
        coach.avatar = data["avatar"]
    if "specialty" in data:
        coach.specialty = ",".join(data["specialty"]) if isinstance(data["specialty"], list) else data["specialty"]
    if "introduction" in data:
        coach.introduction = data["introduction"]
    if "certification" in data:
        coach.certification = json.dumps(data["certification"]) if isinstance(data["certification"], list) else data["certification"]
    if "years_of_experience" in data:
        coach.years_of_experience = data["years_of_experience"]

    await db.commit()
    await db.refresh(coach)

    return {"message": "更新成功"}


# ==================== 教练收入管理 ====================

@router.get("/me/income/summary")
async def get_income_summary(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """获取收入汇总"""
    if current_user["role"] != "coach":
        raise HTTPException(status_code=403, detail="仅教练可访问")

    result = await db.execute(
        select(Coach).where(Coach.user_id == current_user["user_id"])
    )
    coach = result.scalar_one_or_none()
    if not coach:
        raise HTTPException(status_code=404, detail="未找到教练信息")

    from datetime import datetime
    today = date.today()
    this_month_start = today.replace(day=1)
    last_month_start = (this_month_start - timedelta(days=1)).replace(day=1)

    # 本月完成课程数
    this_month_lessons = await db.execute(
        select(func.count()).where(
            Booking.coach_id == coach.id,
            Booking.status == BookingStatus.COMPLETED.value,
            Booking.booking_date >= this_month_start
        )
    )
    this_month_count = this_month_lessons.scalar() or 0

    # 上月完成课程数
    last_month_lessons = await db.execute(
        select(func.count()).where(
            Booking.coach_id == coach.id,
            Booking.status == BookingStatus.COMPLETED.value,
            Booking.booking_date >= last_month_start,
            Booking.booking_date < this_month_start
        )
    )
    last_month_count = last_month_lessons.scalar() or 0

    # 总完成课程数
    total_lessons = await db.execute(
        select(func.count()).where(
            Booking.coach_id == coach.id,
            Booking.status == BookingStatus.COMPLETED.value
        )
    )
    total_count = total_lessons.scalar() or 0

    # 计算收入 (课时费 * 课程数 * 提成比例)
    hourly_rate = float(coach.hourly_rate) if coach.hourly_rate else 0
    commission_rate = float(coach.commission_rate) if coach.commission_rate else 0.7  # 默认70%提成

    this_month_income = this_month_count * hourly_rate * commission_rate
    last_month_income = last_month_count * hourly_rate * commission_rate
    total_income = total_count * hourly_rate * commission_rate

    return {
        "this_month": {
            "lessons": this_month_count,
            "income": round(this_month_income, 2)
        },
        "last_month": {
            "lessons": last_month_count,
            "income": round(last_month_income, 2)
        },
        "total": {
            "lessons": total_count,
            "income": round(total_income, 2)
        },
        "hourly_rate": hourly_rate,
        "commission_rate": commission_rate
    }


@router.get("/me/income/details")
async def get_income_details(
    month: Optional[str] = Query(None, description="月份 YYYY-MM"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """获取收入明细"""
    if current_user["role"] != "coach":
        raise HTTPException(status_code=403, detail="仅教练可访问")

    result = await db.execute(
        select(Coach).where(Coach.user_id == current_user["user_id"])
    )
    coach = result.scalar_one_or_none()
    if not coach:
        raise HTTPException(status_code=404, detail="未找到教练信息")

    from app.models.user import Student

    # 构建查询
    query = select(Booking).where(
        Booking.coach_id == coach.id,
        Booking.status == BookingStatus.COMPLETED.value
    )

    if month:
        from datetime import datetime
        try:
            year, mon = month.split("-")
            start_date = date(int(year), int(mon), 1)
            if int(mon) == 12:
                end_date = date(int(year) + 1, 1, 1)
            else:
                end_date = date(int(year), int(mon) + 1, 1)
            query = query.where(
                Booking.booking_date >= start_date,
                Booking.booking_date < end_date
            )
        except:
            pass

    query = query.order_by(Booking.booking_date.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)

    bookings_result = await db.execute(query)
    bookings = bookings_result.scalars().all()

    hourly_rate = float(coach.hourly_rate) if coach.hourly_rate else 0
    commission_rate = float(coach.commission_rate) if coach.commission_rate else 0.7

    details = []
    for booking in bookings:
        # 获取学员信息
        student = await db.get(Student, booking.student_id)
        income = hourly_rate * commission_rate

        details.append({
            "id": booking.id,
            "booking_date": booking.booking_date.isoformat(),
            "start_time": booking.start_time.strftime("%H:%M"),
            "end_time": booking.end_time.strftime("%H:%M"),
            "student_name": student.name if student else "未知学员",
            "hourly_rate": hourly_rate,
            "commission_rate": commission_rate,
            "income": round(income, 2),
            "completed_at": booking.updated_at.isoformat() if booking.updated_at else None
        })

    return {
        "items": details,
        "page": page,
        "page_size": page_size
    }


# ==================== 教练学员管理 ====================

@router.get("/me/students")
async def get_my_students(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """获取我的学员列表"""
    if current_user["role"] != "coach":
        raise HTTPException(status_code=403, detail="仅教练可访问")

    result = await db.execute(
        select(Coach).where(Coach.user_id == current_user["user_id"])
    )
    coach = result.scalar_one_or_none()
    if not coach:
        raise HTTPException(status_code=404, detail="未找到教练信息")

    from app.models.user import Student

    # 获取有预约记录的学员
    student_ids_query = select(Booking.student_id).where(
        Booking.coach_id == coach.id
    ).distinct()

    students_query = select(Student).where(
        Student.id.in_(student_ids_query)
    ).offset((page - 1) * page_size).limit(page_size)

    students_result = await db.execute(students_query)
    students = students_result.scalars().all()

    student_list = []
    for student in students:
        # 获取该学员的课程统计
        lesson_count = await db.execute(
            select(func.count()).where(
                Booking.coach_id == coach.id,
                Booking.student_id == student.id,
                Booking.status == BookingStatus.COMPLETED.value
            )
        )
        total_lessons = lesson_count.scalar() or 0

        # 获取最近一次上课时间
        last_lesson = await db.execute(
            select(Booking.booking_date).where(
                Booking.coach_id == coach.id,
                Booking.student_id == student.id,
                Booking.status == BookingStatus.COMPLETED.value
            ).order_by(Booking.booking_date.desc()).limit(1)
        )
        last_date = last_lesson.scalar_one_or_none()

        student_list.append({
            "id": student.id,
            "student_no": student.student_no,
            "name": student.name,
            "gender": student.gender,
            "age": student.age,
            "phone": student.phone,
            "total_lessons": total_lessons,
            "last_lesson_date": last_date.isoformat() if last_date else None
        })

    return {
        "items": student_list,
        "page": page,
        "page_size": page_size
    }


@router.get("/me/students/{student_id}")
async def get_student_detail(
    student_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """获取学员详情"""
    if current_user["role"] != "coach":
        raise HTTPException(status_code=403, detail="仅教练可访问")

    result = await db.execute(
        select(Coach).where(Coach.user_id == current_user["user_id"])
    )
    coach = result.scalar_one_or_none()
    if not coach:
        raise HTTPException(status_code=404, detail="未找到教练信息")

    from app.models.user import Student

    student = await db.get(Student, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="学员不存在")

    # 获取课程统计
    lesson_count = await db.execute(
        select(func.count()).where(
            Booking.coach_id == coach.id,
            Booking.student_id == student.id,
            Booking.status == BookingStatus.COMPLETED.value
        )
    )
    total_lessons = lesson_count.scalar() or 0

    # 获取最近课程记录
    recent_lessons = await db.execute(
        select(Booking).where(
            Booking.coach_id == coach.id,
            Booking.student_id == student.id
        ).order_by(Booking.booking_date.desc()).limit(10)
    )
    lessons = recent_lessons.scalars().all()

    return {
        "id": student.id,
        "student_no": student.student_no,
        "name": student.name,
        "gender": student.gender,
        "age": student.age,
        "birth_date": student.birth_date.isoformat() if student.birth_date else None,
        "phone": student.phone,
        "height": float(student.height) if student.height else None,
        "weight": float(student.weight) if student.weight else None,
        "school": student.school,
        "grade": student.grade,
        "total_lessons": total_lessons,
        "recent_lessons": [
            {
                "id": l.id,
                "booking_date": l.booking_date.isoformat(),
                "start_time": l.start_time.strftime("%H:%M"),
                "end_time": l.end_time.strftime("%H:%M"),
                "status": l.status
            }
            for l in lessons
        ]
    }


# ==================== 教练课表管理 ====================

@router.get("/me/schedule")
async def get_my_schedule(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    status: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """获取我的课表"""
    if current_user["role"] != "coach":
        raise HTTPException(status_code=403, detail="仅教练可访问")

    result = await db.execute(
        select(Coach).where(Coach.user_id == current_user["user_id"])
    )
    coach = result.scalar_one_or_none()
    if not coach:
        raise HTTPException(status_code=404, detail="未找到教练信息")

    from app.models.user import Student

    if not start_date:
        start_date = date.today()
    if not end_date:
        end_date = start_date + timedelta(days=7)

    query = select(Booking).where(
        Booking.coach_id == coach.id,
        Booking.booking_date >= start_date,
        Booking.booking_date <= end_date
    )

    if status:
        query = query.where(Booking.status == status)

    query = query.order_by(Booking.booking_date, Booking.start_time)
    bookings_result = await db.execute(query)
    bookings = bookings_result.scalars().all()

    schedule = []
    for booking in bookings:
        student = await db.get(Student, booking.student_id)
        schedule.append({
            "id": booking.id,
            "booking_date": booking.booking_date.isoformat(),
            "start_time": booking.start_time.strftime("%H:%M"),
            "end_time": booking.end_time.strftime("%H:%M"),
            "status": booking.status,
            "student_id": booking.student_id,
            "student_name": student.name if student else "未知学员",
            "notes": booking.notes,
            "created_at": booking.created_at.isoformat()
        })

    return {
        "items": schedule,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat()
    }


@router.put("/me/bookings/{booking_id}/confirm")
async def confirm_booking(
    booking_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """确认预约"""
    if current_user["role"] != "coach":
        raise HTTPException(status_code=403, detail="仅教练可访问")

    result = await db.execute(
        select(Coach).where(Coach.user_id == current_user["user_id"])
    )
    coach = result.scalar_one_or_none()
    if not coach:
        raise HTTPException(status_code=404, detail="未找到教练信息")

    booking = await db.get(Booking, booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="预约不存在")

    if booking.coach_id != coach.id:
        raise HTTPException(status_code=403, detail="无权操作此预约")

    if booking.status != BookingStatus.PENDING.value:
        raise HTTPException(status_code=400, detail="只能确认待确认的预约")

    booking.status = BookingStatus.CONFIRMED.value
    await db.commit()

    return {"message": "预约已确认"}


@router.put("/me/bookings/{booking_id}/complete")
async def complete_booking(
    booking_id: int,
    notes: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """完成课程"""
    if current_user["role"] != "coach":
        raise HTTPException(status_code=403, detail="仅教练可访问")

    result = await db.execute(
        select(Coach).where(Coach.user_id == current_user["user_id"])
    )
    coach = result.scalar_one_or_none()
    if not coach:
        raise HTTPException(status_code=404, detail="未找到教练信息")

    booking = await db.get(Booking, booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="预约不存在")

    if booking.coach_id != coach.id:
        raise HTTPException(status_code=403, detail="无权操作此预约")

    if booking.status != BookingStatus.CONFIRMED.value:
        raise HTTPException(status_code=400, detail="只能完成已确认的预约")

    booking.status = BookingStatus.COMPLETED.value
    if notes:
        booking.notes = notes
    await db.commit()

    return {"message": "课程已完成"}


@router.put("/me/bookings/{booking_id}/no-show")
async def mark_no_show(
    booking_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """标记学员缺席"""
    if current_user["role"] != "coach":
        raise HTTPException(status_code=403, detail="仅教练可访问")

    result = await db.execute(
        select(Coach).where(Coach.user_id == current_user["user_id"])
    )
    coach = result.scalar_one_or_none()
    if not coach:
        raise HTTPException(status_code=404, detail="未找到教练信息")

    booking = await db.get(Booking, booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="预约不存在")

    if booking.coach_id != coach.id:
        raise HTTPException(status_code=403, detail="无权操作此预约")

    if booking.status != BookingStatus.CONFIRMED.value:
        raise HTTPException(status_code=400, detail="只能标记已确认的预约为缺席")

    booking.status = BookingStatus.NO_SHOW.value
    await db.commit()

    return {"message": "已标记为缺席"}
