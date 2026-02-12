"""
文件上传 API
"""
import os
import uuid
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.concurrency import run_in_threadpool

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter()

# 上传目录
UPLOAD_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
    "uploads",
)
AVATAR_DIR = os.path.join(UPLOAD_DIR, "avatars")

# 确保目录存在
os.makedirs(AVATAR_DIR, exist_ok=True)

# 允许的图片类型
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}
ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
CHUNK_SIZE = 64 * 1024


def _normalize_extension(filename: str | None) -> str:
    if not filename:
        return ""
    return Path(filename).suffix.lower()


def _extract_user_id(current_user_data: dict[str, object]) -> int:
    raw_user_id = current_user_data.get("user_id")
    if isinstance(raw_user_id, int):
        return raw_user_id
    if isinstance(raw_user_id, str) and raw_user_id.isdigit():
        return int(raw_user_id)
    raise HTTPException(status_code=401, detail="无效的用户身份")


def _extension_family(ext: str) -> str:
    if ext in {".jpg", ".jpeg"}:
        return "jpeg"
    if ext == ".png":
        return "png"
    if ext == ".gif":
        return "gif"
    if ext == ".webp":
        return "webp"
    return ""


def _detect_image_family(signature: bytes) -> str:
    if signature.startswith(b"\xff\xd8\xff"):
        return "jpeg"
    if signature.startswith(b"\x89PNG\r\n\x1a\n"):
        return "png"
    if signature.startswith(b"GIF87a") or signature.startswith(b"GIF89a"):
        return "gif"
    if len(signature) >= 12 and signature[:4] == b"RIFF" and signature[8:12] == b"WEBP":
        return "webp"
    return ""


async def _save_upload_stream(file: UploadFile, destination_path: str) -> tuple[int, bytes]:
    total_size = 0
    signature = b""

    with open(destination_path, "wb") as output:
        while True:
            chunk = await file.read(CHUNK_SIZE)
            if not chunk:
                break

            if len(signature) < 32:
                signature += chunk[: 32 - len(signature)]

            total_size += len(chunk)
            if total_size > MAX_FILE_SIZE:
                raise HTTPException(status_code=400, detail="文件大小不能超过 5MB")

            _ = await run_in_threadpool(output.write, chunk)

    return total_size, signature


async def _validate_and_store_image(file: UploadFile, final_path: str):
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400,
            detail="不支持的图片格式，请上传 JPG/PNG/GIF/WebP 格式",
        )

    ext = _normalize_extension(file.filename)
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="文件扩展名不合法，请上传 .jpg/.jpeg/.png/.gif/.webp",
        )

    temp_path = f"{final_path}.tmp"

    try:
        _, signature = await _save_upload_stream(file, temp_path)

        detected_family = _detect_image_family(signature)
        expected_family = _extension_family(ext)
        if not detected_family or detected_family != expected_family:
            raise HTTPException(status_code=400, detail="图片内容校验失败，请上传有效图片")

        await run_in_threadpool(os.replace, temp_path, final_path)
    except Exception:
        if os.path.exists(temp_path):
            await run_in_threadpool(os.remove, temp_path)
        raise
    finally:
        await file.close()


@router.post("/avatar")
async def upload_avatar(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user_data: dict[str, object] = Depends(get_current_user),
):
    """上传头像"""
    from sqlalchemy import select

    # 获取完整用户对象
    user_id = _extract_user_id(current_user_data)
    result = await db.execute(select(User).where(User.id == user_id))
    current_user = result.scalar_one_or_none()
    if not current_user:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 生成文件名
    original_ext = _normalize_extension(file.filename) or ".jpg"
    filename = f"{current_user.id}_{uuid.uuid4().hex[:8]}{original_ext}"
    filepath = os.path.join(AVATAR_DIR, filename)

    # 流式保存并校验图片，避免全量加载到内存。
    await _validate_and_store_image(file, filepath)

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
    current_user_data: dict[str, object] = Depends(get_current_user),
):
    """同步微信头像（需要微信授权）"""
    from sqlalchemy import select

    # 获取完整用户对象
    user_id = _extract_user_id(current_user_data)
    result = await db.execute(select(User).where(User.id == user_id))
    current_user = result.scalar_one_or_none()
    if not current_user:
        raise HTTPException(status_code=404, detail="用户不存在")

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
    _current_user_data: dict[str, object] = Depends(get_current_user),
):
    """上传通用图片（用于聊天等）"""
    # 生成文件名
    date_path = datetime.now().strftime("%Y%m")
    image_dir = os.path.join(UPLOAD_DIR, "images", date_path)
    os.makedirs(image_dir, exist_ok=True)

    original_ext = _normalize_extension(file.filename) or ".jpg"
    filename = f"{uuid.uuid4().hex}{original_ext}"
    filepath = os.path.join(image_dir, filename)

    # 流式保存并校验图片，避免全量加载到内存。
    await _validate_and_store_image(file, filepath)

    # 生成 URL
    image_url = f"/uploads/images/{date_path}/{filename}"

    return {
        "url": image_url,
        "message": "图片上传成功"
    }
