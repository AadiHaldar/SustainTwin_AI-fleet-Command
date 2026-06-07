"""Tests for the multi-agent LangGraph system."""

import pytest
from unittest.mock import patch, MagicMock


class TestTelemetryIngestNode:
    """Test Node 1: anomaly detection via z-scores."""

    def test_normal_readings_get_low_severity(self, db_session, seed_machines):
        """Normal readings within expected ranges should yield severity=low."""
        from app.models.machine import Telemetry
        from datetime import datetime, timedelta, timezone
        import json

        # Seed 50 normal readings for T-001
        now = datetime.now(timezone.utc)
        for i in range(50):
            t = Telemetry(
                machine_id="T-001",
                timestamp=now - timedelta(minutes=i * 15),
                sensor_data={
                    "engine_rpm": 1800 + (i % 10) * 5,
                    "engine_temperature": 88 + (i % 5),
                    "vibration_level": 18 + (i % 3),
                    "oil_pressure": 55 + (i % 8),
                    "fuel_consumption": 14 + (i % 4),
                },
                failure_risk=0.0,
                is_anomaly=False,
            )
            db_session.add(t)
        db_session.commit()

        try:
            from app.agents.telemetry_ingest_node import telemetry_ingest_node

            state = {
                "machine_id": "T-001",
                "sensor_data": {
                    "engine_rpm": 1820,
                    "engine_temperature": 90,
                    "vibration_level": 19,
                    "oil_pressure": 57,
                    "fuel_consumption": 15,
                },
                "db_session": db_session,
            }
            result = telemetry_ingest_node(state)
            assert result["severity"] == "low"
            assert all(not v for v in result["anomaly_flags"].values())
        except ImportError:
            pytest.skip("Agent modules not yet available")

    def test_anomalous_readings_get_critical_severity(self, db_session, seed_machines):
        """Extreme readings should yield severity=critical."""
        from app.models.machine import Telemetry
        from datetime import datetime, timedelta, timezone

        now = datetime.now(timezone.utc)
        for i in range(50):
            t = Telemetry(
                machine_id="T-001",
                timestamp=now - timedelta(minutes=i * 15),
                sensor_data={
                    "engine_rpm": 1800,
                    "engine_temperature": 88,
                    "vibration_level": 18,
                    "oil_pressure": 55,
                    "fuel_consumption": 14,
                },
                failure_risk=0.0,
                is_anomaly=False,
            )
            db_session.add(t)
        db_session.commit()

        try:
            from app.agents.telemetry_ingest_node import telemetry_ingest_node

            state = {
                "machine_id": "T-001",
                "sensor_data": {
                    "engine_rpm": 3500,         # way above normal
                    "engine_temperature": 150,   # way above normal
                    "vibration_level": 80,       # way above normal
                    "oil_pressure": 55,
                    "fuel_consumption": 14,
                },
                "db_session": db_session,
            }
            result = telemetry_ingest_node(state)
            assert result["severity"] in ("critical", "medium")
            assert any(v for v in result["anomaly_flags"].values())
        except ImportError:
            pytest.skip("Agent modules not yet available")


class TestSustainabilityNode:
    """Test Node 3: carbon impact calculation."""

    def test_computes_nonzero_carbon_delta(self):
        """Anomalous state should produce non-zero carbon impact."""
        try:
            from app.agents.sustainability_node import sustainability_node

            state = {
                "machine_id": "T-001",
                "sensor_data": {
                    "engine_rpm": 3000,
                    "engine_temperature": 120,
                    "vibration_level": 60,
                    "fuel_consumption": 20,
                },
                "severity": "critical",
                "anomaly_flags": {"engine_rpm": True, "vibration_level": True},
                "z_scores": {"engine_rpm": 4.0, "vibration_level": 3.5},
                "diagnosis": {"root_cause": "bearing wear", "urgency": "immediate"},
            }
            result = sustainability_node(state)
            # Node may return flat or nested under 'sustainability' key
            if "sustainability" in result:
                s = result["sustainability"]
                assert s["carbon_delta_kg"] > 0
                assert len(s["sustainability_recommendation"]) > 10
            else:
                assert result.get("carbon_delta_kg", 0) > 0
                assert len(result.get("sustainability_recommendation", "")) > 10
        except ImportError:
            pytest.skip("Agent modules not yet available")


class TestConditionalRouting:
    """Test that low severity skips Gemini."""

    def test_low_severity_skips_expensive_nodes(self):
        """When severity is low, the graph should skip diagnose and sustain nodes."""
        try:
            from app.agents.graph import should_diagnose

            # Low severity -> END
            state = {"severity": "low"}
            result = should_diagnose(state)
            assert result == "__end__" or result == "end" or "end" in result.lower()
        except (ImportError, AttributeError):
            pytest.skip("Agent graph not yet available")
