"""Security and auth behavior tests for chat websocket."""

from contextlib import asynccontextmanager, contextmanager

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient
from starlette.websockets import WebSocketDisconnect

from app.api.v1.endpoints.chat import ticket_store
from app.main import app


@contextmanager
def _lifespan_free_test_client():
    original_lifespan = app.router.lifespan_context

    @asynccontextmanager
    async def _lifespan(_app):
        yield

    app.router.lifespan_context = _lifespan  # type: ignore[assignment]
    try:
        with TestClient(app) as client:
            yield client
    finally:
        app.router.lifespan_context = original_lifespan


@pytest.mark.asyncio
async def test_ws_ticket_requires_auth(client: AsyncClient):
    response = await client.post("/api/v1/chat/ws-ticket")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_ws_ticket_issue_success(client: AsyncClient, admin_token: str):
    response = await client.post(
        "/api/v1/chat/ws-ticket",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data.get("ticket"), str) and len(data["ticket"]) > 10
    assert data.get("expires_in") == 60


def test_websocket_accepts_ticket_and_rejects_reuse():
    with _lifespan_free_test_client() as client:
        ticket = ticket_store.issue(user_id=999)
        with client.websocket_connect(f"/api/v1/chat/ws?ticket={ticket}") as websocket:
            websocket.send_text("ping")
            assert websocket.receive_text() == "pong"

        with pytest.raises(WebSocketDisconnect):
            with client.websocket_connect(f"/api/v1/chat/ws?ticket={ticket}"):
                pass


def test_websocket_rejects_query_token():
    with _lifespan_free_test_client() as client:
        with pytest.raises(WebSocketDisconnect):
            with client.websocket_connect("/api/v1/chat/ws?token=fake-token"):
                pass
