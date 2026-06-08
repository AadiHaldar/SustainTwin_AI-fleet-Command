"""
The machine behavior model is the heart of the digital twin.

It learns the NORMAL relationships between sensors from historical data:
  Given: engine_rpm (the primary input — operator-controlled)
  Predict: engine_temperature, vibration_level, oil_pressure, fuel_consumption

This captures physics: higher RPM → higher temp, higher vibration, more fuel burned.
Anomalies are detected when reality diverges from these learned relationships.
"""
from __future__ import annotations

import os
import logging
import numpy as np
from typing import Dict, Optional

logger = logging.getLogger(__name__)

# Singleton models — loaded once at startup
_models: Dict[str, object] = {}
_feature_stats: Optional[Dict] = None  # mean/std per sensor for z-score normalization

MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "models")


def _model_path(sensor: str) -> str:
    return os.path.join(MODEL_DIR, f"twin_{sensor}.joblib")


def train_behavior_models(db_session) -> None:
    """
    Train one GradientBoostingRegressor per predicted sensor.
    Only trained on NON-anomaly rows so the model learns healthy behavior.
    
    Input feature: engine_rpm (single regressor — it's the clearest causal driver)
    Targets: engine_temperature, vibration_level, oil_pressure, fuel_consumption
    
    Called from ingest_data.py after telemetry is seeded.
    """
    import joblib
    from sklearn.ensemble import GradientBoostingRegressor
    from sklearn.preprocessing import StandardScaler
    from app.models.machine import Telemetry

    logger.info("[TWIN] Training machine behavior models on healthy telemetry...")

    rows = db_session.query(Telemetry).filter(Telemetry.is_anomaly == False).all()
    if len(rows) < 50:
        logger.warning("[TWIN] Not enough non-anomaly rows to train twin models (need 50+)")
        return

    # Build feature/target arrays
    X = []  # [engine_rpm]
    Y = {
        "engine_temperature": [],
        "vibration_level": [],
        "oil_pressure": [],
        "fuel_consumption": [],
    }

    for r in rows:
        sd = r.sensor_data or {}
        rpm = sd.get("engine_rpm")
        if rpm is None:
            continue
        X.append([rpm])
        Y["engine_temperature"].append(sd.get("engine_temperature", 0.0))
        Y["vibration_level"].append(sd.get("vibration_level", 0.0))
        Y["oil_pressure"].append(sd.get("oil_pressure", 0.0))
        Y["fuel_consumption"].append(sd.get("fuel_consumption", 0.0))

    X = np.array(X)
    os.makedirs(MODEL_DIR, exist_ok=True)

    for sensor, y_vals in Y.items():
        y = np.array(y_vals)
        model = GradientBoostingRegressor(n_estimators=100, max_depth=3, random_state=42)
        model.fit(X, y)
        joblib.dump(model, _model_path(sensor))
        logger.info("[TWIN] Trained model for %s (n=%d)", sensor, len(y))

    # Save per-sensor stats (mean/std of residuals on training data) for normalization
    stats = {}
    for sensor, y_vals in Y.items():
        import joblib as jl
        model = jl.load(_model_path(sensor))
        preds = model.predict(X)
        residuals = np.array(y_vals) - preds
        stats[sensor] = {"mean": float(residuals.mean()), "std": float(residuals.std()) + 1e-6}

    joblib.dump(stats, os.path.join(MODEL_DIR, "twin_residual_stats.joblib"))
    logger.info("[TWIN] Behavior models trained and saved.")


def load_models() -> bool:
    """Load all twin models into memory. Returns True if successful."""
    import joblib

    targets = ["engine_temperature", "vibration_level", "oil_pressure", "fuel_consumption"]
    for sensor in targets:
        path = _model_path(sensor)
        if not os.path.exists(path):
            logger.warning("[TWIN] Model not found: %s — run ingest_data.py first", path)
            return False
        _models[sensor] = joblib.load(path)

    stats_path = os.path.join(MODEL_DIR, "twin_residual_stats.joblib")
    if os.path.exists(stats_path):
        global _feature_stats
        _feature_stats = joblib.load(stats_path)

    logger.info("[TWIN] Behavior models loaded.")
    return True


def predict(engine_rpm: float) -> Dict[str, float]:
    """
    Given engine_rpm, predict what all other sensors should read.
    Returns predicted values dict.
    """
    if not _models:
        load_models()

    X = np.array([[engine_rpm]])
    predictions = {}
    for sensor, model in _models.items():
        predictions[sensor] = float(model.predict(X)[0])
    return predictions


def compute_divergence(predicted: Dict[str, float], actual: Dict[str, float]) -> tuple[Dict[str, float], float]:
    """
    Compute per-sensor residuals and an overall normalized divergence score.
    
    Divergence score is the mean absolute normalized residual across sensors.
    Score of 0 = perfect twin match. Score > 2.0 = warning. Score > 4.0 = critical.
    """
    residuals = {}
    normalized = []

    for sensor in predicted:
        if sensor not in actual:
            continue
        residual = actual[sensor] - predicted[sensor]
        residuals[sensor] = round(residual, 4)

        # Normalize by training residual std
        if _feature_stats and sensor in _feature_stats:
            std = _feature_stats[sensor]["std"]
            normalized.append(abs(residual) / std)
        else:
            normalized.append(abs(residual))

    divergence_score = float(np.mean(normalized)) if normalized else 0.0
    return residuals, round(divergence_score, 4)
