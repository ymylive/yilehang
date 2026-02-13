import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_coach_students_supports_page_size_200(client: AsyncClient, coach_token: str):
    resp = await client.get(
        "/api/v1/coaches/me/students?page=1&page_size=200",
        headers={"Authorization": f"Bearer {coach_token}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["page"] == 1
    assert data["page_size"] == 200


@pytest.mark.asyncio
async def test_coach_can_create_and_list_slots(client: AsyncClient, coach_token: str):
    create_resp = await client.post(
        "/api/v1/coaches/me/slots",
        json={
            "day_of_week": 1,
            "start_time": "09:00:00",
            "end_time": "10:00:00",
            "slot_duration": 60,
            "max_students": 1,
        },
        headers={"Authorization": f"Bearer {coach_token}"},
    )
    assert create_resp.status_code == 200
    created = create_resp.json()
    assert created["day_of_week"] == 1

    list_resp = await client.get(
        "/api/v1/coaches/me/slots",
        headers={"Authorization": f"Bearer {coach_token}"},
    )
    assert list_resp.status_code == 200
    items = list_resp.json()
    assert isinstance(items, list)
    assert any(slot["id"] == created["id"] for slot in items)


@pytest.mark.asyncio
async def test_non_coach_cannot_create_slots(client: AsyncClient, parent_token: str):
    resp = await client.post(
        "/api/v1/coaches/me/slots",
        json={
            "day_of_week": 1,
            "start_time": "09:00:00",
            "end_time": "10:00:00",
            "slot_duration": 60,
            "max_students": 1,
        },
        headers={"Authorization": f"Bearer {parent_token}"},
    )
    assert resp.status_code == 403
