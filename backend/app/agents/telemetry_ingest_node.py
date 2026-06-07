"""Telemetry ingest node -- statistical anomaly detection via z-scores.

Queries the most recent 50 telemetry readings for the same machine,
computes per-sensor mean/std, and flags current readings whose |z-score|
exceeds configurable thresholds.
"""
from __future__ import annotations

import logging
from collections import defaultdict
from typing import Any, Dict

import numpy as np
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.models.machine import Telemetry

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Thresholds
# ---------------------------------------------------------------------------
Z_MEDIUM_THRESHOLD: float = 2.0
Z_CRITICAL_THRESHOLD: float = 3.5
HISTORY_WINDOW: int = 50


def _fetch_historical_sensor_data(
    db: Session,
    machine_id: str,
    limit: int = HISTORY_WINDOW,
) -> list[dict]:
    """Return the last *limit* sensor_data dicts for *machine_id*."""
    rows = (
        db.query(Telemetry.sensor_data)
        .filter(Telemetry.machine_id == machine_id)
        .order_by(desc(Telemetry.timestamp))
        .limit(limit)
        .all()
    )
    return [r[0] for r in rows if r[0] is not None]


def _compute_stats(history: list[dict]) -> tuple[Dict[str, float], Dict[str, float]]:
    """Compute per-sensor mean and std from a list of sensor dicts.

    Returns ``(means, stds)`` where each is a ``{sensor_name: value}`` dict.
    Sensors with < 2 data-points get ``std = 1.0`` to avoid division-by-zero.
    """
    buckets: Dict[str, list[float]] = defaultdict(list)
    for reading in history:
        for key, val in reading.items():
            try:
                buckets[key].append(float(val))
            except (TypeError, ValueError):
                continue

    means: Dict[str, float] = {}
    stds: Dict[str, float] = {}
    for key, values in buckets.items():
        arr = np.array(values)
        means[key] = float(np.mean(arr))
        stds[key] = float(np.std(arr)) if len(arr) >= 2 else 1.0
        # Guard against zero-std (constant sensor)
        if stds[key] < 1e-9:
            stds[key] = 1.0

    return means, stds


def telemetry_ingest_node(state: dict) -> dict:
    """LangGraph node: compute z-scores and flag anomalous sensors.

    **Expects in state:** ``machine_id``, ``sensor_data``, ``db_session``

    **Adds to state:** ``anomaly_flags``, ``z_scores``, ``severity``
    """
    machine_id: str = state["machine_id"]
    sensor_data: dict = state["sensor_data"]
    db: Session = state["db_session"]

    # ------------------------------------------------------------------
    # 1. Fetch historical readings
    # ------------------------------------------------------------------
    history = _fetch_historical_sensor_data(db, machine_id)

    if not history:
        # First reading ever -- nothing to compare against; mark low.
        logger.info("No historical data for machine %s -- defaulting to 'low'", machine_id)
        sensor_keys = list(sensor_data.keys())
        return {
            "anomaly_flags": {k: False for k in sensor_keys},
            "z_scores": {k: 0.0 for k in sensor_keys},
            "severity": "low",
        }

    # ------------------------------------------------------------------
    # 2. Compute statistics and z-scores
    # ------------------------------------------------------------------
    means, stds = _compute_stats(history)

    z_scores: Dict[str, float] = {}
    anomaly_flags: Dict[str, bool] = {}

    for sensor_name, raw_value in sensor_data.items():
        try:
            val = float(raw_value)
        except (TypeError, ValueError):
            z_scores[sensor_name] = 0.0
            anomaly_flags[sensor_name] = False
            continue

        if sensor_name in means:
            z = (val - means[sensor_name]) / stds[sensor_name]
        else:
            z = 0.0  # unseen sensor -- cannot evaluate

        z_scores[sensor_name] = round(z, 4)
        anomaly_flags[sensor_name] = abs(z) > Z_MEDIUM_THRESHOLD

    # ------------------------------------------------------------------
    # 3. Determine overall severity
    # ------------------------------------------------------------------
    abs_z_values = [abs(v) for v in z_scores.values()]
    max_z = max(abs_z_values) if abs_z_values else 0.0

    if max_z > Z_CRITICAL_THRESHOLD:
        severity = "critical"
    elif max_z > Z_MEDIUM_THRESHOLD:
        severity = "medium"
    else:
        severity = "low"

    logger.info(
        "Machine %s ingest complete -- severity=%s, max|z|=%.2f",
        machine_id,
        severity,
        max_z,
    )

    return {
        "anomaly_flags": anomaly_flags,
        "z_scores": z_scores,
        "severity": severity,
    }
