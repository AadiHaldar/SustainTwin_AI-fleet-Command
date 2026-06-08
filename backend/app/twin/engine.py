"""
The twin engine is called on every telemetry sync.
It orchestrates: predict → compare → filter → score → persist.
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Dict, Any

from sqlalchemy.orm import Session

from app.twin.machine_model import predict, compute_divergence, load_models
from app.twin.kalman import run_filter
from app.models.twin_state import TwinState

logger = logging.getLogger(__name__)

# Load models once at import
_models_loaded = False


def process(machine_id: str, sensor_data: Dict[str, float], db: Session) -> Dict[str, Any]:
    """
    Full digital twin processing pipeline for one telemetry reading.

    1. Predict what sensors should read given engine_rpm
    2. Compute residuals (actual - predicted) per sensor
    3. Run Kalman filter to get smoothed state estimate
    4. Compute divergence score
    5. Classify divergence level (none / warning / critical)
    6. Persist TwinState to DB
    7. Return full twin result for API response and WebSocket broadcast

    This is the function that makes it a real digital twin, not a dashboard.
    """
    global _models_loaded
    if not _models_loaded:
        _models_loaded = load_models()

    engine_rpm = sensor_data.get("engine_rpm", 1500.0)

    # Step 1: Twin prediction
    predicted = predict(engine_rpm)

    # Step 2: Actual values (subset that we predict)
    actual = {
        "engine_temperature": sensor_data.get("engine_temperature", 0.0),
        "vibration_level": sensor_data.get("vibration_level", 0.0),
        "oil_pressure": sensor_data.get("oil_pressure", 0.0),
        "fuel_consumption": sensor_data.get("fuel_consumption", 0.0),
    }

    # Step 3: Residuals + divergence score
    residuals, divergence_score = compute_divergence(predicted, actual)

    # Step 4: Kalman filtering
    kalman_state = run_filter(machine_id, actual)

    # Step 5: Classify divergence
    if divergence_score > 4.0:
        twin_anomaly = "critical"
    elif divergence_score > 2.0:
        twin_anomaly = "warning"
    else:
        twin_anomaly = "none"

    # Step 6: Persist
    twin_state = TwinState(
        machine_id=machine_id,
        timestamp=datetime.now(timezone.utc),
        predicted_engine_temperature=predicted.get("engine_temperature"),
        predicted_vibration_level=predicted.get("vibration_level"),
        predicted_oil_pressure=predicted.get("oil_pressure"),
        predicted_fuel_consumption=predicted.get("fuel_consumption"),
        actual_engine_temperature=actual["engine_temperature"],
        actual_vibration_level=actual["vibration_level"],
        actual_oil_pressure=actual["oil_pressure"],
        actual_fuel_consumption=actual["fuel_consumption"],
        residuals=residuals,
        kalman_state=kalman_state,
        divergence_score=divergence_score,
        twin_anomaly=twin_anomaly,
    )
    db.add(twin_state)
    db.commit()
    db.refresh(twin_state)

    logger.info(
        "[TWIN] machine=%s divergence=%.3f status=%s",
        machine_id, divergence_score, twin_anomaly
    )

    return {
        "twin_state_id": twin_state.id,
        "predicted": predicted,
        "actual": actual,
        "residuals": residuals,
        "kalman_state": kalman_state,
        "divergence_score": divergence_score,
        "twin_anomaly": twin_anomaly,
    }
