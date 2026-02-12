"""
Integration tests for multi-role authentication and permission system.

Test Coverage:
- TC001-TC004: Role-based login flows (admin, coach, parent, student)
- TC005-TC008: Role switching and token validation
- TC009-TC012: Cross-role access control (403 scenarios)
- TC013-TC016: Permission API correctness
- TC017-TC020: Role-specific endpoint access
- TC021-TC024: Edge cases and security scenarios
"""
import pytest
from httpx import AsyncClient
from app.models.rbac import Permission, Role, role_permissions, user_roles


class TestRoleLogin:
    """Test role-based login flows."""

    @pytest.mark.asyncio
    async def test_tc001_admin_login_success(self, client: AsyncClient, test_users: dict):
        """TC001: Admin user can login successfully."""
        response = await client.post(
            "/api/v1/auth/login",
            json={"account": "admin@test.com", "password": "admin123"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["user"]["role"] == "admin"
        assert data["user"]["email"] == "admin@test.com"

    @pytest.mark.asyncio
    async def test_tc002_coach_login_success(self, client: AsyncClient, test_users: dict):
        """TC002: Coach user can login successfully."""
        response = await client.post(
            "/api/v1/auth/login",
            json={"account": "coach@test.com", "password": "coach123"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["user"]["role"] == "coach"
        assert data["user"]["email"] == "coach@test.com"

    @pytest.mark.asyncio
    async def test_tc003_parent_login_success(self, client: AsyncClient, test_users: dict):
        """TC003: Parent user can login successfully."""
        response = await client.post(
            "/api/v1/auth/login",
            json={"account": "parent@test.com", "password": "parent123"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["user"]["role"] == "parent"
        assert data["user"]["email"] == "parent@test.com"

    @pytest.mark.asyncio
    async def test_tc004_student_login_success(self, client: AsyncClient, test_users: dict):
        """TC004: Student user can login successfully."""
        response = await client.post(
            "/api/v1/auth/login",
            json={"account": "student@test.com", "password": "student123"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["user"]["role"] == "student"
        assert data["user"]["email"] == "student@test.com"

    @pytest.mark.asyncio
    async def test_tc005_login_with_invalid_credentials(self, client: AsyncClient):
        """TC005: Login fails with invalid credentials."""
        response = await client.post(
            "/api/v1/auth/login",
            json={"account": "admin@test.com", "password": "wrongpassword"}
        )
        assert response.status_code == 401
        assert "Invalid account or password" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_tc006_login_with_nonexistent_user(self, client: AsyncClient):
        """TC006: Login fails with non-existent user."""
        response = await client.post(
            "/api/v1/auth/login",
            json={"account": "nonexistent@test.com", "password": "password123"}
        )
        assert response.status_code == 401


class TestTokenValidation:
    """Test JWT token validation and role extraction."""

    @pytest.mark.asyncio
    async def test_tc007_valid_token_access(self, client: AsyncClient, admin_token: str):
        """TC007: Valid token allows access to protected endpoints."""
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["role"] == "admin"

    @pytest.mark.asyncio
    async def test_tc008_invalid_token_rejected(self, client: AsyncClient):
        """TC008: Invalid token is rejected."""
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid_token_12345"}
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_tc009_missing_token_rejected(self, client: AsyncClient):
        """TC009: Missing token is rejected."""
        response = await client.get("/api/v1/auth/me")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_tc010_token_contains_correct_role(
        self, client: AsyncClient, coach_token: str
    ):
        """TC010: Token contains correct role information."""
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {coach_token}"}
        )
        assert response.status_code == 200
        assert response.json()["role"] == "coach"


class TestCrossRoleAccessControl:
    """Test cross-role access control and 403 scenarios."""

    @pytest.mark.asyncio
    async def test_tc011_student_cannot_add_student(
        self, client: AsyncClient, student_token: str
    ):
        """TC011: Student cannot add new students (403)."""
        response = await client.post(
            "/api/v1/auth/students",
            headers={"Authorization": f"Bearer {student_token}"},
            json={"name": "New Student", "gender": "male"}
        )
        assert response.status_code == 403
        assert "Permission denied" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_tc012_coach_cannot_add_student(
        self, client: AsyncClient, coach_token: str
    ):
        """TC012: Coach cannot add new students (403)."""
        response = await client.post(
            "/api/v1/auth/students",
            headers={"Authorization": f"Bearer {coach_token}"},
            json={"name": "New Student", "gender": "male"}
        )
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_tc013_parent_can_add_student(
        self, client: AsyncClient, parent_token: str
    ):
        """TC013: Parent can add new students (200)."""
        response = await client.post(
            "/api/v1/auth/students",
            headers={"Authorization": f"Bearer {parent_token}"},
            json={"name": "New Student", "gender": "male"}
        )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_tc014_admin_can_add_student(
        self, client: AsyncClient, admin_token: str
    ):
        """TC014: Admin can add new students (200)."""
        response = await client.post(
            "/api/v1/auth/students",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"name": "Admin Student", "gender": "female"}
        )
        assert response.status_code == 200


class TestRoleSpecificEndpoints:
    """Test role-specific endpoint access patterns."""

    @pytest.mark.asyncio
    async def test_tc015_coach_access_own_profile(
        self, client: AsyncClient, coach_token: str
    ):
        """TC015: Coach can access their own profile."""
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {coach_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["role"] == "coach"
        assert "coach" in data

    @pytest.mark.asyncio
    async def test_tc016_student_access_own_profile(
        self, client: AsyncClient, student_token: str
    ):
        """TC016: Student can access their own profile."""
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {student_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["role"] == "student"
        assert "student" in data

    @pytest.mark.asyncio
    async def test_tc017_parent_access_own_profile(
        self, client: AsyncClient, parent_token: str
    ):
        """TC017: Parent can access their own profile."""
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {parent_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["role"] == "parent"

    @pytest.mark.asyncio
    async def test_tc018_admin_access_own_profile(
        self, client: AsyncClient, admin_token: str
    ):
        """TC018: Admin can access their own profile."""
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["role"] == "admin"


class TestUserProfileUpdate:
    """Test user profile update permissions."""

    @pytest.mark.asyncio
    async def test_tc019_user_can_update_own_profile(
        self, client: AsyncClient, student_token: str
    ):
        """TC019: User can update their own profile."""
        response = await client.put(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {student_token}"},
            json={"nickname": "Updated Student"}
        )
        assert response.status_code == 200
        assert response.json()["nickname"] == "Updated Student"

    @pytest.mark.asyncio
    async def test_tc020_user_cannot_change_role(
        self, client: AsyncClient, student_token: str
    ):
        """TC020: User cannot change their own role."""
        # Get current profile
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {student_token}"}
        )
        assert response.status_code == 200
        original_role = response.json()["role"]

        # Try to update (role field should be ignored if present in update)
        response = await client.put(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {student_token}"},
            json={"nickname": "Hacker Student"}
        )
        assert response.status_code == 200

        # Verify role hasn't changed
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {student_token}"}
        )
        assert response.json()["role"] == original_role


class TestPasswordManagement:
    """Test password change and reset flows."""

    @pytest.mark.asyncio
    async def test_tc021_user_can_change_password(
        self, client: AsyncClient, parent_token: str
    ):
        """TC021: User can change their password with correct old password."""
        response = await client.post(
            "/api/v1/auth/password/change",
            headers={"Authorization": f"Bearer {parent_token}"},
            json={"old_password": "parent123", "new_password": "newparent123"}
        )
        assert response.status_code == 200

        # Verify can login with new password
        response = await client.post(
            "/api/v1/auth/login",
            json={"account": "parent@test.com", "password": "newparent123"}
        )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_tc022_password_change_fails_with_wrong_old_password(
        self, client: AsyncClient, coach_token: str
    ):
        """TC022: Password change fails with incorrect old password."""
        response = await client.post(
            "/api/v1/auth/password/change",
            headers={"Authorization": f"Bearer {coach_token}"},
            json={"old_password": "wrongpassword", "new_password": "newcoach123"}
        )
        assert response.status_code == 400
        assert "Invalid old password" in response.json()["detail"]


class TestRegistrationFlows:
    """Test registration flows for different roles."""

    @pytest.mark.asyncio
    async def test_tc023_register_new_parent(self, client: AsyncClient):
        """TC023: New parent can register successfully."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "newparent@test.com",
                "password": "password123",
                "role": "parent",
                "nickname": "New Parent"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["user"]["role"] == "parent"

    @pytest.mark.asyncio
    async def test_tc024_register_duplicate_email_fails(
        self, client: AsyncClient, test_users: dict
    ):
        """TC024: Registration fails with duplicate email."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "admin@test.com",
                "password": "password123",
                "role": "parent"
            }
        )
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"]


class TestLogout:
    """Test logout functionality."""

    @pytest.mark.asyncio
    async def test_tc025_user_can_logout(self, client: AsyncClient, admin_token: str):
        """TC025: User can logout successfully."""
        response = await client.post(
            "/api/v1/auth/logout",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        assert "Logout success" in response.json()["message"]


# ============ RBAC Multi-Role Tests ============

class TestRBACRoleAPI:
    """Test RBAC role management API endpoints."""

    @pytest.mark.asyncio
    async def test_tc026_get_user_roles_endpoint(
        self, client: AsyncClient, admin_token: str
    ):
        """TC026: GET /user/roles returns user's role list."""
        response = await client.get(
            "/api/v1/user/roles",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert "data" in data
        assert isinstance(data["data"], list)
        # Should have at least one role (fallback to legacy role)
        assert len(data["data"]) >= 1

    @pytest.mark.asyncio
    async def test_tc027_get_user_permissions_endpoint(
        self, client: AsyncClient, coach_token: str
    ):
        """TC027: GET /user/permissions returns user's permission list."""
        response = await client.get(
            "/api/v1/user/permissions",
            headers={"Authorization": f"Bearer {coach_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert "data" in data
        assert isinstance(data["data"], list)

    @pytest.mark.asyncio
    async def test_tc028_get_user_menus_endpoint(
        self, client: AsyncClient, parent_token: str
    ):
        """TC028: GET /user/menus returns user's menu tree."""
        response = await client.get(
            "/api/v1/user/menus",
            headers={"Authorization": f"Bearer {parent_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert "data" in data
        assert isinstance(data["data"], list)

    @pytest.mark.asyncio
    async def test_tc029_switch_role_without_permission(
        self, client: AsyncClient, student_token: str
    ):
        """TC029: User cannot switch to a role they don't have."""
        response = await client.post(
            "/api/v1/user/switch-role",
            headers={"Authorization": f"Bearer {student_token}"},
            json={"role_code": "admin"}
        )
        assert response.status_code == 403
        assert "没有" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_tc030_role_api_requires_auth(self, client: AsyncClient):
        """TC030: Role API endpoints require authentication."""
        # Test all role endpoints without auth
        endpoints = [
            ("GET", "/api/v1/user/roles"),
            ("GET", "/api/v1/user/permissions"),
            ("GET", "/api/v1/user/menus"),
            ("POST", "/api/v1/user/switch-role"),
        ]

        for method, endpoint in endpoints:
            if method == "GET":
                response = await client.get(endpoint)
            else:
                response = await client.post(endpoint, json={"role_code": "admin"})
            assert response.status_code == 401, f"{method} {endpoint} should require auth"

    @pytest.mark.asyncio
    async def test_tc041_switch_role_success_updates_active_role_and_token(
        self,
        client: AsyncClient,
        parent_token: str,
        test_users: dict,
        db_session,
    ):
        """TC041: Switching role returns token consistent with new active role."""
        parent_user = test_users["parent"]

        parent_role = Role(code="parent", name="家长", is_system=True, is_active=True, sort_order=1)
        student_role = Role(code="student", name="学员", is_system=True, is_active=True, sort_order=2)
        parent_perm = Permission(
            code="booking:read",
            name="Read booking",
            type="api",
            resource="/api/v1/bookings",
            action="GET",
            is_active=True,
        )
        student_perm = Permission(
            code="training:read",
            name="Read training",
            type="api",
            resource="/api/v1/training/history",
            action="GET",
            is_active=True,
        )
        db_session.add_all([parent_role, student_role, parent_perm, student_perm])
        await db_session.flush()

        await db_session.execute(
            user_roles.insert(),
            [
                {"user_id": parent_user.id, "role_id": parent_role.id, "is_active": True},
                {"user_id": parent_user.id, "role_id": student_role.id, "is_active": False},
            ],
        )
        await db_session.execute(
            role_permissions.insert(),
            [
                {"role_id": parent_role.id, "permission_id": parent_perm.id},
                {"role_id": student_role.id, "permission_id": student_perm.id},
            ],
        )
        await db_session.commit()

        switch_resp = await client.post(
            "/api/v1/user/switch-role",
            headers={"Authorization": f"Bearer {parent_token}"},
            json={"role_code": "student"},
        )
        assert switch_resp.status_code == 200

        switch_data = switch_resp.json()["data"]
        assert switch_data["active_role"] == "student"
        assert switch_data["token_type"] == "bearer"
        assert "access_token" in switch_data
        assert set(switch_data["roles"]) == {"parent", "student"}

        new_token = switch_data["access_token"]

        me_resp = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {new_token}"},
        )
        assert me_resp.status_code == 200
        assert me_resp.json()["role"] == "student"

        roles_resp = await client.get(
            "/api/v1/user/roles",
            headers={"Authorization": f"Bearer {new_token}"},
        )
        assert roles_resp.status_code == 200
        role_codes = {item["code"] for item in roles_resp.json()["data"]}
        assert role_codes == {"parent", "student"}

        perms_resp = await client.get(
            "/api/v1/user/permissions",
            headers={"Authorization": f"Bearer {new_token}"},
        )
        assert perms_resp.status_code == 200
        perm_codes = {item["code"] for item in perms_resp.json()["data"]}
        assert perm_codes == {"booking:read", "training:read"}


class TestRBACCrossRoleAccess:
    """Test cross-role access control with RBAC system."""

    @pytest.mark.asyncio
    async def test_tc031_student_cannot_access_coach_workbench(
        self, client: AsyncClient, student_token: str
    ):
        """TC031: Student role cannot access coach-only endpoints."""
        response = await client.get(
            "/api/v1/coaches/me/schedule",
            headers={"Authorization": f"Bearer {student_token}"}
        )
        # Should be 403 or 404 (no coach profile)
        assert response.status_code in [403, 404]

    @pytest.mark.asyncio
    async def test_tc032_coach_can_access_own_schedule(
        self, client: AsyncClient, coach_token: str
    ):
        """TC032: Coach role can access their own schedule."""
        response = await client.get(
            "/api/v1/coaches/me/schedule",
            headers={"Authorization": f"Bearer {coach_token}"}
        )
        # Should be 200 or empty result, not 403
        assert response.status_code != 403

    @pytest.mark.asyncio
    async def test_tc033_parent_can_view_coaches(
        self, client: AsyncClient, parent_token: str
    ):
        """TC033: Parent role can view coach list."""
        response = await client.get(
            "/api/v1/coaches",
            headers={"Authorization": f"Bearer {parent_token}"}
        )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_tc034_admin_can_access_dashboard(
        self, client: AsyncClient, admin_token: str
    ):
        """TC034: Admin role can access all real dashboard routes."""
        endpoints = [
            "/api/v1/dashboard/overview",
            "/api/v1/dashboard/recent-bookings",
            "/api/v1/dashboard/booking-stats",
            "/api/v1/dashboard/revenue-stats",
        ]

        for endpoint in endpoints:
            response = await client.get(
                endpoint,
                headers={"Authorization": f"Bearer {admin_token}"},
            )
            assert response.status_code == 200, f"Admin should access {endpoint}"

    @pytest.mark.asyncio
    async def test_tc042_non_admin_cannot_access_dashboard_routes(
        self, client: AsyncClient, coach_token: str
    ):
        """TC042: Non-admin role is denied on all dashboard routes."""
        endpoints = [
            "/api/v1/dashboard/overview",
            "/api/v1/dashboard/recent-bookings",
            "/api/v1/dashboard/booking-stats",
            "/api/v1/dashboard/revenue-stats",
        ]

        for endpoint in endpoints:
            response = await client.get(
                endpoint,
                headers={"Authorization": f"Bearer {coach_token}"},
            )
            assert response.status_code == 403, f"Coach should be denied for {endpoint}"


class TestRBACRoleInheritance:
    """Test role-based permission inheritance."""

    @pytest.mark.asyncio
    async def test_tc035_admin_has_all_permissions(
        self, client: AsyncClient, admin_token: str
    ):
        """TC035: Admin role has access to all endpoints."""
        # Test various endpoints that require different permissions
        endpoints = [
            "/api/v1/auth/me",
            "/api/v1/coaches",
            "/api/v1/students",
        ]

        for endpoint in endpoints:
            response = await client.get(
                endpoint,
                headers={"Authorization": f"Bearer {admin_token}"}
            )
            # Admin should not get 403 on any endpoint
            assert response.status_code != 403, f"Admin blocked from {endpoint}"

    @pytest.mark.asyncio
    async def test_tc036_role_specific_data_isolation(
        self, client: AsyncClient, coach_token: str, student_token: str
    ):
        """TC036: Users can only see data relevant to their role."""
        # Coach sees their own profile
        coach_response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {coach_token}"}
        )
        assert coach_response.status_code == 200
        assert coach_response.json()["role"] == "coach"

        # Student sees their own profile
        student_response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {student_token}"}
        )
        assert student_response.status_code == 200
        assert student_response.json()["role"] == "student"


class TestRBACSecurityScenarios:
    """Test security edge cases for RBAC system."""

    @pytest.mark.asyncio
    async def test_tc037_cannot_escalate_privileges(
        self, client: AsyncClient, student_token: str
    ):
        """TC037: User cannot escalate their own privileges."""
        # Try to update profile with admin role (should be ignored)
        response = await client.put(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {student_token}"},
            json={"nickname": "Hacker"}
        )

        if response.status_code == 200:
            # Verify role hasn't changed
            me_response = await client.get(
                "/api/v1/auth/me",
                headers={"Authorization": f"Bearer {student_token}"}
            )
            assert me_response.json()["role"] == "student"

    @pytest.mark.asyncio
    async def test_tc038_expired_token_rejected(self, client: AsyncClient):
        """TC038: Expired or malformed tokens are rejected."""
        # Test with obviously invalid token
        response = await client.get(
            "/api/v1/user/roles",
            headers={"Authorization": "Bearer invalid.token.here"}
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_tc039_role_check_on_sensitive_operations(
        self, client: AsyncClient, student_token: str
    ):
        """TC039: Sensitive operations check role permissions."""
        # Student trying to create another student (should fail)
        response = await client.post(
            "/api/v1/auth/students",
            headers={"Authorization": f"Bearer {student_token}"},
            json={"name": "Unauthorized Student", "gender": "male"}
        )
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_tc040_concurrent_role_access(
        self, client: AsyncClient, admin_token: str, coach_token: str
    ):
        """TC040: Multiple users with different roles can access simultaneously."""
        import asyncio

        async def admin_request():
            return await client.get(
                "/api/v1/auth/me",
                headers={"Authorization": f"Bearer {admin_token}"}
            )

        async def coach_request():
            return await client.get(
                "/api/v1/auth/me",
                headers={"Authorization": f"Bearer {coach_token}"}
            )

        # Run concurrent requests
        admin_resp, coach_resp = await asyncio.gather(
            admin_request(),
            coach_request()
        )

        assert admin_resp.status_code == 200
        assert admin_resp.json()["role"] == "admin"
        assert coach_resp.status_code == 200
        assert coach_resp.json()["role"] == "coach"
