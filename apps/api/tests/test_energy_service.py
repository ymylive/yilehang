from sqlalchemy import select

import pytest

from app.models.energy import EnergyAccount, EnergyRule, EnergyTransaction
from app.models.user import Student, User
from app.services.energy_service import EnergyService


async def _create_student(db_session, suffix: str = "1") -> Student:
    user = User(
        email=f"energy-{suffix}@test.com",
        phone=f"13900000{suffix.zfill(3)}",
        role="student",
        status="active",
    )
    db_session.add(user)
    await db_session.flush()

    student = Student(
        user_id=user.id,
        student_no=f"S{user.id:06d}",
        name=f"Energy Student {suffix}",
        status="active",
        is_active=True,
    )
    db_session.add(student)
    await db_session.flush()
    return student


@pytest.mark.asyncio
async def test_cas_update_rejects_version_mismatch(db_session):
    student = await _create_student(db_session, "101")
    account = EnergyAccount(student_id=student.id, balance=20, total_earned=20, level=1, version=0)
    db_session.add(account)
    await db_session.flush()

    failed = await EnergyService._cas_update_account(
        db_session,
        account_id=account.id,
        expected_version=1,
        balance_delta=5,
    )
    assert failed is None

    snapshot = await EnergyService._get_account_snapshot(db_session, student.id)
    assert snapshot is not None
    assert snapshot["balance"] == 20
    assert snapshot["version"] == 0


@pytest.mark.asyncio
async def test_earn_records_transaction_with_final_balance(db_session):
    student = await _create_student(db_session, "102")
    rule = EnergyRule(
        name="训练完成",
        code="test_energy_earn",
        source_type="training",
        points=15,
        multiplier=1,
        is_active=True,
    )
    db_session.add(rule)
    await db_session.flush()

    success, amount, balance, message = await EnergyService.earn(
        db_session,
        student_id=student.id,
        rule_code=rule.code,
        description="test earn",
    )

    assert success is True
    assert amount == 15
    assert balance == 15
    assert message == "获得 15 能量"

    account = await EnergyService.get_or_create_account(db_session, student.id)
    assert account.balance == 15
    assert account.total_earned == 15
    assert account.version == 1

    tx_result = await db_session.execute(
        select(EnergyTransaction).where(EnergyTransaction.student_id == student.id)
    )
    tx = tx_result.scalar_one()
    assert tx.balance_after == account.balance
    assert tx.amount == 15


@pytest.mark.asyncio
async def test_spend_retries_after_cas_conflict_and_keeps_consistency(db_session, monkeypatch):
    student = await _create_student(db_session, "103")
    account = EnergyAccount(student_id=student.id, balance=30, total_earned=30, level=1, version=0)
    db_session.add(account)
    await db_session.flush()

    original = EnergyService._cas_update_account
    calls = {"count": 0}

    async def flaky_cas(*args, **kwargs):
        calls["count"] += 1
        if calls["count"] == 1:
            return None
        return await original(*args, **kwargs)

    monkeypatch.setattr(EnergyService, "_cas_update_account", staticmethod(flaky_cas))

    success, amount, balance, message = await EnergyService.spend(
        db_session,
        student_id=student.id,
        amount=10,
        reference_type="redeem_order",
        reference_id=1,
        description="test spend",
    )

    assert success is True
    assert amount == 10
    assert balance == 20
    assert message == "消费 10 能量"
    assert calls["count"] >= 2

    refreshed = await EnergyService.get_or_create_account(db_session, student.id)
    assert refreshed.balance == 20
    assert refreshed.total_spent == 10
    assert refreshed.version == 1

    tx_result = await db_session.execute(
        select(EnergyTransaction).where(EnergyTransaction.student_id == student.id)
    )
    tx = tx_result.scalar_one()
    assert tx.balance_after == refreshed.balance
    assert tx.amount == -10


@pytest.mark.asyncio
async def test_refund_updates_balance_with_versioned_write(db_session):
    student = await _create_student(db_session, "104")
    account = EnergyAccount(
        student_id=student.id,
        balance=5,
        total_earned=30,
        total_spent=25,
        level=1,
        version=2,
    )
    db_session.add(account)
    await db_session.flush()

    success, amount, balance, message = await EnergyService.refund(
        db_session,
        student_id=student.id,
        amount=3,
        reference_type="redeem_order",
        reference_id=2,
        description="test refund",
    )

    assert success is True
    assert amount == 3
    assert balance == 8
    assert message == "退还 3 能量"

    refreshed = await EnergyService.get_or_create_account(db_session, student.id)
    assert refreshed.balance == 8
    assert refreshed.total_spent == 22
    assert refreshed.version == 3

    tx_result = await db_session.execute(
        select(EnergyTransaction).where(EnergyTransaction.student_id == student.id)
    )
    tx = tx_result.scalar_one()
    assert tx.balance_after == refreshed.balance
    assert tx.amount == 3
