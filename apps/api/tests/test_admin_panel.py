import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_admin_can_seed_mock_coaches(client: AsyncClient, admin_token: str):
    resp = await client.post(
        "/api/v1/admin-panel/coaches/mock-seed",
        json={"count": 3},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["created_count"] == 3
    assert data["default_password"] == "coach123"
    assert len(data["items"]) == 3


@pytest.mark.asyncio
async def test_non_admin_cannot_seed_mock_coaches(client: AsyncClient, coach_token: str):
    resp = await client.post(
        "/api/v1/admin-panel/coaches/mock-seed",
        json={"count": 1},
        headers={"Authorization": f"Bearer {coach_token}"},
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_admin_can_list_and_update_coach(client: AsyncClient, admin_token: str):
    seed_resp = await client.post(
        "/api/v1/admin-panel/coaches/mock-seed",
        json={"count": 1},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert seed_resp.status_code == 200
    coach_id = seed_resp.json()["items"][0]["id"]

    list_resp = await client.get(
        "/api/v1/admin-panel/coaches?page=1&page_size=20",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert list_resp.status_code == 200
    assert list_resp.json()["total"] >= 1

    update_resp = await client.put(
        f"/api/v1/admin-panel/coaches/{coach_id}",
        json={
            "name": "模拟教练A",
            "specialty": ["篮球", "体操"],
            "hourly_rate": 199,
            "years_of_experience": 5,
            "introduction": "测试更新",
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert update_resp.status_code == 200
    updated = update_resp.json()
    assert updated["name"] == "模拟教练A"
    assert updated["specialty"] == ["篮球", "体操"]


@pytest.mark.asyncio
async def test_admin_can_publish_and_list_notices(client: AsyncClient, admin_token: str):
    publish_resp = await client.post(
        "/api/v1/admin-panel/notices",
        json={
            "kind": "announcement",
            "title": "系统维护通知",
            "content": "今晚22:00进行系统维护。",
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert publish_resp.status_code == 200
    published = publish_resp.json()
    assert published["recipient_count"] >= 1

    list_resp = await client.get(
        "/api/v1/admin-panel/notices?limit=10",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert list_resp.status_code == 200
    items = list_resp.json()["items"]
    assert any(item["publish_id"] == published["publish_id"] for item in items)
