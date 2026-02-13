"""Admin panel APIs for coach management and announcements."""

import json
from datetime import datetime, timezone
from typing import Literal, TypedDict

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user, get_password_hash
from app.models.notification import Notification, NotificationType
from app.models.user import Coach, User

router = APIRouter()

CurrentUserData = dict[str, int | str | None]


def _ensure_admin(current_user: CurrentUserData) -> None:
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin only")


def _parse_specialty(value: str | None) -> list[str]:
    if not value:
        return []
    try:
        loaded = json.loads(value)
        if isinstance(loaded, list):
            return [str(item) for item in loaded if str(item).strip()]
        return [str(loaded)]
    except (json.JSONDecodeError, TypeError):
        return [item.strip() for item in value.split(",") if item.strip()]


def _join_specialty(values: list[str]) -> str:
    return ",".join([value.strip() for value in values if value and value.strip()])


def _coach_item(coach: Coach, user: User) -> dict[str, object]:
    return {
        "id": coach.id,
        "user_id": coach.user_id,
        "coach_no": coach.coach_no,
        "name": coach.name,
        "phone": user.phone,
        "email": user.email,
        "avatar": coach.avatar,
        "specialty": _parse_specialty(coach.specialty),
        "introduction": coach.introduction,
        "hourly_rate": float(coach.hourly_rate) if coach.hourly_rate is not None else None,
        "years_of_experience": coach.years_of_experience,
        "status": coach.status,
    }


class AdminCoachUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=50)
    avatar: str | None = Field(default=None, max_length=500)
    specialty: list[str] | None = None
    introduction: str | None = None
    hourly_rate: float | None = Field(default=None, ge=0)
    years_of_experience: int | None = Field(default=None, ge=0, le=60)
    status: str | None = Field(default=None, pattern=r"^(active|inactive|banned)$")


class AdminMockCoachSeedRequest(BaseModel):
    count: int = Field(default=8, ge=1, le=30)


class AdminNoticePublishRequest(BaseModel):
    kind: Literal["announcement", "activity"] = "announcement"
    title: str = Field(min_length=2, max_length=100)
    content: str = Field(min_length=2, max_length=2000)


class MockCoachProfile(TypedDict):
    name: str
    specialty: list[str]
    hourly_rate: int
    years: int
    intro: str


MOCK_COACH_PROFILES: list[MockCoachProfile] = [
    {
        "name": "林教练",
        "specialty": ["篮球", "体操"],
        "hourly_rate": 168,
        "years": 4,
        "intro": "青少年篮球启蒙教练，擅长兴趣与体能结合。",
    },
    {
        "name": "陈教练",
        "specialty": ["足球", "体操"],
        "hourly_rate": 188,
        "years": 6,
        "intro": "校园足球训练经验丰富，注重团队协作与基础技术。",
    },
    {
        "name": "周教练",
        "specialty": ["游泳", "体操"],
        "hourly_rate": 220,
        "years": 8,
        "intro": "儿童游泳专项教练，强调安全和动作标准。",
    },
    {
        "name": "吴教练",
        "specialty": ["跆拳道", "体操"],
        "hourly_rate": 198,
        "years": 7,
        "intro": "跆拳道与体适能双修课程，提升协调与纪律性。",
    },
    {
        "name": "黄教练",
        "specialty": ["舞蹈", "体操"],
        "hourly_rate": 178,
        "years": 5,
        "intro": "青少年舞蹈基础训练，强调节奏感与身体控制。",
    },
    {
        "name": "何教练",
        "specialty": ["体操", "篮球"],
        "hourly_rate": 186,
        "years": 6,
        "intro": "体操专项教练，擅长柔韧与爆发力提升。",
    },
]


