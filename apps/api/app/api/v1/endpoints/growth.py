"""
成长档案相关API
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import get_current_user, get_db
from app.models import Coach, FitnessMetric, FitnessTest, ParentStudentRelation, Student
from app.schemas import FitnessTestCreate, FitnessTestResponse

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
        raise HTTPException(status_code=403, detail="无权访问该学员数据")


@router.post("/fitness-test", response_model=FitnessTestResponse)
async def create_fitness_test(
    test_data: FitnessTestCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict[str, object] = Depends(get_current_user)
):
    """创建体测记录"""
    await _ensure_student_access(test_data.student_id, db, current_user)

    # 计算BMI
    bmi = None
    if test_data.height and test_data.weight:
        height_m = test_data.height / 100
        bmi = round(test_data.weight / (height_m * height_m), 2)

    # 创建体测记录
    test = FitnessTest(
        student_id=test_data.student_id,
        test_date=test_data.test_date,
        tester_id=test_data.tester_id,
        height=test_data.height,
        weight=test_data.weight,
        bmi=bmi,
        notes=test_data.notes
    )
    db.add(test)
    await db.flush()

    # 创建体测指标
    for metric_data in test_data.metrics:
        metric = FitnessMetric(
            test_id=test.id,
            **metric_data.model_dump()
        )
        db.add(metric)

    await db.flush()
    await db.refresh(test)

    return FitnessTestResponse.model_validate(test)


@router.get("/fitness-test/{student_id}", response_model=List[FitnessTestResponse])
async def get_fitness_history(
    student_id: int,
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
    current_user: dict[str, object] = Depends(get_current_user)
):
    """获取学员体测历史"""
    await _ensure_student_access(student_id, db, current_user)

    result = await db.execute(
        select(FitnessTest)
        .where(FitnessTest.student_id == student_id)
        .order_by(FitnessTest.test_date.desc())
        .offset(skip)
        .limit(limit)
    )
    tests = result.scalars().all()
    return [FitnessTestResponse.model_validate(t) for t in tests]


@router.get("/fitness-test/{student_id}/latest", response_model=FitnessTestResponse)
async def get_latest_fitness_test(
    student_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict[str, object] = Depends(get_current_user)
):
    """获取学员最新体测记录"""
    await _ensure_student_access(student_id, db, current_user)

    result = await db.execute(
        select(FitnessTest)
        .where(FitnessTest.student_id == student_id)
        .order_by(FitnessTest.test_date.desc())
        .limit(1)
    )
    test = result.scalar_one_or_none()
    if not test:
        raise HTTPException(status_code=404, detail="暂无体测记录")
    return FitnessTestResponse.model_validate(test)
