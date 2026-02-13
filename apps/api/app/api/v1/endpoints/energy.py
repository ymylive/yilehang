"""
能量系统 API
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import get_current_user, get_db
from app.models import EnergyRule, Student
from app.models.energy import ENERGY_LEVELS
from app.schemas.energy import (
    EnergyAccountResponse,
    EnergyAccountSummary,
    EnergyEarnRequest,
    EnergyEarnResponse,
    EnergyRuleResponse,
    EnergyTransactionList,
    EnergyTransactionResponse,
)
from app.services.energy_service import EnergyService

router = APIRouter()


@router.get("/account", response_model=EnergyAccountResponse)
async def get_energy_account(
    db: AsyncSession = Depends(get_db), current_user: dict = Depends(get_current_user)
):
    """获取当前用户的能量账户"""
    # 获取学员ID
    student_id = await _get_student_id(db, current_user)
    if not student_id:
        raise HTTPException(status_code=400, detail="未找到关联的学员账户")

    account_data = await EnergyService.get_account_with_level(db, student_id)
    return account_data


@router.get("/account/summary", response_model=EnergyAccountSummary)
async def get_energy_summary(
    db: AsyncSession = Depends(get_db), current_user: dict = Depends(get_current_user)
):
    """获取能量账户摘要（首页展示用）"""
    student_id = await _get_student_id(db, current_user)
    if not student_id:
        raise HTTPException(status_code=400, detail="未找到关联的学员账户")

    account = await EnergyService.get_or_create_account(db, student_id)
    level_info = ENERGY_LEVELS.get(account.level, ENERGY_LEVELS[1])

    today_earned = await EnergyService.get_today_earned(db, student_id)
    week_earned = await EnergyService.get_week_earned(db, student_id)

    return EnergyAccountSummary(
        balance=account.balance,
        level=account.level,
        level_name=level_info["name"],
        level_icon=level_info["icon"],
        today_earned=today_earned,
        week_earned=week_earned,
    )


@router.get("/transactions", response_model=EnergyTransactionList)
async def get_energy_transactions(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    type: Optional[str] = Query(None, description="交易类型: earn/spend/expire"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """获取能量交易记录"""
    student_id = await _get_student_id(db, current_user)
    if not student_id:
        raise HTTPException(status_code=400, detail="未找到关联的学员账户")

    transactions, total = await EnergyService.get_transactions(
        db, student_id, page, page_size, type
    )

    return EnergyTransactionList(
        items=[EnergyTransactionResponse.model_validate(t) for t in transactions],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/rules", response_model=list[EnergyRuleResponse])
async def get_energy_rules(
    db: AsyncSession = Depends(get_db), current_user: dict = Depends(get_current_user)
):
    """获取积分规则列表"""
    result = await db.execute(
        select(EnergyRule).where(EnergyRule.is_active.is_(True)).order_by(EnergyRule.sort_order)
    )
    rules = result.scalars().all()
    return [EnergyRuleResponse.model_validate(r) for r in rules]


@router.post("/earn", response_model=EnergyEarnResponse)
async def earn_energy(
    request: EnergyEarnRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    获取能量积分（内部调用）

    通常由其他业务模块调用，如完成训练、签到等
    """
    # 权限检查：只有管理员或系统可以调用
    if current_user.get("role") not in ["admin", "coach"]:
        raise HTTPException(status_code=403, detail="无权限执行此操作")

    success, amount, balance, message = await EnergyService.earn(
        db,
        request.student_id,
        request.rule_code,
        request.reference_type,
        request.reference_id,
        request.description,
    )

    await db.commit()

    return EnergyEarnResponse(success=success, amount=amount, balance=balance, message=message)


@router.get("/levels")
async def get_energy_levels():
    """获取能量等级配置"""
    return ENERGY_LEVELS


async def _get_student_id(db: AsyncSession, current_user: dict) -> Optional[int]:
    """获取当前用户关联的学员ID"""
    user_id = current_user.get("user_id")
    role = current_user.get("role")

    if role == "student":
        # 学员角色直接查询
        result = await db.execute(select(Student.id).where(Student.user_id == user_id))
        return result.scalar_one_or_none()
    elif role == "parent":
        # 家长角色查询第一个关联的学员
        result = await db.execute(select(Student.id).where(Student.parent_id == user_id).limit(1))
        return result.scalar_one_or_none()

    return None
