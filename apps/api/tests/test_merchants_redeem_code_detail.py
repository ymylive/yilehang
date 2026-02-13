from datetime import datetime, timedelta, timezone
from typing import Any

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Student
from app.models.merchant import Merchant, MerchantUser, RedeemItem, RedeemOrder, RedeemOrderStatus


@pytest.mark.asyncio
async def test_get_order_by_verify_code_returns_enriched_order_detail(
    client: AsyncClient,
    db_session: AsyncSession,
    test_users: dict[str, Any],
    admin_token: str,
):
    merchant = Merchant(
        name="Test Merchant", category="sports", address="Test Address", status="active"
    )
    db_session.add(merchant)
    await db_session.flush()

    merchant_user = MerchantUser(
        merchant_id=merchant.id, user_id=test_users["admin"].id, role="owner"
    )
    db_session.add(merchant_user)

    item = RedeemItem(
        merchant_id=merchant.id,
        name="Test Item",
        image="https://example.com/item.png",
        energy_cost=50,
        stock=10,
        valid_days=30,
    )
    db_session.add(item)
    await db_session.flush()

    student = (
        await db_session.execute(select(Student).where(Student.user_id == test_users["student"].id))
    ).scalar_one()

    order = RedeemOrder(
        order_no="TESTORDER12345678",
        student_id=student.id,
        merchant_id=merchant.id,
        item_id=item.id,
        energy_cost=item.energy_cost,
        verify_code="VERIFY123",
        status=RedeemOrderStatus.PENDING.value,
        expire_at=datetime.now(timezone.utc) + timedelta(days=1),
    )
    db_session.add(order)
    await db_session.commit()

    response = await client.get(
        "/api/v1/merchants/redeem/code/VERIFY123",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == order.id
    assert data["verify_code"] == "VERIFY123"
    assert data["item_name"] == "Test Item"
    assert data["item_image"] == "https://example.com/item.png"
    assert data["student_name"] == student.name
