"""Pytest configuration and fixtures for integration tests."""

import asyncio
import os
from pathlib import Path
from typing import AsyncGenerator, Generator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.core.database import Base, get_db
from app.core.security import get_password_hash
from app.main import app
from app.models import Coach, Student, User

# Test database URL
# Prefer an explicit TEST_DATABASE_URL when provided.
# Default to local SQLite test DB to avoid external PostgreSQL dependency.
_DEFAULT_TEST_DB_FILE = f".pytest_renling_{os.getpid()}.db"
_DEFAULT_TEST_DB_URL = f"sqlite+aiosqlite:///./{_DEFAULT_TEST_DB_FILE}"
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", _DEFAULT_TEST_DB_URL)


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_engine():
    """Create test database engine."""
    engine = create_async_engine(TEST_DATABASE_URL, poolclass=NullPool, echo=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()

    if "TEST_DATABASE_URL" not in os.environ:
        default_db_path = Path(_DEFAULT_TEST_DB_FILE)
        if default_db_path.exists():
            default_db_path.unlink()


@pytest.fixture(scope="function")
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create a fresh database session for each test."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async_session = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        yield session


@pytest.fixture(scope="function")
async def client(db_session: AsyncSession, test_engine) -> AsyncGenerator[AsyncClient, None]:
    """Create test client with database session override."""
    async_session = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)

    async def override_get_db():
        async with async_session() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
async def test_users(db_session: AsyncSession) -> dict:
    """Create test users for all roles."""
    users = {}

    # Admin user
    admin = User(
        email="admin@test.com",
        phone="13800000000",
        password_hash=get_password_hash("admin123"),
        role="admin",
        nickname="Admin User",
        status="active",
    )
    db_session.add(admin)
    await db_session.flush()
    users["admin"] = admin

    # Coach user
    coach_user = User(
        email="coach@test.com",
        phone="13800000001",
        password_hash=get_password_hash("coach123"),
        role="coach",
        nickname="Coach User",
        status="active",
    )
    db_session.add(coach_user)
    await db_session.flush()

    coach = Coach(
        user_id=coach_user.id,
        coach_no=f"C{coach_user.id:06d}",
        name="Coach User",
        status="active",
        is_active=True,
    )
    db_session.add(coach)
    await db_session.flush()
    users["coach"] = coach_user

    # Parent user
    parent = User(
        email="parent@test.com",
        phone="13900000001",
        password_hash=get_password_hash("parent123"),
        role="parent",
        nickname="Parent User",
        status="active",
    )
    db_session.add(parent)
    await db_session.flush()
    users["parent"] = parent

    # Student user
    student_user = User(
        email="student@test.com",
        phone="13900000002",
        password_hash=get_password_hash("student123"),
        role="student",
        nickname="Student User",
        status="active",
    )
    db_session.add(student_user)
    await db_session.flush()

    student = Student(
        user_id=student_user.id,
        student_no=f"S{student_user.id:06d}",
        name="Student User",
        parent_id=parent.id,
        status="active",
        is_active=True,
    )
    db_session.add(student)
    await db_session.flush()
    users["student"] = student_user

    await db_session.commit()

    return users


@pytest.fixture
async def admin_token(client: AsyncClient, test_users: dict) -> str:
    """Get admin authentication token."""
    response = await client.post(
        "/api/v1/auth/login", json={"account": "admin@test.com", "password": "admin123"}
    )
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture
async def coach_token(client: AsyncClient, test_users: dict) -> str:
    """Get coach authentication token."""
    response = await client.post(
        "/api/v1/auth/login", json={"account": "coach@test.com", "password": "coach123"}
    )
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture
async def parent_token(client: AsyncClient, test_users: dict) -> str:
    """Get parent authentication token."""
    response = await client.post(
        "/api/v1/auth/login", json={"account": "parent@test.com", "password": "parent123"}
    )
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture
async def student_token(client: AsyncClient, test_users: dict) -> str:
    """Get student authentication token."""
    response = await client.post(
        "/api/v1/auth/login", json={"account": "student@test.com", "password": "student123"}
    )
    assert response.status_code == 200
    return response.json()["access_token"]
