"""Telemetry API -- ingest, query, and stream machine sensor data."""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import require_role, get_current_user
from app.core.redis import cache_latest_telemetry, get_cached_telemetry
from app.models.machine import Machine, Telemetry
from app.models.diagnosis import Diagnosis
from app.api.websocket import manager

logger = logging.getLogger(__name__)

router = APIRouter()


# ---------------------------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------------------------

class TelemetryPayload(BaseModel):
    machine_id: str
    timestamp: Optional[datetime] = None
    sensor_data: dict
    is_anomaly: bool = Field(default=False)


# ---------------------------------------------------------------------------
# Helper: run agent + persist diagnosis (called in background or inline)
# ---------------------------------------------------------------------------

def _run_agent_and_save(machine_id: str, sensor_data: dict, telemetry_id: int, db: Session):
    """Invoke the health agent, persist diagnosis, cache in Redis."""
    try:
        from app.agents.health_agent import run_health_agent

        # Call the new multi-agent graph
        result = run_health_agent(
            machine_id=machine_id,
            sensor_data=sensor_data,
            db_session=db,
        )

        severity = result.get("severity", "low")
        diagnosis_data = result.get("diagnosis") or {}
        sustainability_data = result.get("sustainability") or {}

        diagnosis = Diagnosis(
            machine_id=machine_id,
            telemetry_id=telemetry_id,
            severity=severity,
            root_cause=diagnosis_data.get("root_cause"),
            confidence=diagnosis_data.get("confidence"),
            recommended_action=diagnosis_data.get("recommended_action"),
            urgency=diagnosis_data.get("urgency"),
            shap_values=result.get("shap_values"),
            anomaly_flags=result.get("anomaly_flags"),
            z_scores=result.get("z_scores"),
            carbon_delta_kg=sustainability_data.get("carbon_delta_kg", 0.0),
            sustainability_recommendation=sustainability_data.get("sustainability_recommendation"),
        )
        db.add(diagnosis)
        db.commit()
        db.refresh(diagnosis)

        # Cache in Redis
        from app.core.redis import cache_diagnosis
        cache_diagnosis(machine_id, {
            "id": diagnosis.id,
            "machine_id": machine_id,
            "severity": severity,
            "root_cause": diagnosis.root_cause,
            "confidence": diagnosis.confidence,
            "recommended_action": diagnosis.recommended_action,
            "urgency": diagnosis.urgency,
            "shap_values": diagnosis.shap_values,
            "carbon_delta_kg": diagnosis.carbon_delta_kg,
            "sustainability_recommendation": diagnosis.sustainability_recommendation,
            "timestamp": diagnosis.timestamp.isoformat() if diagnosis.timestamp else None,
        })

        logger.info("Diagnosis saved for machine %s (severity=%s)", machine_id, severity)
        return {
            "severity": severity,
            "diagnosis": {
                "id": diagnosis.id,
                "root_cause": diagnosis.root_cause,
                "confidence": diagnosis.confidence,
                "recommended_action": diagnosis.recommended_action,
                "urgency": diagnosis.urgency,
            },
            "sustainability": {
                "carbon_delta_kg": diagnosis.carbon_delta_kg,
                "recommendation": diagnosis.sustainability_recommendation,
            },
            "shap_values": diagnosis.shap_values,
        }

    except Exception as exc:
        logger.error("Agent failed for machine %s: %s", machine_id, exc, exc_info=True)
        return {"severity": "unknown", "diagnosis": None, "error": str(exc)}


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.post("/sync")
async def sync_telemetry(
    payload: TelemetryPayload,
    db: Session = Depends(get_db),
    current_user=Depends(require_role("engineer", "admin")),
):
    """Receive telemetry from edge/simulator, save to DB, optionally trigger agent."""

    # Ensure the machine exists
    machine = db.query(Machine).filter(Machine.id == payload.machine_id).first()
    if not machine:
        raise HTTPException(status_code=404, detail=f"Machine '{payload.machine_id}' not found")

    # Persist telemetry
    ts = payload.timestamp or datetime.now(timezone.utc)
    telemetry = Telemetry(
        machine_id=payload.machine_id,
        timestamp=ts,
        sensor_data=payload.sensor_data,
        is_anomaly=payload.is_anomaly,
        failure_risk=0.0,
    )
    db.add(telemetry)
    db.commit()
    db.refresh(telemetry)

    # Cache latest reading in Redis
    cache_payload = {
        "id": telemetry.id,
        "machine_id": telemetry.machine_id,
        "timestamp": telemetry.timestamp.isoformat() if telemetry.timestamp else None,
        "sensor_data": telemetry.sensor_data,
        "is_anomaly": telemetry.is_anomaly,
    }
    cache_latest_telemetry(payload.machine_id, cache_payload)

    # If anomaly flagged, run agent synchronously
    agent_result = None
    if payload.is_anomaly:
        logger.info("[ALERT] Anomaly flagged for %s -- triggering health agent", payload.machine_id)
        agent_result = _run_agent_and_save(
            payload.machine_id, payload.sensor_data, telemetry.id, db
        )

    # Broadcast via WebSocket (fire-and-forget in the event loop)
    broadcast_msg = {
        "type": "telemetry_sync",
        "machine_id": payload.machine_id,
        "timestamp": cache_payload["timestamp"],
        "sensor_data": payload.sensor_data,
        "is_anomaly": payload.is_anomaly,
        "agent_result": agent_result,
    }
    try:
        asyncio.get_event_loop().create_task(manager.broadcast(broadcast_msg))
    except RuntimeError:
        pass  # no running loop (testing context)

    return {
        "status": "success",
        "telemetry_id": telemetry.id,
        "recorded_at": cache_payload["timestamp"],
        "agent_result": agent_result,
    }


@router.get("/")
def list_latest_telemetry(
    db: Session = Depends(get_db),
    current_user=Depends(require_role("operator", "engineer", "admin")),
):
    """Return the latest telemetry reading for every known machine.

    Checks Redis cache first; falls back to DB on miss.
    """
    machines = db.query(Machine).all()
    results = []

    for m in machines:
        # Try Redis first
        cached = get_cached_telemetry(m.id)
        if cached:
            results.append(cached)
            continue

        # Fallback: DB query
        latest = (
            db.query(Telemetry)
            .filter(Telemetry.machine_id == m.id)
            .order_by(Telemetry.timestamp.desc())
            .first()
        )
        if latest:
            entry = {
                "id": latest.id,
                "machine_id": latest.machine_id,
                "timestamp": latest.timestamp.isoformat() if latest.timestamp else None,
                "sensor_data": latest.sensor_data,
                "is_anomaly": latest.is_anomaly,
            }
            # Warm the cache for next time
            cache_latest_telemetry(m.id, entry)
            results.append(entry)

    return results


@router.get("/{machine_id}")
def get_machine_telemetry(
    machine_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_role("operator", "engineer", "admin")),
):
    """Return telemetry history for a specific machine (last 100 readings)."""
    readings = (
        db.query(Telemetry)
        .filter(Telemetry.machine_id == machine_id)
        .order_by(Telemetry.timestamp.desc())
        .limit(100)
        .all()
    )

    return [
        {
            "id": r.id,
            "machine_id": r.machine_id,
            "timestamp": r.timestamp.isoformat() if r.timestamp else None,
            "sensor_data": r.sensor_data,
            "is_anomaly": r.is_anomaly,
            "failure_risk": r.failure_risk,
        }
        for r in readings
    ]
