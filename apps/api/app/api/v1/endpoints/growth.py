"""
成长档案相关API
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core import get_db, get_current_user
from app.models import FitnessTest, FitnessMetric
from app.schemas import FitnessTestCreate, FitnessTestResponse

router = APIRouter()


@router.post("/fitness-test", response_model=FitnessTestResponse)
async def create_fitness_test(
    test_data: FitnessTestCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """创建体测记录"""
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
    current_user: dict = Depends(get_current_user)
):
    """获取学员体测历史"""
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
    current_user: dict = Depends(get_current_user)
):
    """获取学员最新体测记录"""
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
