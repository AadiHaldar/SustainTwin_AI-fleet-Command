"""Tests for API endpoints including auth and RBAC."""

import pytest


class TestAuthEndpoints:
    """Test authentication flow."""

    def test_login_with_valid_credentials(self, client, seed_users):
        """Valid login should return a JWT token."""
        resp = client.post(
            "/api/v1/auth/token",
            data={"username": "test_engineer", "password": "pass123"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["role"] == "engineer"

    def test_login_with_invalid_credentials(self, client):
        """Invalid login should return 401."""
        resp = client.post(
            "/api/v1/auth/token",
            data={"username": "nonexistent", "password": "wrongpass"},
        )
        assert resp.status_code == 401

    def test_login_with_wrong_password(self, client, seed_users):
        """Wrong password should return 401."""
        resp = client.post(
            "/api/v1/auth/token",
            data={"username": "test_operator", "password": "wrongpass"},
        )
        assert resp.status_code == 401


class TestTelemetryRBAC:
    """Test role-based access on telemetry endpoints."""

    def test_get_telemetry_without_token_returns_401(self, client):
        """Unauthenticated request should be rejected."""
        resp = client.get("/api/v1/telemetry")
        assert resp.status_code == 401

    def test_get_telemetry_with_operator_token_returns_200(self, client, auth_token_operator):
        """Operator should be able to read telemetry."""
        resp = client.get(
            "/api/v1/telemetry",
            headers={"Authorization": f"Bearer {auth_token_operator}"},
        )
        assert resp.status_code == 200

    def test_post_sync_with_operator_token_returns_403(self, client, auth_token_operator):
        """Operator should NOT be able to post telemetry (engineer/admin only)."""
        resp = client.post(
            "/api/v1/telemetry/sync",
            json={
                "machine_id": "T-001",
                "sensor_data": {"engine_rpm": 1800, "engine_temperature": 90},
                "is_anomaly": False,
            },
            headers={"Authorization": f"Bearer {auth_token_operator}"},
        )
        assert resp.status_code == 403

    def test_post_sync_with_engineer_token_returns_200(self, client, auth_token_engineer):
        """Engineer should be able to post telemetry."""
        resp = client.post(
            "/api/v1/telemetry/sync",
            json={
                "machine_id": "T-001",
                "sensor_data": {"engine_rpm": 1800, "engine_temperature": 90},
                "is_anomaly": False,
            },
            headers={"Authorization": f"Bearer {auth_token_engineer}"},
        )
        assert resp.status_code == 200


class TestDiagnosticsRBAC:
    """Test role-based access on diagnostics endpoints."""

    def test_get_diagnostics_with_operator_returns_403(self, client, auth_token_operator):
        """Operator should NOT be able to access diagnostics."""
        resp = client.get(
            "/api/v1/diagnostics",
            headers={"Authorization": f"Bearer {auth_token_operator}"},
        )
        assert resp.status_code == 403

    def test_get_diagnostics_with_engineer_returns_200(self, client, auth_token_engineer):
        """Engineer should be able to access diagnostics."""
        resp = client.get(
            "/api/v1/diagnostics",
            headers={"Authorization": f"Bearer {auth_token_engineer}"},
        )
        assert resp.status_code == 200


class TestHealthEndpoints:
    """Test basic health check endpoints."""

    def test_root_endpoint(self, client):
        """Root should return welcome message."""
        resp = client.get("/")
        assert resp.status_code == 200
        assert "SustainTwin" in resp.json().get("message", "")

    def test_health_endpoint(self, client):
        """Health check should return ok."""
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"
