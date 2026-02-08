# Bug 跟踪报告

**项目**: 易乐航 ITS 智慧体教云平台
**模块**: 多角色权限系统 (RBAC)
**更新日期**: 2026-02-08

---

## 概览

| 状态 | 数量 |
|------|------|
| 已修复 | 3 |
| 待修复 | 0 |
| 已知问题 | 2 |
| 总计 | 5 |

---

## 已修复 Bug

### BUG-001: 旧用户无 RBAC 角色记录时 API 报错

**严重程度**: 高
**状态**: 已修复
**发现日期**: 2026-02-07
**修复日期**: 2026-02-08

**描述**:
旧用户在 `user_roles` 表中没有记录时，调用 `/api/v1/user/roles` 返回空数组，导致前端角色切换功能异常。

**根因**:
RBAC 系统上线前的用户没有自动分配角色记录。

**修复方案**:
在 `roles.py` 中添加兼容逻辑，当 RBAC 表无记录时，回退到 `User.role` 字段构造角色响应。

**修复代码**:
```python
# apps/api/app/api/v1/endpoints/roles.py:56-68
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
```

---

### BUG-002: 角色切换后 Token 未更新

**严重程度**: 中
**状态**: 已修复
**发现日期**: 2026-02-07
**修复日期**: 2026-02-08

**描述**:
用户切换角色后，旧 Token 仍然有效，导致权限检查使用旧角色。

**根因**:
`switch-role` 端点未返回新 Token。

**修复方案**:
切换角色后生成新的 JWT Token，包含更新后的 `active_role` 和 `roles` 信息。

**修复代码**:
```python
# apps/api/app/api/v1/endpoints/roles.py:209-225
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
```

---

### BUG-003: 菜单树构建时子菜单丢失

**严重程度**: 中
**状态**: 已修复
**发现日期**: 2026-02-08
**修复日期**: 2026-02-08

**描述**:
当父菜单不在用户可见菜单列表中时，其子菜单也会丢失。

**根因**:
`_build_menu_tree` 函数只处理 `menu_map` 中存在的父菜单。

**修复方案**:
修改树构建逻辑，当父菜单不存在时，将子菜单提升为根节点。

**修复代码**:
```python
# apps/api/app/api/v1/endpoints/roles.py:262-268
for m in menus:
    node = menu_map[m.id]
    if m.parent_id and m.parent_id in menu_map:
        menu_map[m.parent_id].children.append(node)
    else:
        roots.append(node)
```

---

## 已知问题

### KNOWN-001: Admin 角色权限查询返回所有权限

**严重程度**: 低
**状态**: 已知问题 (设计如此)

**描述**:
Admin 角色调用 `/api/v1/user/permissions` 时返回系统所有权限，而非通过 `role_permissions` 表关联的权限。

**影响**:
无负面影响，这是设计行为。Admin 作为超级管理员应拥有所有权限。

**备注**:
如需限制 Admin 权限，可修改 `get_permissions` 函数移除 Admin 特殊处理。

---

### KNOWN-002: 角色切换不会自动刷新前端菜单

**严重程度**: 低
**状态**: 已知问题

**描述**:
用户切换角色后，前端需要手动调用 `/api/v1/user/menus` 刷新菜单，否则显示旧角色菜单。

**影响**:
用户体验略有影响，但功能正常。

**建议**:
前端在收到 `switch-role` 响应后，自动调用菜单刷新接口。

---

## 测试覆盖

所有已修复 Bug 均已添加回归测试：

| Bug ID | 测试用例 | 文件 |
|--------|---------|------|
| BUG-001 | test_get_roles_fallback_to_legacy_role | test_role_api.py |
| BUG-002 | test_switch_role_success | test_role_api.py |
| BUG-003 | test_menu_tree_structure | test_role_api.py |

---

**报告维护**: Claude Code
**最后更新**: 2026-02-08
