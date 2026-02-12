"""
能量系统服务层
"""
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.energy import (
    ENERGY_LEVELS,
    EnergyAccount,
    EnergyRule,
    EnergyTransaction,
    EnergyTransactionType,
)

logger = logging.getLogger(__name__)


class EnergyService:
    """能量系统服务"""

    @staticmethod
    async def get_or_create_account(db: AsyncSession, student_id: int) -> EnergyAccount:
        """获取或创建能量账户"""
        result = await db.execute(
            select(EnergyAccount).where(EnergyAccount.student_id == student_id)
        )
        account = result.scalar_one_or_none()

        if not account:
            account = EnergyAccount(student_id=student_id, balance=0, level=1)
            db.add(account)
            await db.flush()

        return account

    @staticmethod
    async def get_account_with_level(db: AsyncSession, student_id: int) -> dict:
        """获取账户信息（含等级详情）"""
        account = await EnergyService.get_or_create_account(db, student_id)

        level_info = ENERGY_LEVELS.get(account.level, ENERGY_LEVELS[1])
        next_level = account.level + 1
        next_level_info = ENERGY_LEVELS.get(next_level)

        return {
            "id": account.id,
            "student_id": account.student_id,
            "balance": account.balance,
            "total_earned": account.total_earned,
            "total_spent": account.total_spent,
            "level": account.level,
            "level_name": level_info["name"],
            "level_icon": level_info["icon"],
            "next_level_points": next_level_info["min_points"] if next_level_info else None,
            "created_at": account.created_at,
            "updated_at": account.updated_at,
        }

    @staticmethod
    async def get_rule_by_code(db: AsyncSession, code: str) -> Optional[EnergyRule]:
        """根据代码获取积分规则"""
        result = await db.execute(
            select(EnergyRule).where(
                and_(EnergyRule.code == code, EnergyRule.is_active.is_(True))
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def check_limit(
        db: AsyncSession,
        student_id: int,
        rule: EnergyRule
    ) -> Tuple[bool, str]:
        """检查积分获取限制"""
        now = datetime.now(timezone.utc)

        # 检查每日限制
        if rule.daily_limit:
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            result = await db.execute(
                select(func.sum(EnergyTransaction.amount)).where(
                    and_(
                        EnergyTransaction.student_id == student_id,
                        EnergyTransaction.rule_id == rule.id,
                        EnergyTransaction.type == EnergyTransactionType.EARN.value,
                        EnergyTransaction.created_at >= today_start
                    )
                )
            )
            today_earned = result.scalar() or 0
            if today_earned >= rule.daily_limit:
                return False, f"今日已达上限 {rule.daily_limit} 能量"

        # 检查每周限制
        if rule.weekly_limit:
            week_start = now - timedelta(days=now.weekday())
            week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
            result = await db.execute(
                select(func.sum(EnergyTransaction.amount)).where(
                    and_(
                        EnergyTransaction.student_id == student_id,
                        EnergyTransaction.rule_id == rule.id,
                        EnergyTransaction.type == EnergyTransactionType.EARN.value,
                        EnergyTransaction.created_at >= week_start
                    )
                )
            )
            week_earned = result.scalar() or 0
            if week_earned >= rule.weekly_limit:
                return False, f"本周已达上限 {rule.weekly_limit} 能量"

        # 检查每月限制
        if rule.monthly_limit:
            month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            result = await db.execute(
                select(func.sum(EnergyTransaction.amount)).where(
                    and_(
                        EnergyTransaction.student_id == student_id,
                        EnergyTransaction.rule_id == rule.id,
                        EnergyTransaction.type == EnergyTransactionType.EARN.value,
                        EnergyTransaction.created_at >= month_start
                    )
                )
            )
            month_earned = result.scalar() or 0
            if month_earned >= rule.monthly_limit:
                return False, f"本月已达上限 {rule.monthly_limit} 能量"

        return True, ""

    @staticmethod
    async def earn(
        db: AsyncSession,
        student_id: int,
        rule_code: str,
        reference_type: Optional[str] = None,
        reference_id: Optional[int] = None,
        description: Optional[str] = None
    ) -> Tuple[bool, int, int, str]:
        """
        获取能量积分

        Returns:
            (success, amount, balance, message)
        """
        # 获取规则
        rule = await EnergyService.get_rule_by_code(db, rule_code)
        if not rule:
            return False, 0, 0, f"积分规则 {rule_code} 不存在"

        # 检查限制
        can_earn, limit_msg = await EnergyService.check_limit(db, student_id, rule)
        if not can_earn:
            return False, 0, 0, limit_msg

        # 获取账户
        account = await EnergyService.get_or_create_account(db, student_id)

        # 计算积分
        amount = int(rule.points * float(rule.multiplier))

        # 乐观锁更新
        account.balance += amount
        account.total_earned += amount
        account.version += 1

        # 更新等级
        new_level = EnergyService.calculate_level(account.total_earned)
        if new_level > account.level:
            account.level = new_level

        # 创建交易记录
        transaction = EnergyTransaction(
            account_id=account.id,
            student_id=student_id,
            type=EnergyTransactionType.EARN.value,
            source_type=rule.source_type,
            amount=amount,
            balance_after=account.balance,
            rule_id=rule.id,
            reference_type=reference_type,
            reference_id=reference_id,
            description=description or rule.name
        )
        db.add(transaction)

        await db.flush()

        logger.info(f"Student {student_id} earned {amount} energy via {rule_code}")
        return True, amount, account.balance, f"获得 {amount} 能量"

    @staticmethod
    async def spend(
        db: AsyncSession,
        student_id: int,
        amount: int,
        reference_type: str,
        reference_id: int,
        description: Optional[str] = None
    ) -> Tuple[bool, int, int, str]:
        """
        消费能量积分

        Returns:
            (success, amount, balance, message)
        """
        account = await EnergyService.get_or_create_account(db, student_id)

        if account.balance < amount:
            return False, 0, account.balance, f"能量不足，当前余额 {account.balance}"

        # 乐观锁更新
        account.balance -= amount
        account.total_spent += amount
        account.version += 1

        # 创建交易记录
        transaction = EnergyTransaction(
            account_id=account.id,
            student_id=student_id,
            type=EnergyTransactionType.SPEND.value,
            amount=-amount,
            balance_after=account.balance,
            reference_type=reference_type,
            reference_id=reference_id,
            description=description or "能量消费"
        )
        db.add(transaction)

        await db.flush()

        logger.info(
            f"Student {student_id} spent {amount} energy "
            f"for {reference_type}:{reference_id}"
        )
        return True, amount, account.balance, f"消费 {amount} 能量"

    @staticmethod
    async def refund(
        db: AsyncSession,
        student_id: int,
        amount: int,
        reference_type: str,
        reference_id: int,
        description: Optional[str] = None
    ) -> Tuple[bool, int, int, str]:
        """退还能量积分"""
        account = await EnergyService.get_or_create_account(db, student_id)

        account.balance += amount
        account.total_spent -= amount
        account.version += 1

        transaction = EnergyTransaction(
            account_id=account.id,
            student_id=student_id,
            type=EnergyTransactionType.REFUND.value,
            amount=amount,
            balance_after=account.balance,
            reference_type=reference_type,
            reference_id=reference_id,
            description=description or "能量退还"
        )
        db.add(transaction)

        await db.flush()

        return True, amount, account.balance, f"退还 {amount} 能量"

    @staticmethod
    def calculate_level(total_earned: int) -> int:
        """根据累计获取计算等级"""
        level = 1
        for lvl, info in sorted(ENERGY_LEVELS.items(), reverse=True):
            if total_earned >= info["min_points"]:
                level = lvl
                break
        return level

    @staticmethod
    async def get_transactions(
        db: AsyncSession,
        student_id: int,
        page: int = 1,
        page_size: int = 20,
        type_filter: Optional[str] = None
    ) -> Tuple[list, int]:
        """获取交易记录"""
        query = select(EnergyTransaction).where(
            EnergyTransaction.student_id == student_id
        )

        if type_filter:
            query = query.where(EnergyTransaction.type == type_filter)

        # 总数
        count_query = select(func.count()).select_from(query.subquery())
        total = (await db.execute(count_query)).scalar() or 0

        # 分页
        query = query.order_by(EnergyTransaction.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await db.execute(query)
        transactions = result.scalars().all()

        return list(transactions), total

    @staticmethod
    async def get_today_earned(db: AsyncSession, student_id: int) -> int:
        """获取今日获取的能量"""
        today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        result = await db.execute(
            select(func.sum(EnergyTransaction.amount)).where(
                and_(
                    EnergyTransaction.student_id == student_id,
                    EnergyTransaction.type == EnergyTransactionType.EARN.value,
                    EnergyTransaction.created_at >= today_start
                )
            )
        )
        return result.scalar() or 0

    @staticmethod
    async def get_week_earned(db: AsyncSession, student_id: int) -> int:
        """获取本周获取的能量"""
        now = datetime.now(timezone.utc)
        week_start = now - timedelta(days=now.weekday())
        week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
        result = await db.execute(
            select(func.sum(EnergyTransaction.amount)).where(
                and_(
                    EnergyTransaction.student_id == student_id,
                    EnergyTransaction.type == EnergyTransactionType.EARN.value,
                    EnergyTransaction.created_at >= week_start
                )
            )
        )
        return result.scalar() or 0
