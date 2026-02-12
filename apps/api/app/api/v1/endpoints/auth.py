"""Authentication API endpoints."""
from typing import Optional

from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.security import get_current_user, verify_password
from app.models import User
from app.schemas import (
    CoachRegister,
    CoachResponse,
    EmailCodeLogin,
    EmailCodeRequest,
    EmailRegister,
    PasswordChange,
    PasswordReset,
    StudentRegister,
    StudentResponse,
    Token,
    UserCreate,
    UserDetailResponse,
    UserLogin,
    UserResponse,
    UserUpdate,
    WechatLogin,
    WechatPhoneLogin,
)
from app.services.auth_service import AuthService, EmailService, WechatService

router = APIRouter()


def _validate_password_strength(password: str) -> None:
    """Validate password meets security requirements."""
    if len(password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters long"
        )
    if not any(c.isalpha() for c in password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must contain at least one letter"
        )
    if not any(c.isdigit() for c in password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must contain at least one number"
        )


def _ensure_active(user: User) -> None:
    if user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled"
        )


def _token_response(user: User) -> Token:
    access_token, expires_in = AuthService.create_token(user)
    return Token(
        access_token=access_token,
        expires_in=expires_in,
        user=UserResponse.model_validate(user)
    )


def _wechat_error_http_status(message: str) -> int:
    msg = (message or "").lower()
    login_credential_cn = "\u767b\u5f55\u51ed\u8bc1"
    if "not configured" in msg:
        return status.HTTP_503_SERVICE_UNAVAILABLE
    if (
        "40029" in msg
        or "invalid code" in msg
        or login_credential_cn in message
        or "鐧诲綍鍑瘉" in message
        or "code is empty" in msg
    ):
        return status.HTTP_400_BAD_REQUEST
    if "timeout" in msg or "瓒呮椂" in message:
        return status.HTTP_502_BAD_GATEWAY
    return status.HTTP_500_INTERNAL_SERVER_ERROR


def _is_placeholder_wechat_nickname(nickname: Optional[str]) -> bool:
    raw = (nickname or "").strip()
    if not raw:
        return True

    lowered = raw.lower()
    wechat_placeholder = "\u5fae\u4fe1\u7528\u6237"
    wechat_placeholder_garbled = "寰俊鐢ㄦ埛"
    if raw.startswith(wechat_placeholder) or raw.startswith(wechat_placeholder_garbled):
        return True
    if lowered in {"newuser", "wechat user", "wechat_user"}:
        return True
    if lowered.startswith("newuser") or lowered.startswith("user_"):
        return True
    return False


def _normalize_wechat_nickname(nickname: Optional[str], wechat_openid: str) -> str:
    raw = (nickname or "").strip()[:50]
    if raw and not _is_placeholder_wechat_nickname(raw):
        return raw
    suffix = (wechat_openid or "").strip()[-6:] or "wechat"
    return f"\u7528\u6237{suffix}"[:50]


def _requires_wechat_role_selection(user: User) -> bool:
    """
    Detect legacy/incomplete WeChat accounts that were auto-created before
    explicit role selection became mandatory.
    """
    if not user.wechat_openid:
        return False
    if user.email or user.phone:
        return False
    if user.role != "parent":
        return False
    return _is_placeholder_wechat_nickname(user.nickname)


# ============ Registration ============

async def _validate_user_uniqueness(
    db: AsyncSession,
    email: str,
    phone: Optional[str] = None,
    nickname: Optional[str] = None
) -> None:
    """Validate user uniqueness constraints."""
    existing_user = await AuthService.get_user_by_email(db, email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    if phone:
        existing_phone = await AuthService.get_user_by_phone(db, phone)
        if existing_phone:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Phone already in use"
            )

    if nickname:
        existing_nickname = await AuthService.get_user_by_nickname(db, nickname)
        if existing_nickname:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already in use"
            )


