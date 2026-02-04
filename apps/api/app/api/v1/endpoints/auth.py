"""
认证相关API
"""
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.config import settings
from app.core.security import verify_password, get_password_hash, create_access_token, get_current_user
from app.models import User, Student, Coach
from app.schemas import (
    UserCreate, UserLogin, WechatLogin, WechatPhoneLogin,
    SmsCodeRequest, SmsCodeLogin, PasswordReset, PasswordChange,
    UserUpdate, UserResponse, UserDetailResponse, Token,
    StudentRegister, StudentResponse,
    CoachRegister, CoachResponse, CoachProfileResponse
)
from app.services.auth_service import AuthService, WechatService, SmsService

router = APIRouter()


# ============ 注册 ============

@router.post("/register", response_model=Token, summary="手机号注册")
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    """
    手机号密码注册
    - **phone**: 手机号
    - **password**: 密码 (6-20位)
    - **role**: 角色 (parent/student/coach)
    - **nickname**: 昵称 (可选)
    """
    # 检查手机号是否已存在
    existing_user = await AuthService.get_user_by_phone(db, user_data.phone)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该手机号已注册"
        )

    # 创建用户
    user = await AuthService.create_user(
        db=db,
        phone=user_data.phone,
        password=user_data.password,
        role=user_data.role,
        nickname=user_data.nickname
    )

    # 如果是学员角色，创建学员档案
    if user_data.role == "student":
        await AuthService.create_student_profile(
            db=db,
            user_id=user.id,
            name=user_data.nickname or f"学员{user_data.phone[-4:]}"
        )

    await db.commit()

    # 生成Token
    access_token, expires_in = AuthService.create_token(user)

    return Token(
        access_token=access_token,
        expires_in=expires_in,
        user=UserResponse.model_validate(user)
    )


@router.post("/register/coach", response_model=Token, summary="教练注册")
async def register_coach(coach_data: CoachRegister, db: AsyncSession = Depends(get_db)):
    """
    教练注册
    - **phone**: 手机号
    - **password**: 密码
    - **name**: 姓名
    - **specialty**: 专长列表
    - **introduction**: 个人介绍
    """
    # 检查手机号是否已存在
    existing_user = await AuthService.get_user_by_phone(db, coach_data.phone)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该手机号已注册"
        )

    # 创建用户
    user = await AuthService.create_user(
        db=db,
        phone=coach_data.phone,
        password=coach_data.password,
        role="coach",
        nickname=coach_data.name
    )

    # 创建教练档案
    specialty_str = ",".join(coach_data.specialty) if coach_data.specialty else None
    await AuthService.create_coach_profile(
        db=db,
        user_id=user.id,
        name=coach_data.name,
        specialty=specialty_str,
        introduction=coach_data.introduction
    )

    await db.commit()

    # 生成Token
    access_token, expires_in = AuthService.create_token(user)

    return Token(
        access_token=access_token,
        expires_in=expires_in,
        user=UserResponse.model_validate(user)
    )


# ============ 登录 ============

@router.post("/login", response_model=Token, summary="手机号密码登录")
async def login(login_data: UserLogin, db: AsyncSession = Depends(get_db)):
    """
    手机号密码登录
    """
    user = await AuthService.authenticate_user(db, login_data.phone, login_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="手机号或密码错误"
        )

    if user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="账号已被禁用"
        )

    access_token, expires_in = AuthService.create_token(user)

    return Token(
        access_token=access_token,
        expires_in=expires_in,
        user=UserResponse.model_validate(user)
    )


@router.post("/login/sms/send", summary="发送短信验证码")
async def send_sms_code(data: SmsCodeRequest):
    """
    发送短信验证码
    """
    success = await SmsService.send_code(data.phone)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="验证码发送失败"
        )
    return {"message": "验证码已发送"}


@router.post("/login/sms", response_model=Token, summary="短信验证码登录")
async def login_with_sms(login_data: SmsCodeLogin, db: AsyncSession = Depends(get_db)):
    """
    短信验证码登录 (自动注册)
    """
    # 验证验证码
    is_valid = await SmsService.verify_code(login_data.phone, login_data.code)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="验证码错误或已过期"
        )

    # 查找或创建用户
    user = await AuthService.get_user_by_phone(db, login_data.phone)
    if not user:
        # 自动注册
        user = await AuthService.create_user(
            db=db,
            phone=login_data.phone,
            password="",  # 短信登录无密码
            role="parent"
        )
        await db.commit()

    if user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="账号已被禁用"
        )

    access_token, expires_in = AuthService.create_token(user)

    return Token(
        access_token=access_token,
        expires_in=expires_in,
        user=UserResponse.model_validate(user)
    )