@router.get("/coaches")
async def admin_list_coaches(
    keyword: str | None = Query(default=None, description="按姓名/手机号/邮箱搜索"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUserData = Depends(get_current_user),
):
    _ensure_admin(current_user)

    query = select(Coach, User).join(User, Coach.user_id == User.id)
    if keyword:
        text = f"%{keyword.strip()}%"
        query = query.where(
            or_(
                Coach.name.ilike(text),
                User.phone.ilike(text),
                User.email.ilike(text),
                Coach.specialty.ilike(text),
            )
        )

    total = await db.scalar(select(func.count()).select_from(query.subquery())) or 0
    result = await db.execute(
        query.order_by(Coach.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    )
    rows = result.all()

    return {
        "items": [_coach_item(coach, user) for coach, user in rows],
        "total": int(total),
        "page": page,
        "page_size": page_size,
    }


@router.put("/coaches/{coach_id}")
async def admin_update_coach(
    coach_id: int,
    payload: AdminCoachUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUserData = Depends(get_current_user),
):
    _ensure_admin(current_user)

    coach = await db.get(Coach, coach_id)
    if not coach:
        raise HTTPException(status_code=404, detail="Coach not found")

    if payload.name is not None:
        coach.name = payload.name.strip()
    if payload.avatar is not None:
        coach.avatar = payload.avatar.strip() or None
    if payload.specialty is not None:
        coach.specialty = _join_specialty(payload.specialty)
    if payload.introduction is not None:
        coach.introduction = payload.introduction.strip() or None
    if payload.hourly_rate is not None:
        coach.hourly_rate = payload.hourly_rate
    if payload.years_of_experience is not None:
        coach.years_of_experience = payload.years_of_experience
    if payload.status is not None:
        coach.status = payload.status

    await db.commit()

    user = await db.get(User, coach.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Coach user not found")

    await db.refresh(coach)
    return _coach_item(coach, user)


@router.post("/coaches/mock-seed")
async def admin_seed_mock_coaches(
    payload: AdminMockCoachSeedRequest,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUserData = Depends(get_current_user),
):
    _ensure_admin(current_user)

    now = datetime.now(timezone.utc)
    stamp = now.strftime("%m%d%H%M%S")
    created: list[dict[str, object]] = []

    for index in range(payload.count):
        profile = MOCK_COACH_PROFILES[index % len(MOCK_COACH_PROFILES)]
        phone = f"1669{int(stamp[-7:]) + index:07d}"[-11:]
        email = f"mock.coach.{stamp}.{index}@rl.cornna.xyz"
        name = f"{profile['name']}{index + 1}"

        user = User(
            phone=phone,
            email=email,
            password_hash=get_password_hash("coach123"),
            role="coach",
            nickname=name,
            status="active",
        )
        db.add(user)
        await db.flush()

        coach = Coach(
            user_id=user.id,
            coach_no=f"MC{user.id:06d}",
            name=name,
            avatar="/static/default-avatar.png",
            specialty=_join_specialty(profile["specialty"]),
            introduction=str(profile["intro"]),
            hourly_rate=profile["hourly_rate"],
            years_of_experience=profile["years"],
            status="active",
            is_active=True,
        )
        db.add(coach)
        await db.flush()
        created.append(_coach_item(coach, user))

    await db.commit()
    return {
        "created_count": len(created),
        "default_password": "coach123",
        "items": created,
    }


@router.post("/notices")
async def admin_publish_notice(
    payload: AdminNoticePublishRequest,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUserData = Depends(get_current_user),
):
    _ensure_admin(current_user)

    target_result = await db.execute(
        select(User.id).where(User.status == "active", User.role != "admin")
    )
    target_ids = [row[0] for row in target_result.all()]
    if not target_ids:
        return {"message": "No active recipients", "recipient_count": 0}

    publish_id = int(datetime.now(timezone.utc).timestamp() * 1000)
    notifications = [
        Notification(
            user_id=user_id,
            type=NotificationType.SYSTEM.value,
            title=payload.title,
            content=payload.content,
            related_id=publish_id,
            related_type=payload.kind,
        )
        for user_id in target_ids
    ]
    db.add_all(notifications)
    await db.commit()

    return {
        "publish_id": publish_id,
        "kind": payload.kind,
        "title": payload.title,
        "recipient_count": len(target_ids),
    }


@router.get("/notices")
async def admin_list_notices(
    limit: int = Query(default=30, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUserData = Depends(get_current_user),
):
    _ensure_admin(current_user)

    result = await db.execute(
        select(
            Notification.related_id,
            Notification.related_type,
            func.max(Notification.title).label("title"),
            func.max(Notification.content).label("content"),
            func.max(Notification.created_at).label("created_at"),
            func.count(Notification.id).label("recipient_count"),
        )
        .where(
            Notification.type == NotificationType.SYSTEM.value,
            Notification.related_type.in_(["announcement", "activity"]),
            Notification.related_id.is_not(None),
        )
        .group_by(Notification.related_id, Notification.related_type)
        .order_by(func.max(Notification.created_at).desc())
        .limit(limit)
    )

    return {
        "items": [
            {
                "publish_id": int(row.related_id),
                "kind": row.related_type,
                "title": row.title,
                "content": row.content,
                "recipient_count": int(row.recipient_count),
                "created_at": row.created_at.isoformat() if row.created_at else None,
            }
            for row in result.all()
        ]
    }
