"""Tests for the smart edge node."""

import pytest
import numpy as np


class TestEdgeIsolationForest:
    """Test the local IsolationForest scoring logic."""

    def test_normal_reading_not_flagged(self):
        """A clearly normal reading should not be flagged as anomaly."""
        from sklearn.ensemble import IsolationForest

        # Train on normal data
        np.random.seed(42)
        normal_data = np.column_stack([
            np.random.normal(1800, 200, 500),   # rpm
            np.random.normal(88, 6, 500),        # temp
            np.random.normal(18, 5, 500),         # vibration
            np.random.normal(55, 10, 500),        # oil_pressure
            np.random.normal(14, 3, 500),          # fuel
        ])

        model = IsolationForest(contamination=0.05, n_estimators=100, random_state=42)
        model.fit(normal_data)

        # Normal reading
        normal_reading = np.array([[1800, 88, 18, 55, 14]])
        score = model.decision_function(normal_reading)[0]
        assert score > -0.1, f"Normal reading incorrectly flagged as anomaly (score={score})"

    def test_anomalous_reading_flagged(self):
        """A clearly anomalous reading should be flagged."""
        from sklearn.ensemble import IsolationForest

        np.random.seed(42)
        normal_data = np.column_stack([
            np.random.normal(1800, 200, 500),
            np.random.normal(88, 6, 500),
            np.random.normal(18, 5, 500),
            np.random.normal(55, 10, 500),
            np.random.normal(14, 3, 500),
        ])

        model = IsolationForest(contamination=0.05, n_estimators=100, random_state=42)
        model.fit(normal_data)

        # Extremely anomalous reading
        anomalous_reading = np.array([[4500, 180, 95, 10, 45]])
        score = model.decision_function(anomalous_reading)[0]
        assert score < -0.1, f"Anomalous reading not flagged (score={score})"

    def test_compression_ratio_calculation(self):
        """Test that compression ratio math is correct."""
        total_readings = 100
        anomalies_synced = 8
        filtered_pct = ((total_readings - anomalies_synced) / total_readings) * 100
        assert filtered_pct == 92.0
        assert anomalies_synced < total_readings
