"""
排行榜 API
"""
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc

from app.core import get_db, get_current_user
from app.models import Student
from app.models.energy import EnergyAccount, EnergyTransaction, EnergyTransactionType, ENERGY_LEVELS
from app.models.growth import TrainingSession, FitnessTest

from app.schemas.energy import LeaderboardEntry, LeaderboardResponse

router = APIRouter()


@router.get("/energy", response_model=LeaderboardResponse)
async def get_energy_leaderboard(
    period: str = Query("week", description="时间范围: week/month/all"),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """获取能量排行榜"""
    now = datetime.utcnow()

    if period == "week":
        start_time = now - timedelta(days=now.weekday())
        start_time = start_time.replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == "month":
        start_time = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    else:
        start_time = None

    # 查询排行榜
    if start_time:
        # 按时间段统计
        query = (
            select(
                EnergyTransaction.student_id,
                func.sum(EnergyTransaction.amount).label("total")
            )
            .where(
                and_(
                    EnergyTransaction.type == EnergyTransactionType.EARN.value,
                    EnergyTransaction.created_at >= start_time
                )
            )
            .group_by(EnergyTransaction.student_id)
            .order_by(desc("total"))
            .limit(limit)
        )
    else:
        # 全部时间按累计获取排序
        query = (
            select(EnergyAccount.student_id, EnergyAccount.total_earned.label("total"))
            .order_by(desc(EnergyAccount.total_earned))
            .limit(limit)
        )

    result = await db.execute(query)
    rows = result.all()

    # 获取学员信息
    entries = []
    for rank, (student_id, total) in enumerate(rows, 1):
        student_result = await db.execute(
            select(Student).where(Student.id == student_id)
        )
        student = student_result.scalar_one_or_none()

        # 获取等级
        account_result = await db.execute(
            select(EnergyAccount).where(EnergyAccount.student_id == student_id)
        )
        account = account_result.scalar_one_or_none()
        level = account.level if account else 1
        level_info = ENERGY_LEVELS.get(level, ENERGY_LEVELS[1])

        entries.append(LeaderboardEntry(
            rank=rank,
            student_id=student_id,
            student_name=student.name if student else "未知",
            avatar=None,
            value=int(total or 0),
            level=level,
            level_icon=level_info["icon"]
        ))

    # 获取当前用户排名
    my_rank = None
    my_value = None
    student_id = await _get_student_id(db, current_user)
    if student_id:
        for entry in entries:
            if entry.student_id == student_id:
                my_rank = entry.rank
                my_value = entry.value
                break

    return LeaderboardResponse(
        type="energy",
        period=period,
        items=entries,
        my_rank=my_rank,
        my_value=my_value,
        updated_at=now
    )


@router.get("/training", response_model=LeaderboardResponse)
async def get_training_leaderboard(
    period: str = Query("week", description="时间范围: week/month/all"),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """获取训练排行榜（按训练次数）"""
    now = datetime.utcnow()

    if period == "week":
        start_time = now - timedelta(days=now.weekday())
        start_time = start_time.replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == "month":
        start_time = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    else:
        start_time = datetime(2020, 1, 1)

    # 查询训练次数排行
    query = (
        select(
            TrainingSession.student_id,
            func.count(TrainingSession.id).label("total")
        )
        .where(TrainingSession.session_date >= start_time.date())
        .group_by(TrainingSession.student_id)
        .order_by(desc("total"))
        .limit(limit)
    )

    result = await db.execute(query)
    rows = result.all()

    entries = []
    for rank, (student_id, total) in enumerate(rows, 1):
        student_result = await db.execute(
            select(Student).where(Student.id == student_id)
        )
        student = student_result.scalar_one_or_none()

        entries.append(LeaderboardEntry(
            rank=rank,
            student_id=student_id,
            student_name=student.name if student else "未知",
            avatar=None,
            value=int(total or 0)
        ))

    # 获取当前用户排名
    my_rank = None
    my_value = None
    student_id = await _get_student_id(db, current_user)
    if student_id:
        for entry in entries:
            if entry.student_id == student_id:
                my_rank = entry.rank
                my_value = entry.value
                break

    return LeaderboardResponse(
        type="training",
        period=period,
        items=entries,
        my_rank=my_rank,
        my_value=my_value,
        updated_at=now
    )


@router.get("/fitness", response_model=LeaderboardResponse)
async def get_fitness_leaderboard(
    metric: str = Query("jump_rope", description="体测项目"),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """获取体测进步榜"""
    now = datetime.utcnow()

    # 这里简化处理，实际应该计算进步幅度
    # 暂时按最新体测成绩排序
    query = (
        select(FitnessTest.student_id, func.max(FitnessTest.id).label("latest_id"))
        .group_by(FitnessTest.student_id)
        .limit(limit)
    )

    result = await db.execute(query)
    rows = result.all()

    entries = []
    for rank, (student_id, _) in enumerate(rows, 1):
        student_result = await db.execute(
            select(Student).where(Student.id == student_id)
        )
        student = student_result.scalar_one_or_none()

        entries.append(LeaderboardEntry(
            rank=rank,
            student_id=student_id,
            student_name=student.name if student else "未知",
            avatar=None,
            value=0  # 实际应该是进步分数
        ))

    return LeaderboardResponse(
        type="fitness",
        period="all",
        items=entries,
        my_rank=None,
        my_value=None,
        updated_at=now
    )


async def _get_student_id(db: AsyncSession, current_user: dict) -> Optional[int]:
    """获取当前用户关联的学员ID"""
    user_id = current_user.get("user_id")
    role = current_user.get("role")

    if role == "student":
        result = await db.execute(
            select(Student.id).where(Student.user_id == user_id)
        )
        return result.scalar_one_or_none()
    elif role == "parent":
        result = await db.execute(
            select(Student.id).where(Student.parent_id == user_id).limit(1)
        )
        return result.scalar_one_or_none()

    return None
