"""Authentication API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import verify_password, get_current_user
from app.models import User
from app.schemas import (
    UserCreate, UserLogin, WechatLogin, WechatPhoneLogin,
    SmsCodeRequest, SmsCodeLogin, SmsRegister,
    PasswordReset, PasswordChange,
    UserUpdate, UserResponse, UserDetailResponse, Token,
    StudentRegister, StudentResponse,
    CoachRegister, CoachResponse
)
from app.services.auth_service import AuthService, WechatService, SmsService

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

@router.post("/register", response_model=Token, summary="Phone registration")
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    """Phone + password registration (no SMS verification)."""
    existing_user = await AuthService.get_user_by_phone(db, user_data.phone)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone already registered"
        )

    user = await AuthService.create_user(
        db=db,
        phone=user_data.phone,
        password=user_data.password,
        role=user_data.role,
        nickname=user_data.nickname
    )

    if user_data.role == "student":
        await AuthService.create_student_profile(
            db=db,
            user_id=user.id,
            name=user_data.nickname or f"Student{user_data.phone[-4:]}"
        )

    await db.commit()
    return _token_response(user)


@router.post("/register/sms", response_model=Token, summary="SMS registration")
async def register_with_sms(data: SmsRegister, db: AsyncSession = Depends(get_db)):
    """Phone registration with SMS code verification."""
    is_valid = await SmsService.verify_code(data.phone, data.code)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification code"
        )

    existing_user = await AuthService.get_user_by_phone(db, data.phone)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone already registered"
        )

    user = await AuthService.create_user(
        db=db,
        phone=data.phone,
        password=data.password,
        role=data.role,
        nickname=data.nickname
    )

    if data.role == "student":
        await AuthService.create_student_profile(
            db=db,
            user_id=user.id,
            name=data.nickname or f"Student{data.phone[-4:]}"
        )

    await db.commit()
    return _token_response(user)


@router.post("/register/coach", response_model=Token, summary="Coach registration")
async def register_coach(coach_data: CoachRegister, db: AsyncSession = Depends(get_db)):
    existing_user = await AuthService.get_user_by_phone(db, coach_data.phone)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone already registered"
        )

    user = await AuthService.create_user(
        db=db,
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

@router.post("/login", response_model=Token, summary="Phone + password login")
async def login(login_data: UserLogin, db: AsyncSession = Depends(get_db)):
    user = await AuthService.authenticate_user(db, login_data.phone, login_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid phone or password"
        )

    _ensure_active(user)
    return _token_response(user)


@router.post("/login/sms/send", summary="Send SMS code")
async def send_sms_code(data: SmsCodeRequest):
    success = await SmsService.send_code(data.phone)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send code"
        )
    return {"message": "Code sent"}


@router.post("/login/sms", response_model=Token, summary="SMS code login")
async def login_with_sms(login_data: SmsCodeLogin, db: AsyncSession = Depends(get_db)):
    is_valid = await SmsService.verify_code(login_data.phone, login_data.code)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification code"
        )

    user = await AuthService.get_user_by_phone(db, login_data.phone)
    if not user:
        user = await AuthService.create_user(
            db=db,
            phone=login_data.phone,
            password="",
            role="parent"
        )
        await db.commit()

    _ensure_active(user)
    return _token_response(user)


@router.post("/login/wechat", response_model=Token, summary="WeChat login")
async def wechat_login(wechat_data: WechatLogin, db: AsyncSession = Depends(get_db)):
    try:
        session_info = await WechatService.code2session(wechat_data.code)
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
                nickname = wechat_data.user_info.get("nickName")
                avatar = wechat_data.user_info.get("avatarUrl")

            user = User(
                wechat_openid=openid,
                nickname=nickname or "WeChat User",
                avatar=avatar,
                role="parent",
                status="active"
            )
            db.add(user)
            await db.flush()
            await db.refresh(user)
            await db.commit()

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
        session_info = await WechatService.code2session(data.code)
        openid = session_info.get("openid")

        access_token_wx = await WechatService.get_access_token()
        phone = await WechatService.get_phone_number(data.phone_code, access_token_wx)

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

@router.post("/password/reset", summary="Reset password")
async def reset_password(data: PasswordReset, db: AsyncSession = Depends(get_db)):
    is_valid = await SmsService.verify_code(data.phone, data.code)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification code"
        )

    user = await AuthService.get_user_by_phone(db, data.phone)
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
    user = await AuthService.get_user_by_id(db, current_user["user_id"])
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    response = UserDetailResponse(
        id=user.id,
        phone=user.phone,
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
        user.nickname = data.nickname
    if data.avatar is not None:
        user.avatar = data.avatar

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
