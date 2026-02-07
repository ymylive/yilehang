"""Authentication API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import verify_password, get_current_user
from app.models import User
from app.schemas import (
    UserCreate, UserLogin, WechatLogin, WechatPhoneLogin,
    EmailCodeRequest, EmailCodeLogin, EmailRegister,
    PasswordReset, PasswordChange,
    UserUpdate, UserResponse, UserDetailResponse, Token,
    StudentRegister, StudentResponse,
    CoachRegister, CoachResponse
)
from app.services.auth_service import AuthService, WechatService, EmailService
from sqlalchemy.orm import selectinload

router = APIRouter()


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


# ============ Registration ============

@router.post("/register", response_model=Token, summary="Email registration")
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    """Email + password registration (no email code verification)."""
    existing_user = await AuthService.get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    if user_data.phone:
        existing_phone = await AuthService.get_user_by_phone(db, user_data.phone)
        if existing_phone:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Phone already in use"
            )

    if user_data.nickname:
        existing_nickname = await AuthService.get_user_by_nickname(db, user_data.nickname)
        if existing_nickname:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already in use"
            )

    user = await AuthService.create_user(
        db=db,
        email=user_data.email,
        phone=user_data.phone,
        password=user_data.password,
        role=user_data.role,
        nickname=user_data.nickname
    )

    if user_data.role == "student":
        await AuthService.create_student_profile(
            db=db,
            user_id=user.id,
            name=user_data.nickname or user_data.email.split("@")[0]
        )
    elif user_data.role == "coach":
        await AuthService.create_coach_profile(
            db=db,
            user_id=user.id,
            name=user_data.nickname or user_data.email.split("@")[0]
        )

    await db.commit()
    return _token_response(user)


@router.post("/register/email", response_model=Token, summary="Email code registration")
async def register_with_email(data: EmailRegister, db: AsyncSession = Depends(get_db)):
    """Email registration with verification code."""
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

    if data.role == "student":
        await AuthService.create_student_profile(
            db=db,
            user_id=user.id,
            name=data.nickname or data.email.split("@")[0]
        )
    elif data.role == "coach":
        await AuthService.create_coach_profile(
            db=db,
            user_id=user.id,
            name=data.nickname or data.email.split("@")[0]
        )
    elif data.role == "merchant":
        await AuthService.create_merchant_profile(
            db=db,
            user_id=user.id,
            name=data.nickname or data.email.split("@")[0]
        )

    await db.commit()
    return _token_response(user)


@router.post("/register/coach", response_model=Token, summary="Coach registration")
async def register_coach(coach_data: CoachRegister, db: AsyncSession = Depends(get_db)):
    existing_user = await AuthService.get_user_by_email(db, coach_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    if coach_data.phone:
        existing_phone = await AuthService.get_user_by_phone(db, coach_data.phone)
        if existing_phone:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Phone already in use"
            )

    existing_nickname = await AuthService.get_user_by_nickname(db, coach_data.name)
    if existing_nickname:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already in use"
        )

    user = await AuthService.create_user(
        db=db,
        email=coach_data.email,
        phone=coach_data.phone,
        password=coach_data.password,
        role="coach",
        nickname=coach_data.name
    )

    specialty_str = ",".join(coach_data.specialty) if coach_data.specialty else None
    await AuthService.create_coach_profile(
        db=db,
        user_id=user.id,
        name=coach_data.name,
        specialty=specialty_str,
        introduction=coach_data.introduction
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

    if result.get("dev_code"):
        response["dev_code"] = result.get("dev_code")

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
        # Auto-register on first email code login
        user = await AuthService.create_user(
            db=db,
            email=login_data.email,
            password="",
            role="parent"
        )
        await db.commit()

    _ensure_active(user)
    return _token_response(user)


@router.post("/login/wechat", response_model=Token, summary="WeChat login")
async def wechat_login(wechat_data: WechatLogin, db: AsyncSession = Depends(get_db)):
    try:
        if not wechat_data.user_info:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="需要微信授权用户信息后才能登录"
            )

        session_info = await WechatService.code2session(wechat_data.code, wechat_data.device_id)
        openid = session_info.get("openid")

        if not openid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to get WeChat info"
            )

        user = await AuthService.get_user_by_openid(db, openid)

        if not user:
            nickname = None
            avatar = None
            if wechat_data.user_info:
                nickname = (wechat_data.user_info.get("nickName") or "").strip()[:50]
                avatar = wechat_data.user_info.get("avatarUrl")

            user = User(
                wechat_openid=openid,
                nickname=nickname or "微信用户",
                avatar=avatar,
                role="parent",
                status="active"
            )
            db.add(user)
            await db.flush()
            await db.refresh(user)
            await db.commit()
        else:
            profile_updated = False
            incoming_nickname = (wechat_data.user_info.get("nickName") or "").strip()[:50]
            if incoming_nickname and user.nickname != incoming_nickname:
                user.nickname = incoming_nickname
                profile_updated = True
            if wechat_data.user_info.get("avatarUrl") and user.avatar != wechat_data.user_info.get("avatarUrl"):
                user.avatar = wechat_data.user_info.get("avatarUrl")
                profile_updated = True
            if profile_updated:
                await db.commit()
                await db.refresh(user)

        _ensure_active(user)
        return _token_response(user)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"WeChat login failed: {str(e)}"
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
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )


# ============ Password management ============

@router.post("/password/reset", summary="Reset password via email code")
async def reset_password(data: PasswordReset, db: AsyncSession = Depends(get_db)):
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
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
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
    current_user: dict = Depends(get_current_user),
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
    current_user: dict = Depends(get_current_user),
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
async def logout(current_user: dict = Depends(get_current_user)):
    return {"message": "Logout success"}


# ============ Student management (parent) ============

@router.post("/students", response_model=StudentResponse, summary="Add student")
async def add_student(
    data: StudentRegister,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if current_user["role"] not in ["parent", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied"
        )

    student = await AuthService.create_student_profile(
        db=db,
        user_id=None,
        name=data.name,
        gender=data.gender,
        birth_date=data.birth_date,
        parent_id=current_user["user_id"]
    )

    await db.commit()
    return StudentResponse.model_validate(student)


@router.post("/students/{student_id}/create-account", response_model=Token, summary="Create student account")
async def create_student_account(
    student_id: int,
    data: UserCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Parent creates an independent account for their student."""
    from app.models import Student, ParentStudentRelation

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
    from app.services.auth_service import EMAIL_CODE_STORE
    code = EMAIL_CODE_STORE.get_code(email)
    if not code:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active code for this email"
        )
    return {"email": email, "code": code}
