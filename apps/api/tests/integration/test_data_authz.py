"""Integration tests for object-level authorization on data endpoints."""

from datetime import datetime, timedelta, timezone

import pytest
from httpx import AsyncClient
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash
from app.models import Booking, Coach, Course, Schedule, Student, User


@pytest.fixture
async def authz_seed_data(db_session: AsyncSession, test_users: dict) -> dict[str, int]:
    """Create own/foreign students plus schedule and bookings for authz checks."""
    coach_user = test_users["coach"]
    student_user = test_users["student"]
    parent_user = test_users["parent"]

    coach = (
        await db_session.execute(select(Coach).where(Coach.user_id == coach_user.id))
    ).scalar_one()
    own_student = (
        await db_session.execute(select(Student).where(Student.user_id == student_user.id))
    ).scalar_one()
    own_student.parent_id = parent_user.id
    own_student.coach_id = coach.id

    other_parent = User(
        email="parent2@test.com",
        phone="13900000101",
        password_hash=get_password_hash("parent123"),
        role="parent",
        nickname="Parent Two",
        status="active",
    )
    db_session.add(other_parent)
    await db_session.flush()

    other_student_user = User(
        email="student2@test.com",
        phone="13900000102",
        password_hash=get_password_hash("student123"),
        role="student",
        nickname="Student Two",
        status="active",
    )
    db_session.add(other_student_user)
    await db_session.flush()

    other_student = Student(
        user_id=other_student_user.id,
        student_no=f"S{other_student_user.id:06d}",
        name="Student Two",
        parent_id=other_parent.id,
        coach_id=coach.id,
        status="active",
        is_active=True,
    )
    db_session.add(other_student)
    await db_session.flush()

    course = Course(
        name="Authz Course",
        code="AUTHZ001",
        type="group",
        category="other",
        duration=60,
        max_students=20,
        price=0,
        status="active",
    )
    db_session.add(course)
    await db_session.flush()

    start_dt = datetime.now(timezone.utc) + timedelta(days=1)
    end_dt = start_dt + timedelta(hours=1)
    schedule = Schedule(
        course_id=course.id,
        coach_id=coach.id,
        start_time=start_dt,
        end_time=end_dt,
        capacity=20,
        enrolled_count=0,
        status="scheduled",
    )
    db_session.add(schedule)
    await db_session.flush()

    own_booking = Booking(
        student_id=own_student.id,
        coach_id=coach.id,
        schedule_id=schedule.id,
        booking_date=start_dt.date(),
        start_time=start_dt.time().replace(microsecond=0),
        end_time=end_dt.time().replace(microsecond=0),
        course_type="private",
        status="confirmed",
    )
    other_booking = Booking(
        student_id=other_student.id,
        coach_id=coach.id,
        schedule_id=schedule.id,
        booking_date=start_dt.date(),
        start_time=(start_dt + timedelta(hours=2)).time().replace(microsecond=0),
        end_time=(end_dt + timedelta(hours=2)).time().replace(microsecond=0),
        course_type="private",
        status="confirmed",
    )
    db_session.add_all([own_booking, other_booking])
    await db_session.flush()
    await db_session.commit()

    return {
        "own_student_id": own_student.id,
        "other_student_id": other_student.id,
        "schedule_id": schedule.id,
        "own_booking_id": own_booking.id,
        "other_booking_id": other_booking.id,
    }


@pytest.mark.asyncio
async def test_student_cannot_access_other_student_profile(
    client: AsyncClient,
    student_token: str,
    authz_seed_data: dict[str, int],
):
    response = await client.get(
        f"/api/v1/students/{authz_seed_data['other_student_id']}",
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_parent_can_access_own_student_profile(
    client: AsyncClient,
    parent_token: str,
    authz_seed_data: dict[str, int],
):
    response = await client.get(
        f"/api/v1/students/{authz_seed_data['own_student_id']}",
        headers={"Authorization": f"Bearer {parent_token}"},
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_student_cannot_access_other_booking_detail(
    client: AsyncClient,
    student_token: str,
    authz_seed_data: dict[str, int],
):
    response = await client.get(
        f"/api/v1/bookings/{authz_seed_data['other_booking_id']}",
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_parent_can_access_own_booking_detail(
    client: AsyncClient,
    parent_token: str,
    authz_seed_data: dict[str, int],
):
    response = await client.get(
        f"/api/v1/bookings/{authz_seed_data['own_booking_id']}",
        headers={"Authorization": f"Bearer {parent_token}"},
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_student_cannot_access_other_growth_and_training_history(
    client: AsyncClient,
    student_token: str,
    authz_seed_data: dict[str, int],
):
    growth_response = await client.get(
        f"/api/v1/growth/fitness-test/{authz_seed_data['other_student_id']}",
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert growth_response.status_code == 403

    training_response = await client.get(
        "/api/v1/training/history",
        params={"student_id": authz_seed_data["other_student_id"]},
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert training_response.status_code == 403


@pytest.mark.asyncio
async def test_student_cannot_enroll_or_checkin_other_student(
    client: AsyncClient,
    student_token: str,
    authz_seed_data: dict[str, int],
):
    enroll_payload = {
        "schedule_id": authz_seed_data["schedule_id"],
        "student_id": authz_seed_data["other_student_id"],
    }
    enroll_response = await client.post(
        f"/api/v1/schedules/{authz_seed_data['schedule_id']}/enroll",
        json=enroll_payload,
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert enroll_response.status_code == 403

    checkin_payload = {
        "schedule_id": authz_seed_data["schedule_id"],
        "student_id": authz_seed_data["other_student_id"],
        "check_in_method": "manual",
    }
    checkin_response = await client.post(
        f"/api/v1/schedules/{authz_seed_data['schedule_id']}/checkin",
        json=checkin_payload,
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert checkin_response.status_code == 403


@pytest.mark.asyncio
async def test_parent_can_enroll_own_student(
    client: AsyncClient,
    parent_token: str,
    authz_seed_data: dict[str, int],
):
    payload = {
        "schedule_id": authz_seed_data["schedule_id"],
        "student_id": authz_seed_data["own_student_id"],
    }
    response = await client.post(
        f"/api/v1/schedules/{authz_seed_data['schedule_id']}/enroll",
        json=payload,
        headers={"Authorization": f"Bearer {parent_token}"},
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_enroll_capacity_not_exceeded_across_multiple_requests(
    authz_seed_data: dict[str, int],
    db_session: AsyncSession,
):
    await db_session.execute(
        update(Schedule)
        .where(Schedule.id == authz_seed_data["schedule_id"])
        .values(capacity=1, enrolled_count=0)
    )
    await db_session.commit()

    first_update = await db_session.execute(
        update(Schedule)
        .where(
            Schedule.id == authz_seed_data["schedule_id"],
            Schedule.enrolled_count < Schedule.capacity,
        )
        .values(enrolled_count=Schedule.enrolled_count + 1)
        .returning(Schedule.id)
    )
    second_update = await db_session.execute(
        update(Schedule)
        .where(
            Schedule.id == authz_seed_data["schedule_id"],
            Schedule.enrolled_count < Schedule.capacity,
        )
        .values(enrolled_count=Schedule.enrolled_count + 1)
        .returning(Schedule.id)
    )
    await db_session.commit()

    assert first_update.scalar_one_or_none() == authz_seed_data["schedule_id"]
    assert second_update.scalar_one_or_none() is None

    enrolled_count = (
        await db_session.execute(
            select(Schedule.enrolled_count).where(Schedule.id == authz_seed_data["schedule_id"])
        )
    ).scalar_one()
    assert enrolled_count == 1
