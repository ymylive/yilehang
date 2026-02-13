import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_schedules_accepts_timezone_iso_datetime(
    client: AsyncClient, parent_token: str
):
    response = await client.get(
        "/api/v1/schedules?start_date=2026-02-08T16:00:00.000Z&end_date=2026-02-15T16:00:00.000Z",
        headers={"Authorization": f"Bearer {parent_token}"},
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_list_schedules_rejects_invalid_date_range(client: AsyncClient, parent_token: str):
    response = await client.get(
        "/api/v1/schedules?start_date=2026-02-15T00:00:00&end_date=2026-02-08T00:00:00",
        headers={"Authorization": f"Bearer {parent_token}"},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "结束时间必须晚于开始时间"
