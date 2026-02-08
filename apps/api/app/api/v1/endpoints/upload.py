"""
文件上传 API
"""
import os
import uuid
import httpx
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.core.config import settings
from app.models.user import User

router = APIRouter()

# 上传目录
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "uploads")
AVATAR_DIR = os.path.join(UPLOAD_DIR, "avatars")

# 确保目录存在
os.makedirs(AVATAR_DIR, exist_ok=True)

# 允许的图片类型
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB


@router.post("/avatar")
async def upload_avatar(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """上传头像"""
    # 验证文件类型
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(status_code=400, detail="不支持的图片格式，请上传 JPG/PNG/GIF/WebP 格式")

    # 读取文件内容
    content = await file.read()

    # 验证文件大小
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="文件大小不能超过 5MB")

    # 生成文件名
    ext = file.filename.split(".")[-1] if "." in file.filename else "jpg"
    filename = f"{current_user.id}_{uuid.uuid4().hex[:8]}.{ext}"
    filepath = os.path.join(AVATAR_DIR, filename)

    # 保存文件
    with open(filepath, "wb") as f:
        f.write(content)

    # 生成 URL
    avatar_url = f"/uploads/avatars/{filename}"

    # 更新用户头像
    current_user.avatar = avatar_url
    await db.commit()

    return {
        "url": avatar_url,
        "message": "头像上传成功"
    }


@router.post("/avatar/sync-wechat")
async def sync_wechat_avatar(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """同步微信头像（需要微信授权）"""
    # 检查用户是否绑定微信
    if not current_user.wechat_openid:
        raise HTTPException(status_code=400, detail="请先绑定微信账号")

    # 如果用户已有微信头像URL，直接使用
    # 实际场景中，微信头像URL在登录时已经获取并存储
    if current_user.avatar and "wx.qlogo.cn" in current_user.avatar:
        return {
            "url": current_user.avatar,
            "message": "已使用微信头像"
        }

    raise HTTPException(status_code=400, detail="请通过微信登录获取头像")


@router.post("/image")
async def upload_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    """上传通用图片（用于聊天等）"""
    # 验证文件类型
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(status_code=400, detail="不支持的图片格式")

    # 读取文件内容
    content = await file.read()

    # 验证文件大小
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="文件大小不能超过 5MB")

    # 生成文件名
    date_path = datetime.now().strftime("%Y%m")
    image_dir = os.path.join(UPLOAD_DIR, "images", date_path)
    os.makedirs(image_dir, exist_ok=True)

    ext = file.filename.split(".")[-1] if "." in file.filename else "jpg"
    filename = f"{uuid.uuid4().hex}.{ext}"
    filepath = os.path.join(image_dir, filename)

    # 保存文件
    with open(filepath, "wb") as f:
        f.write(content)

    # 生成 URL
    image_url = f"/uploads/images/{date_path}/{filename}"

    return {
        "url": image_url,
        "message": "图片上传成功"
    }
