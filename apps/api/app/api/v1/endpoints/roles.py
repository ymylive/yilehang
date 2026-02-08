"""
角色权限管理 API
- GET /roles          获取当前用户所有角色
- GET /permissions    获取当前用户权限列表
- GET /menus          获取当前用户可见菜单
- POST /switch-role   切换当前激活角色
"""
import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.security import create_access_token, get_current_user
from app.middleware.role_auth import (
    get_current_user_with_roles,
    get_user_permissions,
)
from app.models.user import User
from app.models.rbac import (
    Role, Permission, Menu,
    user_roles, role_permissions, role_menus,
)
from app.schemas.role import (
    RoleResponse, UserRolesResponse,
    PermissionResponse, UserPermissionsResponse,
    MenuResponse, UserMenusResponse,
    SwitchRoleRequest, SwitchRoleResponse,
)

logger = logging.getLogger(__name__)
router = APIRouter()


# ============ 角色查询 ============

@router.get("/roles", response_model=UserRolesResponse, summary="获取当前用户所有角色")
async def get_user_roles(
    current_user: dict = Depends(get_current_user_with_roles),
    db: AsyncSession = Depends(get_db),
):
    """返回当前用户拥有的所有角色列表"""
    user_id = current_user["user_id"]

    result = await db.execute(
        select(Role)
        .join(user_roles, user_roles.c.role_id == Role.id)
        .where(user_roles.c.user_id == user_id, Role.is_active == True)
        .order_by(Role.sort_order)
    )
    roles = result.scalars().all()

    # 兼容旧数据：如果 RBAC 表中无记录，从 User.role 字段构造
    if not roles:
        legacy_role = current_user.get("role", "parent")
        return UserRolesResponse(
            data=[RoleResponse(
                id=0,
                code=legacy_role,
                name=_role_display_name(legacy_role),
                is_system=True,
                is_active=True,
                sort_order=0,
            )]
        )

    return UserRolesResponse(
        data=[RoleResponse.model_validate(r) for r in roles]
    )


# ============ 权限查询 ============

@router.get("/permissions", response_model=UserPermissionsResponse, summary="获取当前用户权限列表")
async def get_permissions(
    current_user: dict = Depends(get_current_user_with_roles),
    db: AsyncSession = Depends(get_db),
):
    """返回当前用户（基于所有角色）的权限列表"""
    user_id = current_user["user_id"]

    # admin 返回所有权限
    if "admin" in current_user.get("roles", []):
        result = await db.execute(
            select(Permission).where(Permission.is_active == True)
        )
        perms = result.scalars().all()
        return UserPermissionsResponse(
            data=[PermissionResponse.model_validate(p) for p in perms]
        )

    result = await db.execute(
        select(Permission)
        .join(role_permissions, role_permissions.c.permission_id == Permission.id)
        .join(Role, Role.id == role_permissions.c.role_id)
        .join(user_roles, user_roles.c.role_id == Role.id)
        .where(
            user_roles.c.user_id == user_id,
            Role.is_active == True,
            Permission.is_active == True,
        )
        .distinct()
    )
    perms = result.scalars().all()

    return UserPermissionsResponse(
        data=[PermissionResponse.model_validate(p) for p in perms]
    )


# ============ 菜单查询 ============

@router.get("/menus", response_model=UserMenusResponse, summary="获取当前用户可见菜单")
async def get_menus(
    current_user: dict = Depends(get_current_user_with_roles),
    db: AsyncSession = Depends(get_db),
):
    """返回当前用户可见的菜单树"""
    user_id = current_user["user_id"]

    # admin 返回所有菜单
    if "admin" in current_user.get("roles", []):
        result = await db.execute(
            select(Menu)
            .where(Menu.is_active == True, Menu.is_visible == True)
            .order_by(Menu.sort_order)
        )
        all_menus = result.scalars().all()
    else:
        result = await db.execute(
            select(Menu)
            .join(role_menus, role_menus.c.menu_id == Menu.id)
            .join(Role, Role.id == role_menus.c.role_id)
            .join(user_roles, user_roles.c.role_id == Role.id)
            .where(
                user_roles.c.user_id == user_id,
                Role.is_active == True,
                Menu.is_active == True,
                Menu.is_visible == True,
            )
            .distinct()
            .order_by(Menu.sort_order)
        )
        all_menus = result.scalars().all()

    # 构建菜单树
    menu_tree = _build_menu_tree(all_menus)

    return UserMenusResponse(data=menu_tree)


# ============ 切换角色 ============

@router.post("/switch-role", response_model=SwitchRoleResponse, summary="切换当前激活角色")
async def switch_role(
    data: SwitchRoleRequest,
    current_user: dict = Depends(get_current_user_with_roles),
    db: AsyncSession = Depends(get_db),
):
    """切换用户当前激活角色，返回新的 access_token"""
    user_id = current_user["user_id"]
    target_code = data.role_code

    # 验证用户是否拥有目标角色
    user_role_codes = current_user.get("roles", [])
    if target_code not in user_role_codes:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"您没有 {target_code} 角色",
        )

    # 查找目标角色 ID
    role_result = await db.execute(
        select(Role).where(Role.code == target_code, Role.is_active == True)
    )
    target_role = role_result.scalar_one_or_none()

    if target_role:
        # 将所有角色设为非激活
        await db.execute(
            update(user_roles)
            .where(user_roles.c.user_id == user_id)
            .values(is_active=False)
        )
        # 将目标角色设为激活
        await db.execute(
            update(user_roles)
            .where(
                user_roles.c.user_id == user_id,
                user_roles.c.role_id == target_role.id,
            )
            .values(is_active=True)
        )

    # 同时更新 User.role 字段（兼容旧逻辑）
    await db.execute(
        update(User).where(User.id == user_id).values(role=target_code)
    )

    await db.commit()

    # 生成新 token（包含新的 active_role）
    from datetime import timedelta
    from app.core.config import settings

    access_token = create_access_token(
        data={
            "sub": str(user_id),
            "role": target_code,
            "roles": user_role_codes,
        },
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    return SwitchRoleResponse(
        data={
            "access_token": access_token,
            "token_type": "bearer",
            "active_role": target_code,
            "roles": user_role_codes,
        }
    )


# ============ 辅助函数 ============

def _role_display_name(code: str) -> str:
    """角色代码 -> 显示名称"""
    mapping = {
        "admin": "管理员",
        "coach": "教练",
        "parent": "家长",
        "student": "学员",
        "merchant": "商家",
    }
    return mapping.get(code, code)


def _build_menu_tree(menus: list) -> List[MenuResponse]:
    """将扁平菜单列表构建为树形结构"""
    menu_map = {}
    for m in menus:
        menu_map[m.id] = MenuResponse(
            id=m.id,
            parent_id=m.parent_id,
            code=m.code,
            name=m.name,
            type=m.type,
            path=m.path,
            component=m.component,
            icon=m.icon,
            sort_order=m.sort_order,
            is_visible=m.is_visible,
            is_active=m.is_active,
            permission_code=m.permission_code,
            children=[],
        )

    roots = []
    for m in menus:
        node = menu_map[m.id]
        if m.parent_id and m.parent_id in menu_map:
            menu_map[m.parent_id].children.append(node)
        else:
            roots.append(node)

    return roots
