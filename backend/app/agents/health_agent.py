"""Thin public API wrapper around the compiled LangGraph agent.

Usage::

    from app.agents.health_agent import run_health_agent
    result = run_health_agent("machine-001", {"engine_rpm": 2400, ...}, db)
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


def run_health_agent(
    machine_id: str,
    sensor_data: dict,
    db_session: Any,
) -> Dict[str, Any]:
    """Invoke the SustainTwin multi-agent graph and return a flat result dict.

    Parameters
    ----------
    machine_id:
        Unique identifier of the machine being analysed.
    sensor_data:
        Dictionary of current sensor readings (e.g. ``engine_rpm``,
        ``engine_temperature``, ``vibration_level``, ``oil_pressure``,
        ``fuel_consumption``).
    db_session:
        An active SQLAlchemy ``Session`` used by the ingest node to query
        historical telemetry.

    Returns
    -------
    dict with keys:
        - ``severity`` (str): 'low', 'medium', or 'critical'
        - ``diagnosis`` (dict | None): root_cause, confidence, recommended_action, urgency
        - ``sustainability`` (dict | None): carbon_delta_kg, sustainability_recommendation
        - ``shap_values`` (dict | None): per-feature SHAP importances
        - ``anomaly_flags`` (dict | None): per-sensor boolean flags
        - ``z_scores`` (dict | None): per-sensor z-score values
    """
    from app.agents.graph import agent_graph

    initial_state: Dict[str, Any] = {
        "machine_id": machine_id,
        "sensor_data": sensor_data,
        "db_session": db_session,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    try:
        result = agent_graph.invoke(initial_state)
    except Exception:
        logger.error(
            "Agent graph invocation failed for machine %s",
            machine_id,
            exc_info=True,
        )
        return {
            "severity": "low",
            "diagnosis": None,
            "sustainability": None,
            "shap_values": None,
            "anomaly_flags": None,
            "z_scores": None,
        }

    return {
        "severity": result.get("severity", "low"),
        "diagnosis": result.get("diagnosis"),
        "sustainability": result.get("sustainability"),
        "shap_values": result.get("shap_values"),
        "anomaly_flags": result.get("anomaly_flags"),
        "z_scores": result.get("z_scores"),
    }
