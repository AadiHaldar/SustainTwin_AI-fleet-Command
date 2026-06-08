"""Digital Twin API — query twin state and divergence history."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import require_role
from app.models.twin_state import TwinState

router = APIRouter()


@router.get("/{machine_id}/state")
def get_twin_state(
    machine_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_role("operator", "engineer", "admin")),
):
    """Return the latest twin state for a machine — predicted vs actual vs Kalman."""
    state = (
        db.query(TwinState)
        .filter(TwinState.machine_id == machine_id)
        .order_by(TwinState.timestamp.desc())
        .first()
    )
    if not state:
        return {"message": "No twin state yet — send telemetry first"}

    return {
        "machine_id": machine_id,
        "timestamp": state.timestamp.isoformat(),
        "predicted": {
            "engine_temperature": state.predicted_engine_temperature,
            "vibration_level": state.predicted_vibration_level,
            "oil_pressure": state.predicted_oil_pressure,
            "fuel_consumption": state.predicted_fuel_consumption,
        },
        "actual": {
            "engine_temperature": state.actual_engine_temperature,
            "vibration_level": state.actual_vibration_level,
            "oil_pressure": state.actual_oil_pressure,
            "fuel_consumption": state.actual_fuel_consumption,
        },
        "kalman_state": state.kalman_state,
        "residuals": state.residuals,
        "divergence_score": state.divergence_score,
        "twin_anomaly": state.twin_anomaly,
    }


@router.get("/{machine_id}/history")
def get_twin_history(
    machine_id: str,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user=Depends(require_role("operator", "engineer", "admin")),
):
    """Return divergence score history — used to plot twin vs reality over time."""
    states = (
        db.query(TwinState)
        .filter(TwinState.machine_id == machine_id)
        .order_by(TwinState.timestamp.desc())
        .limit(limit)
        .all()
    )

    return [
        {
            "timestamp": s.timestamp.isoformat(),
            "divergence_score": s.divergence_score,
            "twin_anomaly": s.twin_anomaly,
            "residuals": s.residuals,
            "predicted": {
                "engine_temperature": s.predicted_engine_temperature,
                "vibration_level": s.predicted_vibration_level,
            },
            "actual": {
                "engine_temperature": s.actual_engine_temperature,
                "vibration_level": s.actual_vibration_level,
            },
            "kalman_state": s.kalman_state,
        }
        for s in reversed(states)
    ]


@router.get("/fleet/divergence")
def get_fleet_divergence(
    db: Session = Depends(get_db),
    current_user=Depends(require_role("operator", "engineer", "admin")),
):
    """Return latest divergence score for every machine — fleet health overview."""
    from sqlalchemy import func
    from app.models.machine import Machine

    machines = db.query(Machine).all()
    results = []

    for m in machines:
        latest = (
            db.query(TwinState)
            .filter(TwinState.machine_id == m.id)
            .order_by(TwinState.timestamp.desc())
            .first()
        )
        results.append({
            "machine_id": m.id,
            "machine_type": m.machine_type,
            "divergence_score": latest.divergence_score if latest else None,
            "twin_anomaly": latest.twin_anomaly if latest else "unknown",
            "last_seen": latest.timestamp.isoformat() if latest else None,
        })

    return results
