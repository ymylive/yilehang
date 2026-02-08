"""
角色权限初始数据脚本
运行方式: python -m scripts.seed_role_permissions

创建:
  - 4个系统角色: admin, coach, parent, student
  - 各角色权限配置
  - 各角色菜单配置
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select, delete
from app.core.database import AsyncSessionLocal
from app.models.rbac import (
    Role, Permission, Menu,
    role_permissions, role_menus,
    PermissionType, MenuType,
)


# ============ 角色定义 ============
ROLES_DATA = [
    {
        "code": "admin",
        "name": "管理员",
        "description": "系统管理员，拥有所有权限",
        "is_system": True,
        "sort_order": 1,
    },
    {
        "code": "coach",
        "name": "教练",
        "description": "教练角色，管理课程和学员",
        "is_system": True,
        "sort_order": 2,
    },
    {
        "code": "parent",
        "name": "家长",
        "description": "家长角色，管理孩子的课程预约",
        "is_system": True,
        "sort_order": 3,
    },
    {
        "code": "student",
        "name": "学员",
        "description": "学员角色，查看课程和成长档案",
        "is_system": True,
        "sort_order": 4,
    },
    {
        "code": "merchant",
        "name": "商家",
        "description": "合作商家，管理兑换商品",
        "is_system": True,
        "sort_order": 5,
    },
]


# ============ 权限定义 ============
PERMISSIONS_DATA = [
    # --- 用户管理 ---
    {"code": "user:list", "name": "查看用户列表", "type": PermissionType.API, "resource": "/api/v1/users", "action": "GET"},
    {"code": "user:create", "name": "创建用户", "type": PermissionType.API, "resource": "/api/v1/users", "action": "POST"},
    {"code": "user:update", "name": "更新用户", "type": PermissionType.API, "resource": "/api/v1/users/*", "action": "PUT"},
    {"code": "user:delete", "name": "删除用户", "type": PermissionType.API, "resource": "/api/v1/users/*", "action": "DELETE"},
    # --- 学员管理 ---
    {"code": "student:list", "name": "查看学员列表", "type": PermissionType.API, "resource": "/api/v1/students", "action": "GET"},
    {"code": "student:detail", "name": "查看学员详情", "type": PermissionType.API, "resource": "/api/v1/students/*", "action": "GET"},
    {"code": "student:create", "name": "创建学员", "type": PermissionType.API, "resource": "/api/v1/students", "action": "POST"},
    {"code": "student:update", "name": "更新学员", "type": PermissionType.API, "resource": "/api/v1/students/*", "action": "PUT"},
    # --- 教练管理 ---
    {"code": "coach:list", "name": "查看教练列表", "type": PermissionType.API, "resource": "/api/v1/coaches", "action": "GET"},
    {"code": "coach:detail", "name": "查看教练详情", "type": PermissionType.API, "resource": "/api/v1/coaches/*", "action": "GET"},
    {"code": "coach:schedule", "name": "管理教练排班", "type": PermissionType.API, "resource": "/api/v1/coaches/*/schedule", "action": "PUT"},
    {"code": "coach:workbench", "name": "教练工作台", "type": PermissionType.PAGE, "resource": "/pages/workbench/index"},
    # --- 预约管理 ---
    {"code": "booking:list", "name": "查看预约列表", "type": PermissionType.API, "resource": "/api/v1/bookings", "action": "GET"},
    {"code": "booking:create", "name": "创建预约", "type": PermissionType.API, "resource": "/api/v1/bookings", "action": "POST"},
    {"code": "booking:cancel", "name": "取消预约", "type": PermissionType.API, "resource": "/api/v1/bookings/*/cancel", "action": "POST"},
    {"code": "booking:confirm", "name": "确认预约", "type": PermissionType.API, "resource": "/api/v1/bookings/*/confirm", "action": "POST"},
    {"code": "booking:complete", "name": "完成预约", "type": PermissionType.API, "resource": "/api/v1/bookings/*/complete", "action": "POST"},
    # --- 课时卡管理 ---
    {"code": "membership:list", "name": "查看课时卡", "type": PermissionType.API, "resource": "/api/v1/memberships", "action": "GET"},
    {"code": "membership:purchase", "name": "购买课时卡", "type": PermissionType.API, "resource": "/api/v1/memberships/purchase", "action": "POST"},
    {"code": "membership:manage", "name": "管理课时卡", "type": PermissionType.API, "resource": "/api/v1/memberships/*", "action": "PUT"},
    # --- 成长档案 ---
    {"code": "growth:view", "name": "查看成长档案", "type": PermissionType.API, "resource": "/api/v1/growth", "action": "GET"},
    {"code": "growth:record", "name": "记录成长数据", "type": PermissionType.API, "resource": "/api/v1/growth", "action": "POST"},
    # --- 评价管理 ---
    {"code": "review:list", "name": "查看评价", "type": PermissionType.API, "resource": "/api/v1/reviews", "action": "GET"},
    {"code": "review:create", "name": "创建评价", "type": PermissionType.API, "resource": "/api/v1/reviews", "action": "POST"},
    {"code": "review:reply", "name": "回复评价", "type": PermissionType.API, "resource": "/api/v1/reviews/*/reply", "action": "POST"},
    # --- 聊天消息 ---
    {"code": "chat:send", "name": "发送消息", "type": PermissionType.API, "resource": "/api/v1/chat", "action": "POST"},
    {"code": "chat:list", "name": "查看消息", "type": PermissionType.API, "resource": "/api/v1/chat", "action": "GET"},
    # --- 能量系统 ---
    {"code": "energy:view", "name": "查看能量", "type": PermissionType.API, "resource": "/api/v1/energy", "action": "GET"},
    {"code": "energy:redeem", "name": "兑换商品", "type": PermissionType.API, "resource": "/api/v1/energy/redeem", "action": "POST"},
    {"code": "energy:manage", "name": "管理能量规则", "type": PermissionType.API, "resource": "/api/v1/energy/rules", "action": "PUT"},
    # --- 商家管理 ---
    {"code": "merchant:list", "name": "查看商家", "type": PermissionType.API, "resource": "/api/v1/merchants", "action": "GET"},
    {"code": "merchant:manage", "name": "管理商家", "type": PermissionType.API, "resource": "/api/v1/merchants/*", "action": "PUT"},
    {"code": "merchant:items", "name": "管理商品", "type": PermissionType.API, "resource": "/api/v1/merchants/*/items", "action": "PUT"},
    # --- 通知管理 ---
    {"code": "notification:list", "name": "查看通知", "type": PermissionType.API, "resource": "/api/v1/notifications", "action": "GET"},
    {"code": "notification:send", "name": "发送通知", "type": PermissionType.API, "resource": "/api/v1/notifications", "action": "POST"},
    # --- 数据看板 ---
    {"code": "dashboard:view", "name": "查看数据看板", "type": PermissionType.PAGE, "resource": "/dashboard"},
    {"code": "dashboard:export", "name": "导出数据", "type": PermissionType.BUTTON, "resource": "/dashboard/export"},
    # --- 系统管理 ---
    {"code": "system:config", "name": "系统配置", "type": PermissionType.API, "resource": "/api/v1/system/config", "action": "PUT"},
    {"code": "system:role", "name": "角色管理", "type": PermissionType.API, "resource": "/api/v1/roles", "action": "PUT"},
]


# ============ 角色-权限映射 ============
ROLE_PERMISSIONS_MAP = {
    "admin": [
        # 管理员拥有所有权限
        "user:list", "user:create", "user:update", "user:delete",
        "student:list", "student:detail", "student:create", "student:update",
        "coach:list", "coach:detail", "coach:schedule", "coach:workbench",
        "booking:list", "booking:create", "booking:cancel", "booking:confirm", "booking:complete",
        "membership:list", "membership:purchase", "membership:manage",
        "growth:view", "growth:record",
        "review:list", "review:create", "review:reply",
        "chat:send", "chat:list",
        "energy:view", "energy:redeem", "energy:manage",
        "merchant:list", "merchant:manage", "merchant:items",
        "notification:list", "notification:send",
        "dashboard:view", "dashboard:export",
        "system:config", "system:role",
    ],
    "coach": [
        # 教练权限
        "student:list", "student:detail",
        "coach:detail", "coach:schedule", "coach:workbench",
        "booking:list", "booking:confirm", "booking:complete",
        "growth:view", "growth:record",
        "review:list", "review:reply",
        "chat:send", "chat:list",
        "notification:list",
    ],
    "parent": [
        # 家长权限
        "student:list", "student:detail", "student:create", "student:update",
        "coach:list", "coach:detail",
        "booking:list", "booking:create", "booking:cancel",
        "membership:list", "membership:purchase",
        "growth:view",
        "review:list", "review:create",
        "chat:send", "chat:list",
        "energy:view", "energy:redeem",
        "merchant:list",
        "notification:list",
    ],
    "student": [
        # 学员权限（较少，主要查看）
        "student:detail",
        "coach:list", "coach:detail",
        "booking:list",
        "membership:list",
        "growth:view",
        "review:list",
        "chat:send", "chat:list",
        "energy:view", "energy:redeem",
        "merchant:list",
        "notification:list",
    ],
    "merchant": [
        # 商家权限
        "merchant:list", "merchant:items",
        "energy:view",
        "notification:list",
    ],
}


# ============ 菜单定义 ============
MENUS_DATA = [
    # --- 学员端菜单 ---
    {"code": "client_home", "name": "首页", "type": MenuType.MENU, "path": "/pages/index/index", "icon": "home", "sort_order": 1},
    {"code": "client_schedule", "name": "课程表", "type": MenuType.MENU, "path": "/pages/schedule/index", "icon": "calendar", "sort_order": 2},
    {"code": "client_training", "name": "训练", "type": MenuType.MENU, "path": "/pages/training/index", "icon": "fitness", "sort_order": 3},
    {"code": "client_growth", "name": "成长", "type": MenuType.MENU, "path": "/pages/growth/index", "icon": "chart", "sort_order": 4},
    {"code": "client_moments", "name": "动态", "type": MenuType.MENU, "path": "/pages/moments/index", "icon": "photo", "sort_order": 5},
    {"code": "client_membership", "name": "会员", "type": MenuType.MENU, "path": "/pages/membership/index", "icon": "vip", "sort_order": 6},
    {"code": "client_energy", "name": "能量", "type": MenuType.MENU, "path": "/pages/energy/index", "icon": "energy", "sort_order": 7},
    {"code": "client_chat", "name": "消息", "type": MenuType.MENU, "path": "/pages/chat/index", "icon": "chat", "sort_order": 8},
    {"code": "client_user", "name": "我的", "type": MenuType.MENU, "path": "/pages/user/index", "icon": "user", "sort_order": 9},
    # --- 教练端菜单 ---
    {"code": "coach_workbench", "name": "工作台", "type": MenuType.MENU, "path": "/pages/workbench/index", "icon": "workbench", "sort_order": 10, "permission_code": "coach:workbench"},
    {"code": "coach_schedule", "name": "排班", "type": MenuType.MENU, "path": "/pages/schedule/index", "icon": "calendar", "sort_order": 11},
    {"code": "coach_students", "name": "学员", "type": MenuType.MENU, "path": "/pages/students/index", "icon": "users", "sort_order": 12},
    {"code": "coach_income", "name": "收入", "type": MenuType.MENU, "path": "/pages/income/index", "icon": "money", "sort_order": 13},
    {"code": "coach_reviews", "name": "评价", "type": MenuType.MENU, "path": "/pages/reviews/index", "icon": "star", "sort_order": 14},
    {"code": "coach_chat", "name": "消息", "type": MenuType.MENU, "path": "/pages/chat/index", "icon": "chat", "sort_order": 15},
    {"code": "coach_user", "name": "我的", "type": MenuType.MENU, "path": "/pages/user/index", "icon": "user", "sort_order": 16},
    # --- 管理后台菜单 ---
    {"code": "admin_dashboard", "name": "数据看板", "type": MenuType.MENU, "path": "/dashboard", "icon": "dashboard", "sort_order": 20, "permission_code": "dashboard:view"},
    {"code": "admin_users", "name": "用户管理", "type": MenuType.DIRECTORY, "path": "/users", "icon": "users", "sort_order": 21},
    {"code": "admin_users_list", "name": "用户列表", "type": MenuType.MENU, "path": "/users/list", "icon": "list", "sort_order": 22, "parent_code": "admin_users", "permission_code": "user:list"},
    {"code": "admin_users_coaches", "name": "教练管理", "type": MenuType.MENU, "path": "/users/coaches", "icon": "coach", "sort_order": 23, "parent_code": "admin_users", "permission_code": "coach:list"},
    {"code": "admin_users_students", "name": "学员管理", "type": MenuType.MENU, "path": "/users/students", "icon": "student", "sort_order": 24, "parent_code": "admin_users", "permission_code": "student:list"},
    {"code": "admin_bookings", "name": "预约管理", "type": MenuType.MENU, "path": "/bookings", "icon": "booking", "sort_order": 25, "permission_code": "booking:list"},
    {"code": "admin_memberships", "name": "课时卡管理", "type": MenuType.MENU, "path": "/memberships", "icon": "card", "sort_order": 26, "permission_code": "membership:manage"},
    {"code": "admin_merchants", "name": "商家管理", "type": MenuType.MENU, "path": "/merchants", "icon": "shop", "sort_order": 27, "permission_code": "merchant:manage"},
    {"code": "admin_system", "name": "系统设置", "type": MenuType.DIRECTORY, "path": "/system", "icon": "setting", "sort_order": 30},
    {"code": "admin_system_roles", "name": "角色权限", "type": MenuType.MENU, "path": "/system/roles", "icon": "role", "sort_order": 31, "parent_code": "admin_system", "permission_code": "system:role"},
    {"code": "admin_system_config", "name": "系统配置", "type": MenuType.MENU, "path": "/system/config", "icon": "config", "sort_order": 32, "parent_code": "admin_system", "permission_code": "system:config"},
]


# ============ 角色-菜单映射 ============
ROLE_MENUS_MAP = {
    "admin": [
        # 管理员可见所有菜单
        "admin_dashboard", "admin_users", "admin_users_list", "admin_users_coaches", "admin_users_students",
        "admin_bookings", "admin_memberships", "admin_merchants",
        "admin_system", "admin_system_roles", "admin_system_config",
    ],
    "coach": [
        # 教练端菜单
        "coach_workbench", "coach_schedule", "coach_students", "coach_income", "coach_reviews", "coach_chat", "coach_user",
    ],
    "parent": [
        # 家长/学员端菜单
        "client_home", "client_schedule", "client_training", "client_growth", "client_moments",
        "client_membership", "client_energy", "client_chat", "client_user",
    ],
    "student": [
        # 学员端菜单（与家长类似）
        "client_home", "client_schedule", "client_training", "client_growth", "client_moments",
        "client_energy", "client_chat", "client_user",
    ],
    "merchant": [
        # 商家端菜单（简化）
        "client_user",
    ],
}


async def clear_rbac_data():
    """清空 RBAC 相关数据"""
    async with AsyncSessionLocal() as db:
        print("清空 RBAC 数据...")
        await db.execute(delete(role_menus))
        await db.execute(delete(role_permissions))
        await db.execute(delete(Menu))
        await db.execute(delete(Permission))
        await db.execute(delete(Role))
        await db.commit()
        print("  RBAC 数据清空完成")


async def seed_roles():
    """创建角色"""
    async with AsyncSessionLocal() as db:
        print("\n创建角色...")
        roles = {}
        for data in ROLES_DATA:
            role = Role(**data)
            db.add(role)
            await db.flush()
            roles[role.code] = role
            print(f"  创建角色: {role.name} ({role.code})")
        await db.commit()
        return roles


async def seed_permissions():
    """创建权限"""
    async with AsyncSessionLocal() as db:
        print("\n创建权限...")
        permissions = {}
        for data in PERMISSIONS_DATA:
            perm = Permission(
                code=data["code"],
                name=data["name"],
                type=data["type"].value if isinstance(data["type"], PermissionType) else data["type"],
                resource=data.get("resource"),
                action=data.get("action"),
                description=data.get("description"),
            )
            db.add(perm)
            await db.flush()
            permissions[perm.code] = perm
        await db.commit()
        print(f"  创建 {len(permissions)} 个权限")
        return permissions


async def seed_menus():
    """创建菜单"""
    async with AsyncSessionLocal() as db:
        print("\n创建菜单...")
        menus = {}
        # 第一轮：创建所有菜单（不设置 parent_id）
        for data in MENUS_DATA:
            menu = Menu(
                code=data["code"],
                name=data["name"],
                type=data["type"].value if isinstance(data["type"], MenuType) else data["type"],
                path=data.get("path"),
                icon=data.get("icon"),
                sort_order=data.get("sort_order", 0),
                permission_code=data.get("permission_code"),
            )
            db.add(menu)
            await db.flush()
            menus[menu.code] = menu
        await db.commit()

        # 第二轮：设置父子关系
        async with AsyncSessionLocal() as db2:
            for data in MENUS_DATA:
                parent_code = data.get("parent_code")
                if parent_code and parent_code in menus:
                    result = await db2.execute(
                        select(Menu).where(Menu.code == data["code"])
                    )
                    menu = result.scalar_one()
                    parent_result = await db2.execute(
                        select(Menu).where(Menu.code == parent_code)
                    )
                    parent = parent_result.scalar_one()
                    menu.parent_id = parent.id
            await db2.commit()

        print(f"  创建 {len(menus)} 个菜单")
        return menus


async def seed_role_permissions():
    """创建角色-权限关联"""
    async with AsyncSessionLocal() as db:
        print("\n创建角色-权限关联...")
        # 获取所有角色和权限
        roles_result = await db.execute(select(Role))
        roles = {r.code: r for r in roles_result.scalars().all()}

        perms_result = await db.execute(select(Permission))
        permissions = {p.code: p for p in perms_result.scalars().all()}

        count = 0
        for role_code, perm_codes in ROLE_PERMISSIONS_MAP.items():
            role = roles.get(role_code)
            if not role:
                continue
            for perm_code in perm_codes:
                perm = permissions.get(perm_code)
                if not perm:
                    continue
                await db.execute(
                    role_permissions.insert().values(role_id=role.id, permission_id=perm.id)
                )
                count += 1
        await db.commit()
        print(f"  创建 {count} 条角色-权限关联")


async def seed_role_menus():
    """创建角色-菜单关联"""
    async with AsyncSessionLocal() as db:
        print("\n创建角色-菜单关联...")
        # 获取所有角色和菜单
        roles_result = await db.execute(select(Role))
        roles = {r.code: r for r in roles_result.scalars().all()}

        menus_result = await db.execute(select(Menu))
        menus = {m.code: m for m in menus_result.scalars().all()}

        count = 0
        for role_code, menu_codes in ROLE_MENUS_MAP.items():
            role = roles.get(role_code)
            if not role:
                continue
            for menu_code in menu_codes:
                menu = menus.get(menu_code)
                if not menu:
                    continue
                await db.execute(
                    role_menus.insert().values(role_id=role.id, menu_id=menu.id)
                )
                count += 1
        await db.commit()
        print(f"  创建 {count} 条角色-菜单关联")


async def main():
    """主函数"""
    print("=" * 60)
    print("角色权限初始数据脚本")
    print("=" * 60)

    await clear_rbac_data()
    await seed_roles()
    await seed_permissions()
    await seed_menus()
    await seed_role_permissions()
    await seed_role_menus()

    print("\n" + "=" * 60)
    print("角色权限数据创建完成！")
    print("=" * 60)
    print("\n角色汇总:")
    for r in ROLES_DATA:
        print(f"  - {r['name']} ({r['code']}): {r['description']}")
    print(f"\n权限总数: {len(PERMISSIONS_DATA)}")
    print(f"菜单总数: {len(MENUS_DATA)}")


if __name__ == "__main__":
    asyncio.run(main())
