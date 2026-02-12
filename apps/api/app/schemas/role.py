"""
RBAC 角色权限相关 schemas
"""
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

# ============ Role ============

class RoleBase(BaseModel):
    """角色基础 schema"""
    code: str = Field(..., description="角色代码")
    name: str = Field(..., description="角色名称")
    description: Optional[str] = Field(None, description="角色描述")


class RoleResponse(RoleBase):
    """角色响应"""
    id: int
    is_system: bool = False
    is_active: bool = True
    sort_order: int = 0

    model_config = ConfigDict(from_attributes=True)


class UserRolesResponse(BaseModel):
    """用户角色列表响应"""
    code: int = 0
    message: str = "success"
    data: List[RoleResponse] = []


# ============ Permission ============

class PermissionBase(BaseModel):
    """权限基础 schema"""
    code: str = Field(..., description="权限代码")
    name: str = Field(..., description="权限名称")
    type: str = Field(default="api", description="权限类型: api/page/button/data")
    resource: Optional[str] = Field(None, description="资源路径")
    action: Optional[str] = Field(None, description="操作")


class PermissionResponse(PermissionBase):
    """权限响应"""
    id: int
    description: Optional[str] = None
    is_active: bool = True

    model_config = ConfigDict(from_attributes=True)


class UserPermissionsResponse(BaseModel):
    """用户权限列表响应"""
    code: int = 0
    message: str = "success"
    data: List[PermissionResponse] = []


# ============ Menu ============

class MenuBase(BaseModel):
    """菜单基础 schema"""
    code: str = Field(..., description="菜单代码")
    name: str = Field(..., description="菜单名称")
    type: str = Field(default="menu", description="菜单类型: directory/menu/button")
    path: Optional[str] = Field(None, description="路由路径")
    icon: Optional[str] = Field(None, description="图标")


class MenuResponse(MenuBase):
    """菜单响应"""
    id: int
    parent_id: Optional[int] = None
    component: Optional[str] = None
    sort_order: int = 0
    is_visible: bool = True
    is_active: bool = True
    permission_code: Optional[str] = None
    children: List["MenuResponse"] = []

    model_config = ConfigDict(from_attributes=True)


class UserMenusResponse(BaseModel):
    """用户菜单列表响应"""
    code: int = 0
    message: str = "success"
    data: List[MenuResponse] = []


# ============ Switch Role ============

class SwitchRoleRequest(BaseModel):
    """切换角色请求"""
    role_code: str = Field(..., description="目标角色代码")


class SwitchRoleResponse(BaseModel):
    """切换角色响应"""
    code: int = 0
    message: str = "success"
    data: Optional[dict] = None


# ============ 统一响应包装 ============

class ApiResponse(BaseModel):
    """统一 API 响应格式"""
    code: int = 0
    message: str = "success"
    data: Optional[dict] = None
