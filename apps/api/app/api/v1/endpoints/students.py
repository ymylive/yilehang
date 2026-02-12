"""
学员相关API
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import get_current_user, get_db
from app.models import Coach, FitnessTest, ParentStudentRelation, Student, TrainingSession
from app.schemas import (
    GrowthProfile,
    RadarChartData,
    StudentCreate,
    StudentResponse,
    StudentUpdate,
)

router = APIRouter()


async def _get_permitted_student_ids(
    db: AsyncSession, current_user: dict[str, object]
) -> set[int]:
    role = current_user.get("role")
    user_id = current_user.get("user_id")
    if not user_id:
        return set()

    if role == "student":
        result = await db.execute(select(Student.id).where(Student.user_id == user_id))
        return set(result.scalars().all())

    if role == "parent":
        relation_result = await db.execute(
            select(ParentStudentRelation.student_id).where(
                ParentStudentRelation.parent_id == user_id
            )
        )
        direct_result = await db.execute(select(Student.id).where(Student.parent_id == user_id))
        return set(relation_result.scalars().all()) | set(direct_result.scalars().all())

    if role == "coach":
        coach_result = await db.execute(select(Coach.id).where(Coach.user_id == user_id).limit(1))
        coach_id = coach_result.scalar_one_or_none()
        if not coach_id:
            return set()
        result = await db.execute(select(Student.id).where(Student.coach_id == coach_id))
        return set(result.scalars().all())

    return set()


async def _ensure_student_access(
    student_id: int, db: AsyncSession, current_user: dict[str, object]
) -> None:
    if current_user.get("role") == "admin":
        return

    permitted_student_ids = await _get_permitted_student_ids(db, current_user)
    if student_id not in permitted_student_ids:
        raise HTTPException(status_code=403, detail="无权访问该学员")


def generate_student_no() -> str:
    """生成学员编号"""
    import random
    import string
    return "S" + "".join(random.choices(string.digits, k=8))


@router.get("/", response_model=List[StudentResponse])
async def list_students(
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: dict[str, object] = Depends(get_current_user)
):
    """获取学员列表"""
    query = select(Student).where(Student.status == "active")

    if current_user.get("role") != "admin":
        permitted_student_ids = await _get_permitted_student_ids(db, current_user)
        if not permitted_student_ids:
            return []
        query = query.where(Student.id.in_(permitted_student_ids))

    result = await db.execute(query.offset(skip).limit(limit))
    students = result.scalars().all()
    return [StudentResponse.model_validate(s) for s in students]


@router.post("/", response_model=StudentResponse)
async def create_student(
    student_data: StudentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict[str, object] = Depends(get_current_user)
):
    """创建学员"""
    student = Student(
        student_no=generate_student_no(),
        **student_data.model_dump()
    )
    db.add(student)
    await db.flush()
    await db.refresh(student)
    return StudentResponse.model_validate(student)


@router.get("/{student_id}", response_model=StudentResponse)
async def get_student(
    student_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict[str, object] = Depends(get_current_user)
):
    """获取学员详情"""
    await _ensure_student_access(student_id, db, current_user)

    result = await db.execute(select(Student).where(Student.id == student_id))
    student = result.scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=404, detail="学员不存在")
    return StudentResponse.model_validate(student)


@router.put("/{student_id}", response_model=StudentResponse)
async def update_student(
    student_id: int,
    student_data: StudentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict[str, object] = Depends(get_current_user)
):
    """更新学员信息"""
    await _ensure_student_access(student_id, db, current_user)

    result = await db.execute(select(Student).where(Student.id == student_id))
    student = result.scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=404, detail="学员不存在")

    for key, value in student_data.model_dump(exclude_unset=True).items():
        setattr(student, key, value)

    await db.flush()
    await db.refresh(student)
    return StudentResponse.model_validate(student)


@router.get("/{student_id}/growth", response_model=GrowthProfile)
async def get_student_growth(
    student_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict[str, object] = Depends(get_current_user)
):
    """获取学员成长档案(雷达图数据)"""
    await _ensure_student_access(student_id, db, current_user)

    # 获取学员信息
    result = await db.execute(select(Student).where(Student.id == student_id))
    student = result.scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=404, detail="学员不存在")

    # 获取最新体测记录
    result = await db.execute(
        select(FitnessTest)
        .where(FitnessTest.student_id == student_id)
        .order_by(FitnessTest.test_date.desc())
        .limit(2)
    )
    tests = result.scalars().all()

    # 计算雷达图数据
    current_radar = RadarChartData()
    previous_radar = None

    if tests:
        # 从最新体测计算五维数据
        latest_test = tests[0]
        for metric in latest_test.metrics:
            if metric.metric_type == "speed":
                current_radar.speed = float(metric.score or 0)
            elif metric.metric_type == "agility":
                current_radar.agility = float(metric.score or 0)
            elif metric.metric_type == "endurance":
                current_radar.endurance = float(metric.score or 0)
            elif metric.metric_type == "strength":
                current_radar.strength = float(metric.score or 0)
            elif metric.metric_type == "flexibility":
                current_radar.flexibility = float(metric.score or 0)

        if len(tests) > 1:
            previous_radar = RadarChartData()
            prev_test = tests[1]
            for metric in prev_test.metrics:
                if metric.metric_type == "speed":
                    previous_radar.speed = float(metric.score or 0)
                elif metric.metric_type == "agility":
                    previous_radar.agility = float(metric.score or 0)
                elif metric.metric_type == "endurance":
                    previous_radar.endurance = float(metric.score or 0)
                elif metric.metric_type == "strength":
                    previous_radar.strength = float(metric.score or 0)
                elif metric.metric_type == "flexibility":
                    previous_radar.flexibility = float(metric.score or 0)

    # 统计训练数据
    result = await db.execute(
        select(
            func.sum(TrainingSession.duration).label("total_duration"),
            func.count(TrainingSession.id).label("total_sessions")
        )
        .where(TrainingSession.student_id == student_id)
    )
    training_stats = result.one()

    # 统计体测次数
    result = await db.execute(
        select(func.count(FitnessTest.id))
        .where(FitnessTest.student_id == student_id)
    )
    tests_count = result.scalar() or 0

    return GrowthProfile(
        student_id=student_id,
        student_name=student.name,
        current_radar=current_radar,
        previous_radar=previous_radar,
        total_training_hours=(training_stats.total_duration or 0) / 3600,
        total_training_sessions=training_stats.total_sessions or 0,
        fitness_tests_count=tests_count
    )
