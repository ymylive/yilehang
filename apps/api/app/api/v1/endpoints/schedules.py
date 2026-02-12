"""
排课相关API
"""
from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import fetch_user_from_token, get_current_user
from app.models import Attendance, Coach, Course, ParentStudentRelation, Schedule, Student
from app.schemas import (
    AttendanceCreate,
    AttendanceResponse,
    CheckInRequest,
    ScheduleCreate,
    ScheduleResponse,
    ScheduleUpdate,
)

router = APIRouter()


async def _get_permitted_student_ids(db: AsyncSession, user) -> set[int]:
    if user.role == "admin":
        return set()

    if user.role == "student":
        result = await db.execute(select(Student.id).where(Student.user_id == user.id))
        return set(result.scalars().all())

    if user.role == "parent":
        relation_result = await db.execute(
            select(ParentStudentRelation.student_id).where(
                ParentStudentRelation.parent_id == user.id
            )
        )
        direct_result = await db.execute(select(Student.id).where(Student.parent_id == user.id))
        return set(relation_result.scalars().all()) | set(direct_result.scalars().all())

    if user.role == "coach":
        coach_result = await db.execute(select(Coach.id).where(Coach.user_id == user.id).limit(1))
        coach_id = coach_result.scalar_one_or_none()
        if not coach_id:
            return set()
        result = await db.execute(select(Student.id).where(Student.coach_id == coach_id))
        return set(result.scalars().all())

    return set()


async def _ensure_student_access(student_id: int, db: AsyncSession, user) -> None:
    if user.role == "admin":
        return

    permitted_student_ids = await _get_permitted_student_ids(db, user)
    if student_id not in permitted_student_ids:
        raise HTTPException(status_code=403, detail="无权操作该学员")


@router.get("", response_model=List[ScheduleResponse])
async def list_schedules(
    start_date: datetime = None,
    end_date: datetime = None,
    coach_id: int = None,
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user_data: dict = Depends(get_current_user)
):
    """获取排课列表"""
    await fetch_user_from_token(db, current_user_data)
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


@router.post("", response_model=ScheduleResponse)
async def create_schedule(
    schedule_data: ScheduleCreate,
    db: AsyncSession = Depends(get_db),
    current_user_data: dict = Depends(get_current_user)
):
    """创建排课"""
    await fetch_user_from_token(db, current_user_data)
    schedule = Schedule(**schedule_data.model_dump())
    db.add(schedule)
    await db.flush()
    await db.refresh(schedule)
    return ScheduleResponse.model_validate(schedule)


@router.get("/{schedule_id}", response_model=ScheduleResponse)
async def get_schedule(
    schedule_id: int,
    db: AsyncSession = Depends(get_db),
    current_user_data: dict = Depends(get_current_user)
):
    """获取排课详情"""
    await fetch_user_from_token(db, current_user_data)
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
    current_user_data: dict = Depends(get_current_user)
):
    """更新排课"""
    await fetch_user_from_token(db, current_user_data)
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
    current_user_data: dict = Depends(get_current_user)
):
    """报名课程"""
    current_user = await fetch_user_from_token(db, current_user_data)

    if attendance_data.schedule_id != schedule_id:
        raise HTTPException(status_code=400, detail="请求中的 schedule_id 与路径不一致")

    await _ensure_student_access(attendance_data.student_id, db, current_user)

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
    current_user_data: dict = Depends(get_current_user)
):
    """签到"""
    current_user = await fetch_user_from_token(db, current_user_data)

    if checkin_data.schedule_id != schedule_id:
        raise HTTPException(status_code=400, detail="请求中的 schedule_id 与路径不一致")

    await _ensure_student_access(checkin_data.student_id, db, current_user)

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
    attendance.check_in_time = datetime.now(timezone.utc)
    attendance.check_in_method = checkin_data.check_in_method
    attendance.status = "checked_in"

    await db.flush()
    await db.refresh(attendance)
    return AttendanceResponse.model_validate(attendance)


@router.get("/{schedule_id}/attendances", response_model=List[AttendanceResponse])
async def list_attendances(
    schedule_id: int,
    db: AsyncSession = Depends(get_db),
    current_user_data: dict = Depends(get_current_user)
):
    """获取课程考勤列表"""
    await fetch_user_from_token(db, current_user_data)
    result = await db.execute(
        select(Attendance).where(Attendance.schedule_id == schedule_id)
    )
    attendances = result.scalars().all()
    return [AttendanceResponse.model_validate(a) for a in attendances]
