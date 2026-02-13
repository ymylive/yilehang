import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_parent_energy_summary_returns_200(client: AsyncClient, parent_token: str):
    response = await client.get(
        "/api/v1/energy/account/summary",
        headers={"Authorization": f"Bearer {parent_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "balance" in data
    assert "today_earned" in data
    assert "week_earned" in data


@pytest.mark.asyncio
async def test_coach_energy_summary_returns_400_not_500(client: AsyncClient, coach_token: str):
    response = await client.get(
        "/api/v1/energy/account/summary",
        headers={"Authorization": f"Bearer {coach_token}"},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "未找到关联的学员账户"
