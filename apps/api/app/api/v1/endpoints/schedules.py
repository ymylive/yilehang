"""
排课相关API
"""
from typing import List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.core import get_db, get_current_user
from app.models import Schedule, Attendance, Course
from app.schemas import (
    ScheduleCreate, ScheduleUpdate, ScheduleResponse,
    AttendanceCreate, CheckInRequest, AttendanceResponse
)

router = APIRouter()


@router.get("/", response_model=List[ScheduleResponse])
async def list_schedules(
    start_date: datetime = None,
    end_date: datetime = None,
    coach_id: int = None,
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """获取排课列表"""
    query = select(Schedule).join(Course)

    filters = []
    if start_date:
        filters.append(Schedule.start_time >= start_date)
    if end_date:
        filters.append(Schedule.end_time <= end_date)
    if coach_id:
        filters.append(Schedule.coach_id == coach_id)

    if filters:
        query = query.where(and_(*filters))

    query = query.order_by(Schedule.start_time).offset(skip).limit(limit)

    result = await db.execute(query)
    schedules = result.scalars().all()
    return [ScheduleResponse.model_validate(s) for s in schedules]


@router.post("/", response_model=ScheduleResponse)
async def create_schedule(
    schedule_data: ScheduleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """创建排课"""
    schedule = Schedule(**schedule_data.model_dump())
    db.add(schedule)
    await db.flush()
    await db.refresh(schedule)
    return ScheduleResponse.model_validate(schedule)


@router.get("/{schedule_id}", response_model=ScheduleResponse)
async def get_schedule(
    schedule_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """获取排课详情"""
    result = await db.execute(select(Schedule).where(Schedule.id == schedule_id))
    schedule = result.scalar_one_or_none()
    if not schedule:
        raise HTTPException(status_code=404, detail="排课不存在")
    return ScheduleResponse.model_validate(schedule)


@router.put("/{schedule_id}", response_model=ScheduleResponse)
async def update_schedule(
    schedule_id: int,
    schedule_data: ScheduleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """更新排课"""
    result = await db.execute(select(Schedule).where(Schedule.id == schedule_id))
    schedule = result.scalar_one_or_none()
    if not schedule:
        raise HTTPException(status_code=404, detail="排课不存在")

    for key, value in schedule_data.model_dump(exclude_unset=True).items():
        setattr(schedule, key, value)

    await db.flush()
    await db.refresh(schedule)
    return ScheduleResponse.model_validate(schedule)


@router.post("/{schedule_id}/enroll", response_model=AttendanceResponse)
async def enroll_schedule(
    schedule_id: int,
    attendance_data: AttendanceCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """报名课程"""
    # 检查排课是否存在
    result = await db.execute(select(Schedule).where(Schedule.id == schedule_id))
    schedule = result.scalar_one_or_none()
    if not schedule:
        raise HTTPException(status_code=404, detail="排课不存在")

    # 检查是否已满
    if schedule.enrolled_count >= schedule.capacity:
        raise HTTPException(status_code=400, detail="课程已满")

    # 检查是否已报名
    result = await db.execute(
        select(Attendance).where(
            and_(
                Attendance.schedule_id == schedule_id,
                Attendance.student_id == attendance_data.student_id
            )
        )
    )
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="已报名该课程")

    # 创建考勤记录
    attendance = Attendance(
        schedule_id=schedule_id,
        student_id=attendance_data.student_id,
        status="enrolled"
    )
    db.add(attendance)

    # 更新报名人数
    schedule.enrolled_count += 1

    await db.flush()
    await db.refresh(attendance)
    return AttendanceResponse.model_validate(attendance)


@router.post("/{schedule_id}/checkin", response_model=AttendanceResponse)
async def checkin_schedule(
    schedule_id: int,
    checkin_data: CheckInRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """签到"""
    # 查找考勤记录
    result = await db.execute(
        select(Attendance).where(
            and_(
                Attendance.schedule_id == schedule_id,
                Attendance.student_id == checkin_data.student_id
            )
        )
    )
    attendance = result.scalar_one_or_none()
    if not attendance:
        raise HTTPException(status_code=404, detail="未报名该课程")

    if attendance.status == "checked_in":
        raise HTTPException(status_code=400, detail="已签到")

    # 更新签到状态
    attendance.check_in_time = datetime.utcnow()
    attendance.check_in_method = checkin_data.check_in_method
    attendance.status = "checked_in"

    await db.flush()
    await db.refresh(attendance)
    return AttendanceResponse.model_validate(attendance)


@router.get("/{schedule_id}/attendances", response_model=List[AttendanceResponse])
async def list_attendances(
    schedule_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """获取课程考勤列表"""
    result = await db.execute(
        select(Attendance).where(Attendance.schedule_id == schedule_id)
    )
    attendances = result.scalars().all()
    return [AttendanceResponse.model_validate(a) for a in attendances]
