"""
管理后台仪表盘API
"""
from datetime import date, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User, Student, Coach
from app.models.booking import (
    Booking, BookingStatus, MembershipCard, StudentMembership,
    Transaction, TransactionType
)

router = APIRouter()


@router.get("/overview")
async def get_dashboard_overview(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """获取仪表盘概览数据"""
    if current_user["role"] != "admin":
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="仅管理员可访问")

    today = date.today()
    this_month_start = today.replace(day=1)
    last_month_start = (this_month_start - timedelta(days=1)).replace(day=1)

    # 学员统计
    total_students = await db.execute(select(func.count()).select_from(Student))
    student_count = total_students.scalar() or 0

    # 本月新增学员
    new_students_this_month = await db.execute(
        select(func.count()).where(
            Student.created_at >= this_month_start
        )
    )
    new_student_count = new_students_this_month.scalar() or 0

    # 教练统计
    total_coaches = await db.execute(
        select(func.count()).where(Coach.status == "active")
    )
    coach_count = total_coaches.scalar() or 0

    # 今日预约数
    today_bookings = await db.execute(
        select(func.count()).where(
            Booking.booking_date == today
        )
    )
    today_booking_count = today_bookings.scalar() or 0

    # 待确认预约
    pending_bookings = await db.execute(
        select(func.count()).where(
            Booking.status == BookingStatus.PENDING.value
        )
    )
    pending_count = pending_bookings.scalar() or 0

    # 本月完成课程数
    completed_this_month = await db.execute(
        select(func.count()).where(
            Booking.status == BookingStatus.COMPLETED.value,
            Booking.booking_date >= this_month_start
        )
    )
    completed_count = completed_this_month.scalar() or 0

    # 本月收入
    this_month_income = await db.execute(
        select(func.sum(Transaction.amount)).where(
            Transaction.type == TransactionType.PURCHASE.value,
            Transaction.created_at >= this_month_start
        )
    )
    income = this_month_income.scalar() or 0

    # 上月收入
    last_month_income = await db.execute(
        select(func.sum(Transaction.amount)).where(
            Transaction.type == TransactionType.PURCHASE.value,
            Transaction.created_at >= last_month_start,
            Transaction.created_at < this_month_start
        )
    )
    last_income = last_month_income.scalar() or 0

    # 活跃课时卡数
    active_memberships = await db.execute(
        select(func.count()).where(
            StudentMembership.status == "active"
        )
    )
    active_membership_count = active_memberships.scalar() or 0

    return {
        "students": {
            "total": student_count,
            "new_this_month": new_student_count
        },
        "coaches": {
            "total": coach_count
        },
        "bookings": {
            "today": today_booking_count,
            "pending": pending_count,
            "completed_this_month": completed_count
        },
        "revenue": {
            "this_month": float(income),
            "last_month": float(last_income),
            "growth_rate": round((float(income) - float(last_income)) / float(last_income) * 100, 1) if last_income else 0
        },
        "memberships": {
            "active": active_membership_count
        }
    }


@router.get("/recent-bookings")
async def get_recent_bookings(
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """获取最近预约"""
    if current_user["role"] != "admin":
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="仅管理员可访问")

    result = await db.execute(
        select(Booking)
        .order_by(Booking.created_at.desc())
        .limit(limit)
    )
    bookings = result.scalars().all()

    items = []
    for booking in bookings:
        student = await db.get(Student, booking.student_id)
        coach = await db.get(Coach, booking.coach_id)

        items.append({
            "id": booking.id,
            "student_name": student.name if student else "未知",
            "coach_name": coach.name if coach else "未知",
            "booking_date": booking.booking_date.isoformat(),
            "start_time": booking.start_time.strftime("%H:%M"),
            "end_time": booking.end_time.strftime("%H:%M"),
            "status": booking.status,
            "created_at": booking.created_at.isoformat()
        })

    return items


@router.get("/booking-stats")
async def get_booking_stats(
    days: int = 7,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """获取预约统计（按天）"""
    if current_user["role"] != "admin":
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="仅管理员可访问")

    today = date.today()
    start_date = today - timedelta(days=days - 1)

    stats = []
    for i in range(days):
        current_date = start_date + timedelta(days=i)

        # 当天预约数
        total = await db.execute(
            select(func.count()).where(
                Booking.booking_date == current_date
            )
        )
        total_count = total.scalar() or 0

        # 当天完成数
        completed = await db.execute(
            select(func.count()).where(
                Booking.booking_date == current_date,
                Booking.status == BookingStatus.COMPLETED.value
            )
        )
        completed_count = completed.scalar() or 0

        stats.append({
            "date": current_date.isoformat(),
            "total": total_count,
            "completed": completed_count
        })

    return stats


@router.get("/revenue-stats")
async def get_revenue_stats(
    months: int = 6,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """获取收入统计（按月）"""
    if current_user["role"] != "admin":
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="仅管理员可访问")

    today = date.today()
    stats = []

    for i in range(months - 1, -1, -1):
        # 计算月份
        month_date = today.replace(day=1)
        for _ in range(i):
            month_date = (month_date - timedelta(days=1)).replace(day=1)

        # 下个月第一天
        if month_date.month == 12:
            next_month = month_date.replace(year=month_date.year + 1, month=1)
        else:
            next_month = month_date.replace(month=month_date.month + 1)

        # 当月收入
        income = await db.execute(
            select(func.sum(Transaction.amount)).where(
                Transaction.type == TransactionType.PURCHASE.value,
                Transaction.created_at >= month_date,
                Transaction.created_at < next_month
            )
        )
        month_income = income.scalar() or 0

        stats.append({
            "month": month_date.strftime("%Y-%m"),
            "revenue": float(month_income)
        })

    return stats
