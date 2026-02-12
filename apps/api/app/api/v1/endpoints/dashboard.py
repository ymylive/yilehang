"""Dashboard API endpoints."""

from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.booking import (
    Booking,
    BookingStatus,
    StudentMembership,
    Transaction,
    TransactionType,
)
from app.models.user import Coach, Student

router = APIRouter()


@router.get("/overview")
async def get_dashboard_overview(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Get dashboard overview metrics."""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin only")

    today = date.today()
    this_month_start = today.replace(day=1)
    last_month_start = (this_month_start - timedelta(days=1)).replace(day=1)

    stats_query = select(
        select(func.count()).select_from(Student).scalar_subquery().label("student_count"),
        select(func.count())
        .where(Student.created_at >= this_month_start)
        .scalar_subquery()
        .label("new_student_count"),
        select(func.count())
        .where(Coach.status == "active")
        .scalar_subquery()
        .label("coach_count"),
        select(func.count())
        .where(Booking.booking_date == today)
        .scalar_subquery()
        .label("today_booking_count"),
        select(func.count())
        .where(Booking.status == BookingStatus.PENDING.value)
        .scalar_subquery()
        .label("pending_count"),
        select(func.count())
        .where(
            Booking.status == BookingStatus.COMPLETED.value,
            Booking.booking_date >= this_month_start,
        )
        .scalar_subquery()
        .label("completed_count"),
        select(func.coalesce(func.sum(Transaction.amount), 0))
        .where(
            Transaction.type == TransactionType.PURCHASE.value,
            Transaction.created_at >= this_month_start,
        )
        .scalar_subquery()
        .label("income"),
        select(func.coalesce(func.sum(Transaction.amount), 0))
        .where(
            Transaction.type == TransactionType.PURCHASE.value,
            Transaction.created_at >= last_month_start,
            Transaction.created_at < this_month_start,
        )
        .scalar_subquery()
        .label("last_income"),
        select(func.count())
        .where(StudentMembership.status == "active")
        .scalar_subquery()
        .label("active_membership_count"),
    )
    stats = (await db.execute(stats_query)).one()

    student_count = stats.student_count or 0
    new_student_count = stats.new_student_count or 0
    coach_count = stats.coach_count or 0
    today_booking_count = stats.today_booking_count or 0
    pending_count = stats.pending_count or 0
    completed_count = stats.completed_count or 0
    income = stats.income or 0
    last_income = stats.last_income or 0
    active_membership_count = stats.active_membership_count or 0

    return {
        "students": {
            "total": student_count,
            "new_this_month": new_student_count,
        },
        "coaches": {
            "total": coach_count,
        },
        "bookings": {
            "today": today_booking_count,
            "pending": pending_count,
            "completed_this_month": completed_count,
        },
        "revenue": {
            "this_month": float(income),
            "last_month": float(last_income),
            "growth_rate": (
                round((float(income) - float(last_income)) / float(last_income) * 100, 1)
                if last_income
                else 0
            ),
        },
        "memberships": {
            "active": active_membership_count,
        },
    }


@router.get("/recent-bookings")
async def get_recent_bookings(
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Get recent bookings for dashboard."""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin only")

    result = await db.execute(
        select(Booking)
        .options(selectinload(Booking.student), selectinload(Booking.coach))
        .order_by(Booking.created_at.desc())
        .limit(limit)
    )
    bookings = result.scalars().all()

    return [
        {
            "id": booking.id,
            "student_name": booking.student.name if booking.student else "Unknown",
            "coach_name": booking.coach.name if booking.coach else "Unknown",
            "booking_date": booking.booking_date.isoformat(),
            "start_time": booking.start_time.strftime("%H:%M"),
            "end_time": booking.end_time.strftime("%H:%M"),
            "status": booking.status,
            "created_at": booking.created_at.isoformat(),
        }
        for booking in bookings
    ]


@router.get("/booking-stats")
async def get_booking_stats(
    days: int = 7,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Get booking counts grouped by day."""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin only")

    today = date.today()
    start_date = today - timedelta(days=days - 1)

    result = await db.execute(
        select(
            Booking.booking_date,
            func.count().label("total"),
            func.sum(case((Booking.status == BookingStatus.COMPLETED.value, 1), else_=0)).label(
                "completed"
            ),
        )
        .where(Booking.booking_date.between(start_date, today))
        .group_by(Booking.booking_date)
    )

    stats_dict = {
        row.booking_date: {"total": row.total, "completed": row.completed or 0}
        for row in result
    }

    return [
        {
            "date": (start_date + timedelta(days=i)).isoformat(),
            "total": stats_dict.get(start_date + timedelta(days=i), {}).get("total", 0),
            "completed": stats_dict.get(start_date + timedelta(days=i), {}).get("completed", 0),
        }
        for i in range(days)
    ]


@router.get("/revenue-stats")
async def get_revenue_stats(
    months: int = 6,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Get monthly revenue stats."""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin only")

    today = date.today()
    month_dates = []
    for i in range(months - 1, -1, -1):
        month_date = today.replace(day=1)
        for _ in range(i):
            month_date = (month_date - timedelta(days=1)).replace(day=1)
        month_dates.append(month_date)

    if not month_dates:
        return []

    last_month = month_dates[-1]
    if last_month.month == 12:
        range_end = last_month.replace(year=last_month.year + 1, month=1)
    else:
        range_end = last_month.replace(month=last_month.month + 1)

    year_expr = func.extract("year", Transaction.created_at)
    month_expr = func.extract("month", Transaction.created_at)
    revenue_result = await db.execute(
        select(
            year_expr.label("year"),
            month_expr.label("month"),
            func.sum(Transaction.amount).label("revenue"),
        )
        .where(
            Transaction.type == TransactionType.PURCHASE.value,
            Transaction.created_at >= month_dates[0],
            Transaction.created_at < range_end,
        )
        .group_by(year_expr, month_expr)
    )

    revenue_map = {
        (int(year), int(month)): float(revenue or 0)
        for year, month, revenue in revenue_result.all()
    }

    return [
        {
            "month": month_date.strftime("%Y-%m"),
            "revenue": revenue_map.get((month_date.year, month_date.month), 0.0),
        }
        for month_date in month_dates
    ]
