"""SHAP-based anomaly explainer backed by IsolationForest.

Loads a pre-trained model from ``backend/models/anomaly_model.joblib`` when
available; otherwise trains a default IsolationForest on synthetic operating
data so the rest of the pipeline can still function.
"""
from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Feature ordering -- every vector MUST follow this order
# ---------------------------------------------------------------------------
FEATURE_NAMES: List[str] = [
    "engine_rpm",
    "engine_temperature",
    "vibration_level",
    "oil_pressure",
    "fuel_consumption",
]

# ---------------------------------------------------------------------------
# Lazy-loaded singletons (populated by _ensure_model)
# ---------------------------------------------------------------------------
_model = None
_explainer = None
_model_loaded: bool = False

# Path to persisted model (project-root relative)
_MODEL_DIR = Path(__file__).resolve().parents[3] / "models"
_MODEL_PATH = _MODEL_DIR / "anomaly_model.joblib"


def _generate_synthetic_training_data(n_samples: int = 500) -> np.ndarray:
    """Return (n_samples, 5) array of 'normal' operating telemetry."""
    rng = np.random.RandomState(42)
    return np.column_stack(
        [
            rng.normal(1500, 200, n_samples),   # engine_rpm
            rng.normal(85, 8, n_samples),        # engine_temperature (C)
            rng.normal(2.5, 0.8, n_samples),     # vibration_level (mm/s)
            rng.normal(45, 5, n_samples),         # oil_pressure (psi)
            rng.normal(12, 2, n_samples),         # fuel_consumption (L/hr)
        ]
    )


def _ensure_model() -> None:
    """Lazy-load or create the IsolationForest + SHAP explainer."""
    global _model, _explainer, _model_loaded  # noqa: PLW0603

    if _model_loaded:
        return

    try:
        from sklearn.ensemble import IsolationForest
        import joblib
        import shap
    except ImportError as exc:
        logger.error("Required packages missing (sklearn / shap / joblib): %s", exc)
        _model_loaded = True  # prevent retry loop
        return

    # 1. Try loading persisted model -----------------------------------------
    if _MODEL_PATH.exists():
        try:
            _model = joblib.load(_MODEL_PATH)
            logger.info("Loaded anomaly model from %s", _MODEL_PATH)
        except Exception:
            logger.warning("Failed to load model from %s, will retrain", _MODEL_PATH, exc_info=True)
            _model = None

    # 2. Fallback: train on synthetic data -----------------------------------
    if _model is None:
        logger.info("Training default IsolationForest on synthetic data ...")
        X_train = _generate_synthetic_training_data()
        _model = IsolationForest(
            n_estimators=150,
            contamination=0.05,
            random_state=42,
        )
        _model.fit(X_train)

        # Persist so subsequent restarts are faster
        try:
            _MODEL_DIR.mkdir(parents=True, exist_ok=True)
            joblib.dump(_model, _MODEL_PATH)
            logger.info("Saved default model to %s", _MODEL_PATH)
        except OSError:
            logger.warning("Could not persist model to %s", _MODEL_PATH, exc_info=True)

    # 3. Build SHAP explainer ------------------------------------------------
    try:
        _explainer = shap.TreeExplainer(_model)
    except Exception:
        logger.warning("SHAP TreeExplainer creation failed", exc_info=True)

    _model_loaded = True


def _sensor_dict_to_array(sensor_data: dict) -> np.ndarray:
    """Convert a sensor dict to a (1, n_features) numpy array.

    Missing features default to 0.0 so the model always receives the
    correct number of columns.
    """
    return np.array(
        [[float(sensor_data.get(f, 0.0)) for f in FEATURE_NAMES]]
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def explain(sensor_data: dict) -> Dict[str, float]:
    """Return top-5 SHAP feature importances for *sensor_data*.

    Returns an empty dict if the model or explainer is unavailable.
    """
    _ensure_model()

    if _explainer is None or _model is None:
        logger.warning("SHAP explainer unavailable -- returning empty importances")
        return {}

    try:
        X = _sensor_dict_to_array(sensor_data)
        shap_values = _explainer.shap_values(X)

        # shap_values may be a list (one array per class) or a 2-D array
        if isinstance(shap_values, list):
            vals = np.abs(shap_values[0][0])
        else:
            vals = np.abs(shap_values[0])

        ranked = sorted(
            zip(FEATURE_NAMES, vals.tolist()),
            key=lambda t: t[1],
            reverse=True,
        )
        return {name: round(value, 6) for name, value in ranked[:5]}
    except Exception:
        logger.error("SHAP explain failed", exc_info=True)
        return {}


def predict_anomaly(sensor_data: dict) -> Tuple[bool, float]:
    """Return ``(is_anomaly, anomaly_score)`` for the given reading.

    ``anomaly_score`` is the raw *decision_function* value from
    IsolationForest (negative = more anomalous).  ``is_anomaly`` is True
    when the model predicts -1.
    """
    _ensure_model()

    if _model is None:
        logger.warning("Anomaly model unavailable -- defaulting to (False, 0.0)")
        return False, 0.0

    try:
        X = _sensor_dict_to_array(sensor_data)
        prediction = int(_model.predict(X)[0])
        score = float(_model.decision_function(X)[0])
        return prediction == -1, round(score, 6)
    except Exception:
        logger.error("Anomaly prediction failed", exc_info=True)
        return False, 0.0
