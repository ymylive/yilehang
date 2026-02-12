"""
RBAC (Role-Based Access Control) 数据模型
多角色权限系统核心表
"""

from datetime import datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Table, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from typing import Any

    User = Any

# 用户-角色关联表（多对多）
user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
    Column("role_id", Integer, ForeignKey("roles.id", ondelete="CASCADE"), nullable=False),
    Column("is_active", Boolean, default=True, comment="是否为当前激活角色"),
    Column("created_at", DateTime, default=lambda: datetime.now(timezone.utc)),
)


# 角色-权限关联表（多对多）
role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("role_id", Integer, ForeignKey("roles.id", ondelete="CASCADE"), nullable=False),
    Column(
        "permission_id", Integer, ForeignKey("permissions.id", ondelete="CASCADE"), nullable=False
    ),
    Column("created_at", DateTime, default=lambda: datetime.now(timezone.utc)),
)


# 角色-菜单关联表（多对多）
role_menus = Table(
    "role_menus",
    Base.metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("role_id", Integer, ForeignKey("roles.id", ondelete="CASCADE"), nullable=False),
    Column("menu_id", Integer, ForeignKey("menus.id", ondelete="CASCADE"), nullable=False),
    Column("created_at", DateTime, default=lambda: datetime.now(timezone.utc)),
)


class RoleType(str, Enum):
    """角色类型"""

    ADMIN = "admin"
    COACH = "coach"
    PARENT = "parent"
    STUDENT = "student"
    MERCHANT = "merchant"


class Role(Base):
    """角色表"""

    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, index=True, comment="角色代码")
    name: Mapped[str] = mapped_column(String(100), comment="角色名称")
    description: Mapped[Optional[str]] = mapped_column(Text, comment="角色描述")
    is_system: Mapped[bool] = mapped_column(Boolean, default=False, comment="是否系统内置角色")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, comment="是否启用")
    sort_order: Mapped[int] = mapped_column(Integer, default=0, comment="排序")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # 关系
    users: Mapped[List["User"]] = relationship("User", secondary=user_roles, back_populates="roles")
    permissions: Mapped[List["Permission"]] = relationship(
        "Permission", secondary=role_permissions, back_populates="roles"
    )
    menus: Mapped[List["Menu"]] = relationship("Menu", secondary=role_menus, back_populates="roles")


class PermissionType(str, Enum):
    """权限类型"""

    API = "api"  # API接口权限
    PAGE = "page"  # 页面访问权限
    BUTTON = "button"  # 按钮操作权限
    DATA = "data"  # 数据权限


class Permission(Base):
    """权限表"""

    __tablename__ = "permissions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(100), unique=True, index=True, comment="权限代码")
    name: Mapped[str] = mapped_column(String(100), comment="权限名称")
    type: Mapped[str] = mapped_column(
        String(20), default=PermissionType.API.value, comment="权限类型"
    )
    resource: Mapped[Optional[str]] = mapped_column(
        String(200), comment="资源路径（API路径/页面路径）"
    )
    action: Mapped[Optional[str]] = mapped_column(
        String(50), comment="操作（GET/POST/PUT/DELETE等）"
    )
    description: Mapped[Optional[str]] = mapped_column(Text, comment="权限描述")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, comment="是否启用")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # 关系
    roles: Mapped[List["Role"]] = relationship(
        "Role", secondary=role_permissions, back_populates="permissions"
    )


class MenuType(str, Enum):
    """菜单类型"""

    DIRECTORY = "directory"  # 目录
    MENU = "menu"  # 菜单
    BUTTON = "button"  # 按钮


class Menu(Base):
    """菜单表"""

    __tablename__ = "menus"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    parent_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("menus.id"), comment="父菜单ID"
    )
    code: Mapped[str] = mapped_column(String(100), unique=True, index=True, comment="菜单代码")
    name: Mapped[str] = mapped_column(String(100), comment="菜单名称")
    type: Mapped[str] = mapped_column(String(20), default=MenuType.MENU.value, comment="菜单类型")
    path: Mapped[Optional[str]] = mapped_column(String(200), comment="路由路径")
    component: Mapped[Optional[str]] = mapped_column(String(200), comment="组件路径")
    icon: Mapped[Optional[str]] = mapped_column(String(100), comment="图标")
    sort_order: Mapped[int] = mapped_column(Integer, default=0, comment="排序")
    is_visible: Mapped[bool] = mapped_column(Boolean, default=True, comment="是否可见")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, comment="是否启用")
    permission_code: Mapped[Optional[str]] = mapped_column(String(100), comment="关联权限代码")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # 关系
    roles: Mapped[List["Role"]] = relationship("Role", secondary=role_menus, back_populates="menus")
    children: Mapped[List["Menu"]] = relationship(
        "Menu", back_populates="parent", foreign_keys=[parent_id]
    )
    parent: Mapped[Optional["Menu"]] = relationship(
        "Menu", back_populates="children", remote_side=[id], foreign_keys=[parent_id]
    )
