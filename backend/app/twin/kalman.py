"""
Per-machine Kalman filter for state estimation.

The Kalman filter maintains a probabilistic estimate of the machine's TRUE state,
smoothing noisy sensor readings and allowing the twin to estimate state even
when a reading is delayed or missing.

State vector: [engine_temperature, vibration_level, oil_pressure, fuel_consumption]
"""
from __future__ import annotations

import numpy as np
from typing import Dict, Optional

# One filter instance per machine, stored in memory
_filters: Dict[str, "MachineKalmanFilter"] = {}


class MachineKalmanFilter:
    """Scalar Kalman filter applied independently to each sensor."""

    # Process noise (how much we expect the true state to change between readings)
    Q = np.diag([0.5, 0.05, 0.3, 0.2])

    # Measurement noise (sensor uncertainty)
    R = np.diag([1.0, 0.1, 0.5, 0.3])

    def __init__(self, initial_state: np.ndarray):
        self.x = initial_state.copy()       # state estimate [temp, vib, oil, fuel]
        self.P = np.eye(4) * 10.0           # initial covariance (high uncertainty)
        self.F = np.eye(4)                  # state transition (identity — values persist)
        self.H = np.eye(4)                  # observation model (direct measurement)

    def update(self, measurement: np.ndarray) -> np.ndarray:
        """Run one predict-update cycle. Returns the filtered state estimate."""
        # Predict
        x_pred = self.F @ self.x
        P_pred = self.F @ self.P @ self.F.T + self.Q

        # Update
        S = self.H @ P_pred @ self.H.T + self.R
        K = P_pred @ self.H.T @ np.linalg.inv(S)
        self.x = x_pred + K @ (measurement - self.H @ x_pred)
        self.P = (np.eye(4) - K @ self.H) @ P_pred

        return self.x.copy()


def get_or_create_filter(machine_id: str, initial: Optional[Dict[str, float]] = None) -> MachineKalmanFilter:
    if machine_id not in _filters:
        if initial:
            state = np.array([
                initial.get("engine_temperature", 80.0),
                initial.get("vibration_level", 3.0),
                initial.get("oil_pressure", 55.0),
                initial.get("fuel_consumption", 12.0),
            ])
        else:
            state = np.array([80.0, 3.0, 55.0, 12.0])
        _filters[machine_id] = MachineKalmanFilter(state)
    return _filters[machine_id]


def run_filter(machine_id: str, sensor_data: Dict[str, float]) -> Dict[str, float]:
    """
    Feed a new sensor reading into the machine's Kalman filter.
    Returns the smoothed state estimate.
    """
    measurement = np.array([
        sensor_data.get("engine_temperature", 80.0),
        sensor_data.get("vibration_level", 3.0),
        sensor_data.get("oil_pressure", 55.0),
        sensor_data.get("fuel_consumption", 12.0),
    ])

    kf = get_or_create_filter(machine_id, sensor_data)
    filtered = kf.update(measurement)

    return {
        "engine_temperature": round(float(filtered[0]), 3),
        "vibration_level": round(float(filtered[1]), 3),
        "oil_pressure": round(float(filtered[2]), 3),
        "fuel_consumption": round(float(filtered[3]), 3),
    }
