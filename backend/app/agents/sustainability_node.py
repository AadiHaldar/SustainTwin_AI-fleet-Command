"""Sustainability node -- carbon-impact estimation and green recommendations.

Calculates the incremental CO2 footprint of the detected anomaly and
generates a targeted sustainability recommendation.
"""
from __future__ import annotations

import logging
from typing import Dict

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Default factors (overridden by Settings when available)
# ---------------------------------------------------------------------------
_DEFAULT_FUEL_CO2_KG_PER_LITER: float = 2.31   # diesel combustion
_DEFAULT_IDLE_CO2_KG_PER_HR: float = 2.68       # EPA heavy-machinery idle


def _load_factors() -> tuple[float, float]:
    """Load CO2 factors from app settings, with safe fallback."""
    try:
        from app.core.config import get_settings
        settings = get_settings()
        return settings.FUEL_CO2_KG_PER_LITER, settings.IDLE_CO2_KG_PER_HR
    except Exception:
        return _DEFAULT_FUEL_CO2_KG_PER_LITER, _DEFAULT_IDLE_CO2_KG_PER_HR


def _compute_carbon_delta(
    sensor_data: dict,
    anomaly_flags: dict,
    z_scores: dict,
    fuel_co2: float,
    idle_co2: float,
) -> float:
    """Estimate excess CO2 (kg) caused by the detected anomaly.

    Heuristics:
    * **High RPM anomaly** -- excess RPM drives proportionally higher fuel
      burn: ``(excess_rpm / 2000) * fuel_consumption * fuel_co2``.
    * **High temperature anomaly** -- assumed to cause an idle/shutdown
      penalty: ``idle_co2 * estimated_hours_lost`` (hours estimated from
      the temperature z-score magnitude).
    * **General / other** -- small fixed penalty scaled by the worst
      z-score.
    """
    carbon = 0.0

    rpm_val = float(sensor_data.get("engine_rpm", 0))
    temp_val = float(sensor_data.get("engine_temperature", 0))
    fuel_val = float(sensor_data.get("fuel_consumption", 0))

    rpm_anomalous = anomaly_flags.get("engine_rpm", False)
    temp_anomalous = anomaly_flags.get("engine_temperature", False)

    rpm_z = abs(z_scores.get("engine_rpm", 0.0))
    temp_z = abs(z_scores.get("engine_temperature", 0.0))

    if rpm_anomalous and rpm_z > 0:
        # Excess RPM above nominal (1500 baseline)
        excess_rpm = max(rpm_val - 1500, 0)
        carbon += (excess_rpm / 2000.0) * max(fuel_val, 1.0) * fuel_co2

    if temp_anomalous and temp_z > 0:
        # Temperature anomaly implies potential forced cooldown / idle hours
        # Rough estimate: each unit of z above threshold ~ 0.5 hr downtime
        estimated_hours = max(temp_z - 2.0, 0.0) * 0.5
        carbon += idle_co2 * estimated_hours

    # General fallback if no specific anomaly matched but severity != low
    if carbon < 0.01:
        worst_z = max((abs(v) for v in z_scores.values()), default=0.0)
        carbon = worst_z * 0.3 * fuel_co2  # conservative estimate

    return round(carbon, 4)


def _generate_recommendation(
    sensor_data: dict,
    anomaly_flags: dict,
    z_scores: dict,
    carbon_delta_kg: float,
    diagnosis: dict | None,
) -> str:
    """Generate one specific, actionable sustainability recommendation."""
    rpm_anomalous = anomaly_flags.get("engine_rpm", False)
    temp_anomalous = anomaly_flags.get("engine_temperature", False)
    vib_anomalous = anomaly_flags.get("vibration_level", False)
    oil_anomalous = anomaly_flags.get("oil_pressure", False)

    parts: list[str] = []

    if rpm_anomalous:
        rpm_val = float(sensor_data.get("engine_rpm", 0))
        parts.append(
            f"Reduce engine RPM from {rpm_val:.0f} to the nominal 1500 RPM band "
            f"to cut excess fuel burn. Estimated CO2 saving: {carbon_delta_kg:.2f} kg per incident."
        )
    elif temp_anomalous:
        temp_val = float(sensor_data.get("engine_temperature", 0))
        parts.append(
            f"Investigate cooling subsystem -- engine temperature at {temp_val:.1f} C "
            f"is significantly above baseline. Scheduling a coolant flush could prevent "
            f"thermal shutdowns that waste {carbon_delta_kg:.2f} kg CO2 in idle penalties."
        )
    elif vib_anomalous:
        parts.append(
            "Elevated vibration suggests bearing or alignment degradation. "
            "Proactive replacement avoids catastrophic failure that would "
            f"incur up to {carbon_delta_kg * 3:.2f} kg CO2 in emergency repairs and downtime."
        )
    elif oil_anomalous:
        parts.append(
            "Oil pressure deviation detected. Schedule an oil analysis and filter "
            "replacement to prevent accelerated engine wear and the associated "
            f"carbon cost of premature part manufacturing ({carbon_delta_kg:.2f} kg CO2 equivalent)."
        )
    else:
        root_cause = (diagnosis or {}).get("root_cause", "anomaly")
        parts.append(
            f"Address the detected {root_cause} promptly. "
            f"Early resolution saves an estimated {carbon_delta_kg:.2f} kg CO2 "
            "compared to running until unplanned failure."
        )

    return " ".join(parts)


def sustainability_node(state: dict) -> dict:
    """LangGraph node: estimate carbon impact and recommend green action.

    **Expects in state:** ``sensor_data``, ``anomaly_flags``, ``z_scores``,
    ``diagnosis`` (may be None)

    **Adds to state:** ``sustainability`` dict with keys
    ``carbon_delta_kg`` and ``sustainability_recommendation``.
    """
    sensor_data: dict = state.get("sensor_data", {})
    anomaly_flags: dict = state.get("anomaly_flags", {})
    z_scores: dict = state.get("z_scores", {})
    diagnosis: dict | None = state.get("diagnosis")

    fuel_co2, idle_co2 = _load_factors()

    carbon_delta_kg = _compute_carbon_delta(
        sensor_data, anomaly_flags, z_scores, fuel_co2, idle_co2,
    )

    recommendation = _generate_recommendation(
        sensor_data, anomaly_flags, z_scores, carbon_delta_kg, diagnosis,
    )

    logger.info(
        "Sustainability: carbon_delta=%.4f kg CO2, recommendation=%s",
        carbon_delta_kg,
        recommendation[:100],
    )

    return {
        "sustainability": {
            "carbon_delta_kg": carbon_delta_kg,
            "sustainability_recommendation": recommendation,
        },
    }
