"""
Performance tests for multi-role authentication system.

Tests:
- Concurrent login (100 users)
- Permission query response time
- Token validation throughput
"""
import asyncio
import os
import statistics
import time

import pytest
from httpx import AsyncClient


class TestConcurrentLogin:
    """Test concurrent login performance."""

    @pytest.mark.asyncio
    async def test_concurrent_login_100_users(self, client: AsyncClient, test_users: dict):
        """Simulate 100 concurrent login requests and measure response times."""
        credentials = [
            {"account": "admin@test.com", "password": "admin123"},
            {"account": "coach@test.com", "password": "coach123"},
            {"account": "parent@test.com", "password": "parent123"},
            {"account": "student@test.com", "password": "student123"},
        ]

        async def single_login(cred: dict) -> tuple:
            """Execute a single login and return (status_code, response_time_ms)."""
            start = time.perf_counter()
            response = await client.post("/api/v1/auth/login", json=cred)
            elapsed_ms = (time.perf_counter() - start) * 1000
            return response.status_code, elapsed_ms

        # Create 100 login tasks (round-robin across 4 roles)
        tasks = []
        for i in range(100):
            cred = credentials[i % len(credentials)]
            tasks.append(single_login(cred))

        results = await asyncio.gather(*tasks)

        status_codes = [r[0] for r in results]
        response_times = [r[1] for r in results]

        # All logins should succeed
        success_count = sum(1 for s in status_codes if s == 200)
        success_rate = success_count / len(status_codes) * 100

        # Calculate statistics
        avg_time = statistics.mean(response_times)
        p50_time = statistics.median(response_times)
        p95_time = sorted(response_times)[int(len(response_times) * 0.95)]
        p99_time = sorted(response_times)[int(len(response_times) * 0.99)]
        max_time = max(response_times)
        min_time = min(response_times)

        print(f"\n{'='*60}")
        print("Concurrent Login Performance (100 users)")
        print(f"{'='*60}")
        print(f"Success Rate: {success_rate:.1f}% ({success_count}/100)")
        print(f"Avg Response Time: {avg_time:.2f}ms")
        print(f"P50 Response Time: {p50_time:.2f}ms")
        print(f"P95 Response Time: {p95_time:.2f}ms")
        print(f"P99 Response Time: {p99_time:.2f}ms")
        print(f"Min Response Time: {min_time:.2f}ms")
        print(f"Max Response Time: {max_time:.2f}ms")
        print(f"{'='*60}")

        # Assertions
        database_url = os.getenv("TEST_DATABASE_URL", "")
        p95_threshold_ms = 1200 if not database_url or database_url.startswith("sqlite") else 500
        assert success_rate >= 95.0, f"Success rate {success_rate}% below 95% threshold"
        assert p95_time < p95_threshold_ms, (
            f"P95 response time {p95_time:.2f}ms exceeds {p95_threshold_ms}ms threshold"
        )


class TestPermissionQueryPerformance:
    """Test permission query response times."""

    @pytest.mark.asyncio
    async def test_permission_query_response_time(
        self, client: AsyncClient, admin_token: str
    ):
        """Measure response time for permission-related queries."""
        iterations = 50
        response_times = []

        for _ in range(iterations):
            start = time.perf_counter()
            response = await client.get(
                "/api/v1/auth/me",
                headers={"Authorization": f"Bearer {admin_token}"}
            )
            elapsed_ms = (time.perf_counter() - start) * 1000
            assert response.status_code == 200
            response_times.append(elapsed_ms)

        avg_time = statistics.mean(response_times)
        p95_time = sorted(response_times)[int(len(response_times) * 0.95)]
        p99_time = sorted(response_times)[int(len(response_times) * 0.99)]

        print(f"\n{'='*60}")
        print(f"Permission Query Performance ({iterations} iterations)")
        print(f"{'='*60}")
        print(f"Avg Response Time: {avg_time:.2f}ms")
        print(f"P95 Response Time: {p95_time:.2f}ms")
        print(f"P99 Response Time: {p99_time:.2f}ms")
        print(f"{'='*60}")

        assert p95_time < 500, f"P95 response time {p95_time:.2f}ms exceeds 500ms threshold"

    @pytest.mark.asyncio
    async def test_multi_role_permission_query(
        self, client: AsyncClient,
        admin_token: str, coach_token: str,
        parent_token: str, student_token: str
    ):
        """Measure response time for permission queries across all roles."""
        tokens = {
            "admin": admin_token,
            "coach": coach_token,
            "parent": parent_token,
            "student": student_token,
        }

        role_times = {}
        iterations = 20

        for role, token in tokens.items():
            times = []
            for _ in range(iterations):
                start = time.perf_counter()
                response = await client.get(
                    "/api/v1/auth/me",
                    headers={"Authorization": f"Bearer {token}"}
                )
                elapsed_ms = (time.perf_counter() - start) * 1000
                assert response.status_code == 200
                times.append(elapsed_ms)

            role_times[role] = {
                "avg": statistics.mean(times),
                "p95": sorted(times)[int(len(times) * 0.95)],
                "max": max(times),
            }

        print(f"\n{'='*60}")
        print("Multi-Role Permission Query Performance")
        print(f"{'='*60}")
        for role, stats in role_times.items():
            print(
                f"  {role:10s}: avg={stats['avg']:.2f}ms "
                f" p95={stats['p95']:.2f}ms  max={stats['max']:.2f}ms"
            )
        print(f"{'='*60}")

        # All roles should respond within 500ms at P95
        for role, stats in role_times.items():
            assert stats["p95"] < 500, (
                f"{role} P95 response time {stats['p95']:.2f}ms exceeds 500ms"
            )


class TestTokenValidationThroughput:
    """Test token validation throughput."""

    @pytest.mark.asyncio
    async def test_token_validation_throughput(
        self, client: AsyncClient, admin_token: str
    ):
        """Measure how many token validations can be processed per second."""
        duration_seconds = 3
        request_count = 0
        errors = 0
        start_time = time.perf_counter()

        while (time.perf_counter() - start_time) < duration_seconds:
            response = await client.get(
                "/api/v1/auth/me",
                headers={"Authorization": f"Bearer {admin_token}"}
            )
            request_count += 1
            if response.status_code != 200:
                errors += 1

        elapsed = time.perf_counter() - start_time
        rps = request_count / elapsed

        print(f"\n{'='*60}")
        print(f"Token Validation Throughput ({duration_seconds}s)")
        print(f"{'='*60}")
        print(f"Total Requests: {request_count}")
        print(f"Errors: {errors}")
        print(f"Requests/Second: {rps:.1f}")
        print(f"{'='*60}")

        assert errors == 0, f"{errors} errors during throughput test"
        # Minimum 10 RPS for single-threaded async test
        assert rps > 10, f"Throughput {rps:.1f} RPS below 10 RPS minimum"
