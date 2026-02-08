"""multi role permission system

Revision ID: 001_multi_role
Revises:
Create Date: 2026-02-08

Creates:
  - roles: 角色定义表
  - permissions: 权限定义表
  - menus: 菜单/页面配置表
  - user_roles: 用户-角色关联表
  - role_permissions: 角色-权限关联表
  - role_menus: 角色-菜单关联表
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "001_multi_role"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- roles ---
    op.create_table(
        "roles",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("code", sa.String(50), nullable=False, comment="角色代码"),
        sa.Column("name", sa.String(100), nullable=False, comment="角色名称"),
        sa.Column("description", sa.Text(), nullable=True, comment="角色描述"),
        sa.Column("is_system", sa.Boolean(), server_default=sa.text("false"), comment="是否系统内置角色"),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), comment="是否启用"),
        sa.Column("sort_order", sa.Integer(), server_default=sa.text("0"), comment="排序"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index("ix_roles_code", "roles", ["code"], unique=True)

    # --- permissions ---
    op.create_table(
        "permissions",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("code", sa.String(100), nullable=False, comment="权限代码"),
        sa.Column("name", sa.String(100), nullable=False, comment="权限名称"),
        sa.Column("type", sa.String(20), server_default="api", comment="权限类型: api/page/button/data"),
        sa.Column("resource", sa.String(200), nullable=True, comment="资源路径"),
        sa.Column("action", sa.String(50), nullable=True, comment="操作"),
        sa.Column("description", sa.Text(), nullable=True, comment="权限描述"),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), comment="是否启用"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index("ix_permissions_code", "permissions", ["code"], unique=True)

    # --- menus ---
    op.create_table(
        "menus",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("parent_id", sa.Integer(), sa.ForeignKey("menus.id", ondelete="SET NULL"), nullable=True, comment="父菜单ID"),
        sa.Column("code", sa.String(100), nullable=False, comment="菜单代码"),
        sa.Column("name", sa.String(100), nullable=False, comment="菜单名称"),
        sa.Column("type", sa.String(20), server_default="menu", comment="菜单类型: directory/menu/button"),
        sa.Column("path", sa.String(200), nullable=True, comment="路由路径"),
        sa.Column("component", sa.String(200), nullable=True, comment="组件路径"),
        sa.Column("icon", sa.String(100), nullable=True, comment="图标"),
        sa.Column("sort_order", sa.Integer(), server_default=sa.text("0"), comment="排序"),
        sa.Column("is_visible", sa.Boolean(), server_default=sa.text("true"), comment="是否可见"),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), comment="是否启用"),
        sa.Column("permission_code", sa.String(100), nullable=True, comment="关联权限代码"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index("ix_menus_code", "menus", ["code"], unique=True)
    op.create_index("ix_menus_parent_id", "menus", ["parent_id"])

    # --- user_roles (many-to-many) ---
    op.create_table(
        "user_roles",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("role_id", sa.Integer(), sa.ForeignKey("roles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), comment="是否为当前激活角色"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
    )
    op.create_index("ix_user_roles_user_id", "user_roles", ["user_id"])
    op.create_index("ix_user_roles_role_id", "user_roles", ["role_id"])
    op.create_unique_constraint("uq_user_roles_user_role", "user_roles", ["user_id", "role_id"])

    # --- role_permissions (many-to-many) ---
    op.create_table(
        "role_permissions",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("role_id", sa.Integer(), sa.ForeignKey("roles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("permission_id", sa.Integer(), sa.ForeignKey("permissions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
    )
    op.create_index("ix_role_permissions_role_id", "role_permissions", ["role_id"])
    op.create_unique_constraint("uq_role_permissions", "role_permissions", ["role_id", "permission_id"])

    # --- role_menus (many-to-many) ---
    op.create_table(
        "role_menus",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("role_id", sa.Integer(), sa.ForeignKey("roles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("menu_id", sa.Integer(), sa.ForeignKey("menus.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
    )
    op.create_index("ix_role_menus_role_id", "role_menus", ["role_id"])
    op.create_unique_constraint("uq_role_menus", "role_menus", ["role_id", "menu_id"])


def downgrade() -> None:
    op.drop_table("role_menus")
    op.drop_table("role_permissions")
    op.drop_table("user_roles")
    op.drop_table("menus")
    op.drop_table("permissions")
    op.drop_table("roles")