@router.post("/login/wechat", response_model=Token, summary="微信登录")
async def wechat_login(wechat_data: WechatLogin, db: AsyncSession = Depends(get_db)):
    """
    微信小程序登录
    - **code**: 微信登录code (wx.login获取)
    - **user_info**: 微信用户信息 (可选)
    """
    try:
        # 获取微信openid
        session_info = await WechatService.code2session(wechat_data.code)
        openid = session_info.get("openid")

        if not openid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="获取微信信息失败"
            )

        # 查找用户
        user = await AuthService.get_user_by_openid(db, openid)

        if not user:
            # 新用户，创建账号
            nickname = None
            avatar = None
            if wechat_data.user_info:
                nickname = wechat_data.user_info.get("nickName")
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

        if user.status != "active":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="账号已被禁用"
            )

        access_token, expires_in = AuthService.create_token(user)

        return Token(
            access_token=access_token,
            expires_in=expires_in,
            user=UserResponse.model_validate(user)
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"微信登录失败: {str(e)}"
        )


@router.post("/login/wechat-phone", response_model=Token, summary="微信手机号登录")
async def wechat_phone_login(data: WechatPhoneLogin, db: AsyncSession = Depends(get_db)):
    """
    微信手机号快捷登录
    - **code**: 微信登录code
    - **phone_code**: 获取手机号的code
    """
    try:
        # 获取微信openid
        session_info = await WechatService.code2session(data.code)
        openid = session_info.get("openid")

        # 获取access_token
        access_token_wx = await WechatService.get_access_token()

        # 获取手机号
        phone = await WechatService.get_phone_number(data.phone_code, access_token_wx)

        if not phone:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="获取手机号失败"
            )

        # 查找用户 (优先手机号)
        user = await AuthService.get_user_by_phone(db, phone)

        if user:
            # 已有用户，绑定微信
            if not user.wechat_openid and openid:
                await AuthService.bind_wechat(db, user, openid)
                await db.commit()
        else:
            # 新用户
            user = await AuthService.create_user(
                db=db,
                phone=phone,
                password="",
                role="parent",
                openid=openid
            )
            await db.commit()

        if user.status != "active":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="账号已被禁用"
            )

        access_token, expires_in = AuthService.create_token(user)

        return Token(
            access_token=access_token,
            expires_in=expires_in,
            user=UserResponse.model_validate(user)
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"登录失败: {str(e)}"
        )


# ============ 密码管理 ============

@router.post("/password/reset", summary="重置密码")
async def reset_password(data: PasswordReset, db: AsyncSession = Depends(get_db)):
    """
    通过短信验证码重置密码
    """
    # 验证验证码
    is_valid = await SmsService.verify_code(data.phone, data.code)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="验证码错误或已过期"
        )

    # 查找用户
    user = await AuthService.get_user_by_phone(db, data.phone)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )

    # 更新密码
    await AuthService.update_password(db, user, data.new_password)
    await db.commit()

    return {"message": "密码重置成功"}


@router.post("/password/change", summary="修改密码")
async def change_password(
    data: PasswordChange,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    修改密码 (需要登录)
    """
    user = await AuthService.get_user_by_id(db, current_user["user_id"])
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )

    # 验证旧密码
    if not user.password_hash or not verify_password(data.old_password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="旧密码错误"
        )

    # 更新密码
    await AuthService.update_password(db, user, data.new_password)
    await db.commit()

    return {"message": "密码修改成功"}


# ============ 用户信息 ============

@router.get("/me", response_model=UserDetailResponse, summary="获取当前用户信息")
async def get_current_user_info(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取当前登录用户信息
    """
    user = await AuthService.get_user_by_id(db, current_user["user_id"])
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
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

    # 加载关联信息
    if user.student:
        response.student = StudentResponse.model_validate(user.student)
    if user.coach:
        response.coach = CoachResponse.model_validate(user.coach)

    return response


@router.put("/me", response_model=UserResponse, summary="更新用户信息")
async def update_user_info(
    data: UserUpdate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    更新当前用户信息
    """
    user = await AuthService.get_user_by_id(db, current_user["user_id"])
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )

    if data.nickname is not None:
        user.nickname = data.nickname
    if data.avatar is not None:
        user.avatar = data.avatar

    await db.commit()
    await db.refresh(user)

    return UserResponse.model_validate(user)


@router.post("/logout", summary="退出登录")
async def logout(current_user: dict = Depends(get_current_user)):
    """
    退出登录
    """
    # TODO: 如果使用Redis存储token，这里需要将token加入黑名单
    return {"message": "退出成功"}


# ============ 学员管理 (家长端) ============

@router.post("/students", response_model=StudentResponse, summary="添加学员")
async def add_student(
    data: StudentRegister,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    家长为孩子添加学员档案
    """
    if current_user["role"] not in ["parent", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权限操作"
        )

    # 创建学员档案
    student = await AuthService.create_student_profile(
        db=db,
        user_id=None,  # 学员可以没有独立账号
        name=data.name,
        gender=data.gender,
        birth_date=data.birth_date,
        parent_id=current_user["user_id"]
    )

    await db.commit()

    return StudentResponse.model_validate(student)
