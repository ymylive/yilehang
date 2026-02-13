"""
角色权限中间件与依赖注入
提供 require_role / require_permission 装饰器和 FastAPI 依赖
"""

import logging
from typing import List, Optional

from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.rbac import Permission, Role, role_permissions, user_roles

logger = logging.getLogger(__name__)


async def get_current_user_with_roles(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """获取当前用户及其所有角色信息（FastAPI 依赖）"""
    user_id = current_user["user_id"]

    # 查询用户的所有角色
    result = await db.execute(
        select(Role)
        .join(user_roles, user_roles.c.role_id == Role.id)
        .where(user_roles.c.user_id == user_id, Role.is_active.is_(True))
    )
    roles = result.scalars().all()

    role_codes = [r.code for r in roles]

    # 如果用户在 RBAC 表中没有角色记录，回退到 User.role 字段（兼容旧数据）
    if not role_codes:
        role_codes = [current_user.get("role", "parent")]

    # 查找当前激活角色
    active_result = await db.execute(
        select(Role.code)
        .join(user_roles, user_roles.c.role_id == Role.id)
        .where(
            user_roles.c.user_id == user_id,
            user_roles.c.is_active.is_(True),
            Role.is_active.is_(True),
        )
    )
    active_role = active_result.scalar_one_or_none()
    if not active_role:
        active_role = role_codes[0] if role_codes else current_user.get("role", "parent")

    return {
        **current_user,
        "roles": role_codes,
        "active_role": active_role,
    }


async def get_user_permissions(
    user_id: int,
    db: AsyncSession,
    role_codes: Optional[List[str]] = None,
) -> List[str]:
    """获取用户所有权限代码列表"""
    query = (
        select(Permission.code)
        .join(role_permissions, role_permissions.c.permission_id == Permission.id)
        .join(Role, Role.id == role_permissions.c.role_id)
        .join(user_roles, user_roles.c.role_id == Role.id)
        .where(
            user_roles.c.user_id == user_id,
            Role.is_active.is_(True),
            Permission.is_active.is_(True),
        )
    )
    if role_codes:
        query = query.where(Role.code.in_(role_codes))

    result = await db.execute(query)
    return list(result.scalars().all())


def require_role(allowed_roles: List[str]):
    """
    角色验证依赖工厂。

    用法:
        @router.get("/admin/users", dependencies=[Depends(require_role(["admin"]))])
        async def list_users(...): ...

    或作为参数依赖:
        async def endpoint(user=Depends(require_role(["admin", "coach"]))):
    """

    async def _dependency(
        current_user: dict = Depends(get_current_user_with_roles),
    ) -> dict:
        user_roles_list = current_user.get("roles", [])

        # 检查用户是否拥有任一允许的角色
        has_role = any(r in allowed_roles for r in user_roles_list)
        if not has_role:
            logger.warning(
                "Role denied: user=%s roles=%s required=%s",
                current_user["user_id"],
                user_roles_list,
                allowed_roles,
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"需要以下角色之一: {', '.join(allowed_roles)}",
            )
        return current_user

    return _dependency


def require_permission(required_permissions: List[str]):
    """
    权限验证依赖工厂。

    用法:
        @router.post("/courses", dependencies=[Depends(require_permission(["course:create"]))])
        async def create_course(...): ...
    """

    async def _dependency(
        current_user: dict = Depends(get_current_user_with_roles),
        db: AsyncSession = Depends(get_db),
    ) -> dict:
        # admin 角色拥有所有权限
        if "admin" in current_user.get("roles", []):
            return current_user

        user_id = current_user["user_id"]
        user_perms = await get_user_permissions(user_id, db)

        # 检查是否拥有所有必需权限
        missing = [p for p in required_permissions if p not in user_perms]
        if missing:
            logger.warning(
                "Permission denied: user=%s missing=%s",
                user_id,
                missing,
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"缺少权限: {', '.join(missing)}",
            )
        return current_user

    return _dependency