async def _create_role_profile(
    db: AsyncSession,
    user_id: int,
    role: str,
    name: str,
    specialty: Optional[str] = None,
    introduction: Optional[str] = None
) -> None:
    """Create role-specific profile."""
    if role == "student":
        await AuthService.create_student_profile(db=db, user_id=user_id, name=name)
    elif role == "coach":
        await AuthService.create_coach_profile(
            db=db,
            user_id=user_id,
            name=name,
            specialty=specialty,
            introduction=introduction
        )
    elif role == "merchant":
        await AuthService.create_merchant_profile(db=db, user_id=user_id, name=name)


@router.post("/register", response_model=Token, summary="Email registration")
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    """Email + password registration (no email code verification)."""
    _validate_password_strength(user_data.password)
    await _validate_user_uniqueness(db, user_data.email, user_data.phone, user_data.nickname)

    user = await AuthService.create_user(
        db=db,
        email=user_data.email,
        phone=user_data.phone,
        password=user_data.password,
        role=user_data.role,
        nickname=user_data.nickname
    )

    await _create_role_profile(
        db=db,
        user_id=user.id,
        role=user_data.role,
        name=user_data.nickname or user_data.email.split("@")[0]
    )

    await db.commit()
    return _token_response(user)


@router.post("/register/email", response_model=Token, summary="Email code registration")
async def register_with_email(data: EmailRegister, db: AsyncSession = Depends(get_db)):
    """Email registration with verification code."""
    _validate_password_strength(data.password)
    is_valid = await EmailService.verify_code(data.email, data.code)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification code"
        )

    existing_user = await AuthService.get_user_by_email(db, data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    if data.phone:
        existing_phone = await AuthService.get_user_by_phone(db, data.phone)
        if existing_phone:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Phone already in use"
            )

    if data.nickname:
        existing_nickname = await AuthService.get_user_by_nickname(db, data.nickname)
        if existing_nickname:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already in use"
            )

    user = await AuthService.create_user(
        db=db,
        email=data.email,
        phone=data.phone,
        password=data.password,
        role=data.role,
        nickname=data.nickname
    )

    await _create_role_profile(
        db=db,
        user_id=user.id,
        role=data.role,
        name=data.nickname or data.email.split("@")[0]
    )

    await db.commit()
    return _token_response(user)


@router.post("/register/coach", response_model=Token, summary="Coach registration")
async def register_coach(coach_data: CoachRegister, db: AsyncSession = Depends(get_db)):
    _validate_password_strength(coach_data.password)
    await _validate_user_uniqueness(db, coach_data.email, coach_data.phone, coach_data.name)

    user = await AuthService.create_user(
        db=db,
        email=coach_data.email,
        phone=coach_data.phone,
        password=coach_data.password,
        role="coach",
        nickname=coach_data.name
    )

    specialty_str = ",".join(coach_data.specialty) if coach_data.specialty else None
    await _create_role_profile(
        db=db,
        user_id=user.id,
        role="coach",
        name=coach_data.name,
        specialty=specialty_str,
        introduction=coach_data.introduction
    )

    await db.commit()
    return _token_response(user)


