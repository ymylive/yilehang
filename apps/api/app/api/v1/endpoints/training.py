"""
训练相关API
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import get_current_user, get_db
from app.models import Coach, ParentStudentRelation, Student, TrainingSession
from app.schemas import TrainingSessionCreate, TrainingSessionResponse

router = APIRouter()


async def _get_permitted_student_ids(db: AsyncSession, current_user: dict[str, object]) -> set[int]:
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


# 支持的运动类型
EXERCISE_TYPES = [
    {
        "id": "squat",
        "name": "深蹲",
        "description": "标准深蹲动作",
        "calories_per_rep": 0.32,
        "difficulty": "normal",
    },
    {
        "id": "jumping_jack",
        "name": "开合跳",
        "description": "全身有氧运动",
        "calories_per_rep": 0.2,
        "difficulty": "easy",
    },
    {
        "id": "high_knees",
        "name": "高抬腿",
        "description": "原地高抬腿跑",
        "calories_per_rep": 0.15,
        "difficulty": "normal",
    },
    {
        "id": "pushup",
        "name": "俯卧撑",
        "description": "标准俯卧撑",
        "calories_per_rep": 0.5,
        "difficulty": "hard",
    },
    {
        "id": "jump_rope",
        "name": "跳绳",
        "description": "模拟跳绳动作",
        "calories_per_rep": 0.1,
        "difficulty": "normal",
    },
    {
        "id": "lunge",
        "name": "弓步蹲",
        "description": "交替弓步蹲",
        "calories_per_rep": 0.35,
        "difficulty": "normal",
    },
    {
        "id": "plank",
        "name": "平板支撑",
        "description": "核心力量训练",
        "calories_per_rep": 0.05,  # 每秒
        "difficulty": "hard",
    },
]


@router.get("/exercises")
async def list_exercises():
    """获取支持的运动类型列表"""
    return EXERCISE_TYPES


@router.post("/start")
async def start_training(
    exercise_type: str,
    student_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict[str, object] = Depends(get_current_user),
):
    """开始训练会话"""
    await _ensure_student_access(student_id, db, current_user)

    # 验证运动类型
    exercise = next((e for e in EXERCISE_TYPES if e["id"] == exercise_type), None)
    if not exercise:
        raise HTTPException(status_code=400, detail="不支持的运动类型")

    return {
        "message": "训练开始",
        "exercise": exercise,
        "student_id": student_id,
        "tips": ["请确保摄像头能够拍摄到全身", "保持适当距离，约2-3米", "确保光线充足"],
    }


@router.post("/complete", response_model=TrainingSessionResponse)
async def complete_training(
    session_data: TrainingSessionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict[str, object] = Depends(get_current_user),
):
    """完成训练并保存记录"""
    await _ensure_student_access(session_data.student_id, db, current_user)

    # 计算卡路里消耗
    exercise = next((e for e in EXERCISE_TYPES if e["id"] == session_data.exercise_type), None)
    calories = 0
    if exercise:
        calories = session_data.reps_count * exercise["calories_per_rep"]

    session = TrainingSession(
        student_id=session_data.student_id,
        exercise_type=session_data.exercise_type,
        duration=session_data.duration,
        reps_count=session_data.reps_count,
        accuracy_score=session_data.accuracy_score,
        calories_burned=calories,
        video_url=session_data.video_url,
    )
    db.add(session)
    await db.flush()
    await db.refresh(session)

    return TrainingSessionResponse.model_validate(session)


@router.get("/history", response_model=List[TrainingSessionResponse])
async def get_training_history(
    student_id: int,
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: dict[str, object] = Depends(get_current_user),
):
    """获取训练历史"""
    await _ensure_student_access(student_id, db, current_user)

    result = await db.execute(
        select(TrainingSession)
        .where(TrainingSession.student_id == student_id)
        .order_by(TrainingSession.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    sessions = result.scalars().all()
    return [TrainingSessionResponse.model_validate(s) for s in sessions]
