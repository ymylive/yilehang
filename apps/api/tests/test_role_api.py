"""
Unit tests for RBAC (Role-Based Access Control) API endpoints.

Test Coverage:
- Role query API tests
- Permission query API tests
- Menu query API tests
- Role switching API tests
- require_role decorator tests
- require_permission decorator tests
"""

from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.middleware.role_auth import (
    get_current_user_with_roles,
    get_user_permissions,
    require_permission,
    require_role,
)
from app.models.rbac import Permission, Role, RoleType


class TestGetCurrentUserWithRoles:
    """Unit tests for get_current_user_with_roles dependency."""

    @pytest.mark.asyncio
    async def test_returns_user_with_roles_from_rbac_table(self):
        """Test that roles are fetched from RBAC tables when available."""
        mock_db = AsyncMock(spec=AsyncSession)
        mock_current_user = {"user_id": 1, "role": "parent"}

        mock_role = MagicMock()
        mock_role.code = "admin"
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [mock_role]
        mock_db.execute.return_value = mock_result

        mock_active_result = MagicMock()
        mock_active_result.scalar_one_or_none.return_value = "admin"
        mock_db.execute.side_effect = [mock_result, mock_active_result]

        result = await get_current_user_with_roles(mock_current_user, mock_db)

        assert result["roles"] == ["admin"]
        assert result["active_role"] == "admin"
        assert result["user_id"] == 1

    @pytest.mark.asyncio
    async def test_fallback_to_user_role_when_no_rbac_records(self):
        """Test fallback to User.role field when RBAC tables are empty."""
        mock_db = AsyncMock(spec=AsyncSession)
        mock_current_user = {"user_id": 1, "role": "coach"}

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []

        mock_active_result = MagicMock()
        mock_active_result.scalar_one_or_none.return_value = None

        mock_db.execute.side_effect = [mock_result, mock_active_result]

        result = await get_current_user_with_roles(mock_current_user, mock_db)

        assert result["roles"] == ["coach"]
        assert result["active_role"] == "coach"


class TestGetUserPermissions:
    """Unit tests for get_user_permissions function."""

    @pytest.mark.asyncio
    async def test_returns_permission_codes_for_user(self):
        """Test that permission codes are correctly fetched."""
        mock_db = AsyncMock(spec=AsyncSession)

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [
            "course:read",
            "course:create",
            "booking:read",
        ]
        mock_db.execute.return_value = mock_result

        permissions = await get_user_permissions(1, mock_db)

        assert "course:read" in permissions
        assert "course:create" in permissions
        assert "booking:read" in permissions

    @pytest.mark.asyncio
    async def test_filters_by_role_codes_when_provided(self):
        """Test that permissions are filtered by role codes."""
        mock_db = AsyncMock(spec=AsyncSession)

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = ["course:read"]
        mock_db.execute.return_value = mock_result

        permissions = await get_user_permissions(1, mock_db, role_codes=["coach"])

        assert permissions == ["course:read"]


class TestRequireRoleDecorator:
    """Unit tests for require_role dependency factory."""

    @pytest.mark.asyncio
    async def test_allows_user_with_matching_role(self):
        """Test that users with matching roles are allowed."""
        dependency = require_role(["admin", "coach"])

        mock_user = {"user_id": 1, "roles": ["coach"], "active_role": "coach"}

        result = await dependency(mock_user)

        assert result == mock_user

    @pytest.mark.asyncio
    async def test_allows_user_with_any_of_multiple_roles(self):
        """Test that users with any of the allowed roles pass."""
        dependency = require_role(["admin", "coach", "parent"])

        mock_user = {"user_id": 1, "roles": ["parent", "student"], "active_role": "parent"}

        result = await dependency(mock_user)

        assert result == mock_user

    @pytest.mark.asyncio
    async def test_denies_user_without_matching_role(self):
        """Test that users without matching roles get 403."""
        from fastapi import HTTPException

        dependency = require_role(["admin"])

        mock_user = {"user_id": 1, "roles": ["student"], "active_role": "student"}

        with pytest.raises(HTTPException) as exc_info:
            await dependency(mock_user)

        assert exc_info.value.status_code == 403
        assert "admin" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_denies_user_with_empty_roles(self):
        """Test that users with no roles get 403."""
        from fastapi import HTTPException

        dependency = require_role(["coach"])

        mock_user = {"user_id": 1, "roles": [], "active_role": ""}

        with pytest.raises(HTTPException) as exc_info:
            await dependency(mock_user)

        assert exc_info.value.status_code == 403