@router.post("/register/with-role", response_model=Token, summary="Register with role selection")
async def register_with_role(
    payload: Optional[dict[str, object]] = Body(None),
    email: Optional[str] = None,
    wechat_openid: Optional[str] = None,
    role: Optional[str] = None,
    nickname: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Register user with explicit role selection (for email or WeChat login)."""
    payload = payload or {}
    if email is None:
        email = payload.get("email")
    if wechat_openid is None:
        wechat_openid = payload.get("wechat_openid")
    if role is None:
        role = payload.get("role")
    if nickname is None:
        nickname = payload.get("nickname")

    email = str(email).strip() if email is not None else None
    wechat_openid = str(wechat_openid).strip() if wechat_openid is not None else None
    role = str(role).strip() if role is not None else None
    nickname = str(nickname).strip() if nickname is not None else None

    if not role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role is required"
        )

    if role not in ["parent", "student", "coach", "merchant"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid role"
        )

    if not email and not wechat_openid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either email or wechat_openid is required"
        )

    if email:
        existing_user = await AuthService.get_user_by_email(db, email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

    if wechat_openid:
        existing_user = await AuthService.get_user_by_openid(db, wechat_openid)
        if existing_user:
            # Backward compatibility: allow legacy auto-created WeChat accounts
            # (without email/phone) to complete explicit role selection.
            if not existing_user.email and not existing_user.phone:
                existing_user.role = role
                existing_user.nickname = _normalize_wechat_nickname(
                    nickname or existing_user.nickname,
                    wechat_openid,
                )

                await _create_role_profile(
                    db=db,
                    user_id=existing_user.id,
                    role=role,
                    name=existing_user.nickname or f"user_{existing_user.id}"
                )

                await db.commit()
                await db.refresh(existing_user)
                return _token_response(existing_user)

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="WeChat account already registered"
            )

    normalized_nickname = nickname
    if wechat_openid:
        normalized_nickname = _normalize_wechat_nickname(nickname, wechat_openid)

    user = await AuthService.create_user(
        db=db,
        email=email,
        password="",
        role=role,
        nickname=normalized_nickname,
        openid=wechat_openid
    )

    await _create_role_profile(
        db=db,
        user_id=user.id,
        role=role,
        name=normalized_nickname or (email.split("@")[0] if email else f"user_{user.id}")
    )

    await db.commit()
    return _token_response(user)


# ============ Login ============

@router.post("/login", response_model=Token, summary="Account + password login")
async def login(login_data: UserLogin, db: AsyncSession = Depends(get_db)):
    account = (login_data.account or login_data.phone or login_data.email or "").strip()
    user = await AuthService.authenticate_user(db, account, login_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid account or password"
        )

    _ensure_active(user)
    return _token_response(user)


@router.post("/login/email/send", summary="Send email verification code")
async def send_email_code(data: EmailCodeRequest):
    from app.services.auth_service import EMAIL_CODE_STORE

    # Check rate limit: 3 attempts per 5 minutes
    is_allowed, seconds_until_reset = EMAIL_CODE_STORE.check_rate_limit(
        f"email_send:{data.email}", max_attempts=3, window_minutes=5
    )

    if not is_allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Too many requests. Please try again in {seconds_until_reset} seconds."
        )

    result = await EmailService.send_code_with_detail(data.email)
    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.get("message") or "Failed to send verification code"
        )

    response = {
        "message": result.get("message") or "Verification code sent",
        "delivery": result.get("delivery") or "smtp"
    }

    return response


@router.post("/login/email", response_model=Token, summary="Email code login")
async def login_with_email(login_data: EmailCodeLogin, db: AsyncSession = Depends(get_db)):
    is_valid = await EmailService.verify_code(login_data.email, login_data.code)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification code"
        )

    user = await AuthService.get_user_by_email(db, login_data.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="USER_NOT_REGISTERED"
        )

    _ensure_active(user)
    return _token_response(user)


@router.post("/login/wechat", response_model=Token, summary="WeChat login")
async def wechat_login(wechat_data: WechatLogin, db: AsyncSession = Depends(get_db)):
    try:
        session_info = await WechatService.code2session(wechat_data.code, wechat_data.device_id)
        openid = (session_info.get("openid") or "").strip()

        if not openid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to get WeChat openid from session"
            )

        incoming_nickname = ((wechat_data.user_info or {}).get("nickName") or "").strip()[:50]
        incoming_avatar = ((wechat_data.user_info or {}).get("avatarUrl") or "").strip()

        user = await AuthService.get_user_by_openid(db, openid)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "code": "WECHAT_ROLE_REQUIRED",
                    "message": "First WeChat login requires role selection",
                    "wechat_openid": openid,
                    "nickname": incoming_nickname or ""
                }
            )

        if _requires_wechat_role_selection(user):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "code": "WECHAT_ROLE_REQUIRED",
                    "message": "First WeChat login requires role selection",
                    "wechat_openid": openid,
                    "nickname": incoming_nickname or user.nickname or ""
                }
            )

        if wechat_data.user_info:
            profile_updated = False
            if incoming_nickname and user.nickname != incoming_nickname:
                user.nickname = incoming_nickname
                profile_updated = True
            if incoming_avatar and user.avatar != incoming_avatar:
                user.avatar = incoming_avatar
                profile_updated = True
            if profile_updated:
                await db.commit()
                await db.refresh(user)

        _ensure_active(user)
        return _token_response(user)

    except HTTPException:
        raise
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        message = str(e)
        logger.error(f"WeChat login error: {message}", exc_info=True)
        http_status = _wechat_error_http_status(message)
        if http_status != status.HTTP_500_INTERNAL_SERVER_ERROR:
            detail = message
        else:
            detail = f"WeChat login failed: {message}"
        raise HTTPException(
            status_code=http_status,
            detail=detail
        )

@router.post("/login/wechat-phone", response_model=Token, summary="WeChat phone login")
async def wechat_phone_login(data: WechatPhoneLogin, db: AsyncSession = Depends(get_db)):
    try:
        session_info = await WechatService.code2session(data.code, data.device_id)
        openid = session_info.get("openid")

        phone = ""
        if not data.phone_code.startswith("dev_phone:"):
            access_token_wx = await WechatService.get_access_token()
            phone = await WechatService.get_phone_number(data.phone_code, access_token_wx)
        else:
            phone = data.phone_code.split(":", 1)[1]

        if not phone:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to get phone number"
            )

        user = await AuthService.get_user_by_phone(db, phone)

        if user:
            if not user.wechat_openid and openid:
                await AuthService.bind_wechat(db, user, openid)
                await db.commit()
        else:
            user = await AuthService.create_user(
                db=db,
                phone=phone,
                password="",
                role="parent",
                openid=openid
            )
            await db.commit()

        _ensure_active(user)
        return _token_response(user)

    except HTTPException:
        raise
    except Exception as e:
        message = str(e)
        http_status = _wechat_error_http_status(message)
        if http_status != status.HTTP_500_INTERNAL_SERVER_ERROR:
            detail = message
        else:
            detail = f"Login failed: {message}"
        raise HTTPException(
            status_code=http_status,
            detail=detail
        )


# ============ Password management ============

@router.post("/password/reset", summary="Reset password via email code")
async def reset_password(data: PasswordReset, db: AsyncSession = Depends(get_db)):
    from app.services.auth_service import EMAIL_CODE_STORE

    # Rate limit: 5 attempts per hour per IP
    is_allowed, seconds_until_reset = EMAIL_CODE_STORE.check_rate_limit(
        f"password_reset:{data.email}", max_attempts=5, window_minutes=60
    )

    if not is_allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=(
                "Too many password reset attempts. "
                f"Please try again in {seconds_until_reset} seconds."
            ),
        )

    _validate_password_strength(data.new_password)
    is_valid = await EmailService.verify_code(data.email, data.code)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification code"
        )

    user = await AuthService.get_user_by_email(db, data.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    await AuthService.update_password(db, user, data.new_password)
    await db.commit()

    return {"message": "Password reset success"}


@router.post("/password/change", summary="Change password")
async def change_password(
    data: PasswordChange,
    current_user: dict[str, object] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    _validate_password_strength(data.new_password)
    user = await AuthService.get_user_by_id(db, current_user["user_id"])
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if not user.password_hash or not verify_password(data.old_password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid old password"
        )

    await AuthService.update_password(db, user, data.new_password)
    await db.commit()

    return {"message": "Password changed"}


# ============ User info ============

@router.get("/me", response_model=UserDetailResponse, summary="Get current user")
async def get_current_user_info(
    current_user: dict[str, object] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Preload relations to avoid async lazy-load errors (MissingGreenlet).
    result = await db.execute(
        select(User)
        .options(selectinload(User.student), selectinload(User.coach))
        .where(User.id == current_user["user_id"])
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    response = UserDetailResponse(
        id=user.id,
        phone=user.phone,
        email=user.email,
        nickname=user.nickname,
        avatar=user.avatar,
        role=user.role,
        status=user.status,
        created_at=user.created_at,
        wechat_bindded=bool(user.wechat_openid)
    )

    if user.student:
        response.student = StudentResponse.model_validate(user.student)
    if user.coach:
        response.coach = CoachResponse.model_validate(user.coach)

    return response


@router.put("/me", response_model=UserResponse, summary="Update current user")
async def update_user_info(
    data: UserUpdate,
    current_user: dict[str, object] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    user = await AuthService.get_user_by_id(db, current_user["user_id"])
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if data.nickname is not None:
        if data.nickname:
            existing = await AuthService.get_user_by_nickname(db, data.nickname)
            if existing and existing.id != user.id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already in use"
                )
        user.nickname = data.nickname
    if data.avatar is not None:
        user.avatar = data.avatar
    if data.phone is not None:
        # Check phone uniqueness
        if data.phone:
            existing = await AuthService.get_user_by_phone(db, data.phone)
            if existing and existing.id != user.id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Phone already in use"
                )
        user.phone = data.phone or None

    await db.commit()
    await db.refresh(user)

    return UserResponse.model_validate(user)


@router.post("/logout", summary="Logout")
async def logout(current_user: dict[str, object] = Depends(get_current_user)):
    return {"message": "Logout success"}


# ============ Student management (parent) ============

@router.post("/students", response_model=StudentResponse, summary="Add student")
async def add_student(
    data: StudentRegister,
    current_user: dict[str, object] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if current_user["role"] not in ["parent", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied"
        )

    student_user = await AuthService.create_user(
        db=db,
        email=None,
        phone=None,
        password="",
        role="student",
        nickname=data.name
    )

    student = await AuthService.create_student_profile(
        db=db,
        user_id=student_user.id,
        name=data.name,
        gender=data.gender,
        birth_date=data.birth_date,
        parent_id=current_user["user_id"]
    )

    await db.commit()
    return StudentResponse.model_validate(student)


@router.post(
    "/students/{student_id}/create-account",
    response_model=Token,
    summary="Create student account",
)
async def create_student_account(
    student_id: int,
    data: UserCreate,
    current_user: dict[str, object] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Parent creates an independent account for their student."""
    from app.models import ParentStudentRelation, Student

    if current_user["role"] not in ["parent", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied"
        )

    # Verify the student belongs to this parent
    student_query = select(Student).where(Student.id == student_id)
    result = await db.execute(student_query)
    student = result.scalar_one_or_none()

    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )

    # Check if parent owns this student
    if student.parent_id != current_user["user_id"]:
        # Also check parent_student_relations table
        relation_query = select(ParentStudentRelation).where(
            ParentStudentRelation.parent_id == current_user["user_id"],
            ParentStudentRelation.student_id == student_id
        )
        relation_result = await db.execute(relation_query)
        if not relation_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to manage this student"
            )

    # Check if student already has an account
    if student.user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Student already has an account"
        )

    # Check email uniqueness
    existing_user = await AuthService.get_user_by_email(db, data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create user account for student
    _validate_password_strength(data.password)
    user = await AuthService.create_user(
        db=db,
        email=data.email,
        password=data.password,
        role="student",
        nickname=student.name
    )

    # Link student to user
    student.user_id = user.id

    await db.commit()
    return _token_response(user)


# ============ Dev/Test helpers ============

@router.get("/dev/email-code/{email}", summary="[DEV] Get email verification code")
async def dev_get_email_code(email: str):
    """Dev-only endpoint to retrieve the current verification code for testing.
    Should be disabled in production."""
    from app.core.config import settings
    if not (settings.DEBUG and settings.DEV_PRINT_CODE):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Endpoint not available"
        )
    from app.services.auth_service import EMAIL_CODE_STORE
    code = EMAIL_CODE_STORE.get_code(email)
    if not code:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active code for this email"
        )
    return {"email": email, "code": code}

