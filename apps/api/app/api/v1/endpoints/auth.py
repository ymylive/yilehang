"""
认证相关API
"""
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core import get_db, settings, verify_password, get_password_hash, create_access_token
from app.models import User
from app.schemas import UserCreate, UserLogin, WechatLogin, Token, UserResponse

router = APIRouter()


@router.post("/register", response_model=Token)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    """用户注册"""
    # 检查手机号是否已存在
    result = await db.execute(select(User).where(User.phone == user_data.phone))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该手机号已注册"
        )

    # 创建用户
    user = User(
        phone=user_data.phone,
        password_hash=get_password_hash(user_data.password),
        role=user_data.role,
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)

    # 生成Token
    access_token = create_access_token(
        data={"sub": str(user.id), "role": user.role}
    )

    return Token(
        access_token=access_token,
        user=UserResponse.model_validate(user)
    )


@router.post("/login", response_model=Token)
async def login(login_data: UserLogin, db: AsyncSession = Depends(get_db)):
    """手机号密码登录"""
    result = await db.execute(select(User).where(User.phone == login_data.phone))
    user = result.scalar_one_or_none()

    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="手机号或密码错误"
        )

    if user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="账号已被禁用"
        )

    access_token = create_access_token(
        data={"sub": str(user.id), "role": user.role}
    )

    return Token(
        access_token=access_token,
        user=UserResponse.model_validate(user)
    )


@router.post("/wechat-login", response_model=Token)
async def wechat_login(wechat_data: WechatLogin, db: AsyncSession = Depends(get_db)):
    """微信登录"""
    # TODO: 调用微信API获取openid
    # 这里需要实现微信登录逻辑
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="微信登录功能开发中"
    )


@router.post("/refresh", response_model=Token)
async def refresh_token(current_user: dict = Depends(get_db)):
    """刷新Token"""
    # TODO: 实现Token刷新逻辑
    pass