class TestRequirePermissionDecorator:
    """Unit tests for require_permission dependency factory."""

    @pytest.mark.asyncio
    async def test_admin_bypasses_permission_check(self):
        """Test that admin role bypasses all permission checks."""
        dependency = require_permission(["course:delete", "user:admin"])

        mock_user = {"user_id": 1, "roles": ["admin"], "active_role": "admin"}
        mock_db = AsyncMock(spec=AsyncSession)

        result = await dependency(mock_user, mock_db)

        assert result == mock_user

    @pytest.mark.asyncio
    async def test_allows_user_with_all_required_permissions(self):
        """Test that users with all required permissions pass."""
        dependency = require_permission(["course:read", "course:create"])

        mock_user = {"user_id": 1, "roles": ["coach"], "active_role": "coach"}
        mock_db = AsyncMock(spec=AsyncSession)

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [
            "course:read",
            "course:create",
            "course:update",
        ]
        mock_db.execute.return_value = mock_result

        result = await dependency(mock_user, mock_db)

        assert result == mock_user

    @pytest.mark.asyncio
    async def test_denies_user_missing_some_permissions(self):
        """Test that users missing any required permission get 403."""
        from fastapi import HTTPException

        dependency = require_permission(["course:read", "course:delete"])

        mock_user = {"user_id": 1, "roles": ["coach"], "active_role": "coach"}
        mock_db = AsyncMock(spec=AsyncSession)

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = ["course:read"]
        mock_db.execute.return_value = mock_result

        with pytest.raises(HTTPException) as exc_info:
            await dependency(mock_user, mock_db)

        assert exc_info.value.status_code == 403
        assert "course:delete" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_denies_user_with_no_permissions(self):
        """Test that users with no permissions get 403."""
        from fastapi import HTTPException

        dependency = require_permission(["booking:create"])

        mock_user = {"user_id": 1, "roles": ["student"], "active_role": "student"}
        mock_db = AsyncMock(spec=AsyncSession)

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db.execute.return_value = mock_result

        with pytest.raises(HTTPException) as exc_info:
            await dependency(mock_user, mock_db)

        assert exc_info.value.status_code == 403


class TestRoleTypeEnum:
    """Unit tests for RoleType enum."""

    def test_role_type_values(self):
        """Test that RoleType enum has correct values."""
        assert RoleType.ADMIN.value == "admin"
        assert RoleType.COACH.value == "coach"
        assert RoleType.PARENT.value == "parent"
        assert RoleType.STUDENT.value == "student"
        assert RoleType.MERCHANT.value == "merchant"

    def test_role_type_is_string_enum(self):
        """Test that RoleType values are strings."""
        for role_type in RoleType:
            assert isinstance(role_type.value, str)


class TestRoleModel:
    """Unit tests for Role model."""

    def test_role_model_attributes(self):
        """Test Role model has expected attributes."""
        role = Role(
            code="test_role",
            name="Test Role",
            description="A test role",
            is_system=False,
            is_active=True,
            sort_order=10,
        )

        assert role.code == "test_role"
        assert role.name == "Test Role"
        assert role.description == "A test role"
        assert role.is_system is False
        assert role.is_active is True
        assert role.sort_order == 10


class TestPermissionModel:
    """Unit tests for Permission model."""

    def test_permission_model_attributes(self):
        """Test Permission model has expected attributes."""
        permission = Permission(
            code="course:create",
            name="Create Course",
            type="api",
            resource="/api/v1/courses",
            action="POST",
            description="Permission to create courses",
        )

        assert permission.code == "course:create"
        assert permission.name == "Create Course"
        assert permission.type == "api"
        assert permission.resource == "/api/v1/courses"
        assert permission.action == "POST"
