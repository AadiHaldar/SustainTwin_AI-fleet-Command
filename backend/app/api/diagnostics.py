"""Diagnostics API -- browse agent-generated diagnoses."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import require_role
from app.models.diagnosis import Diagnosis

router = APIRouter()


@router.get("/")
def list_recent_diagnoses(
    db: Session = Depends(get_db),
    current_user=Depends(require_role("engineer", "admin")),
):
    """Return the 50 most recent diagnoses across all machines."""
    diagnoses = (
        db.query(Diagnosis)
        .order_by(Diagnosis.timestamp.desc())
        .limit(50)
        .all()
    )

    return [
        {
            "id": d.id,
            "machine_id": d.machine_id,
            "telemetry_id": d.telemetry_id,
            "timestamp": d.timestamp.isoformat() if d.timestamp else None,
            "severity": d.severity,
            "root_cause": d.root_cause,
            "confidence": d.confidence,
            "recommended_action": d.recommended_action,
            "urgency": d.urgency,
            "shap_values": d.shap_values,
            "carbon_delta_kg": d.carbon_delta_kg,
            "sustainability_recommendation": d.sustainability_recommendation,
            "anomaly_flags": d.anomaly_flags,
            "z_scores": d.z_scores,
        }
        for d in diagnoses
    ]


@router.get("/{machine_id}")
def get_machine_diagnoses(
    machine_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_role("engineer", "admin")),
):
    """Return diagnosis history for a specific machine (latest first)."""
    diagnoses = (
        db.query(Diagnosis)
        .filter(Diagnosis.machine_id == machine_id)
        .order_by(Diagnosis.timestamp.desc())
        .limit(50)
        .all()
    )

    return [
        {
            "id": d.id,
            "machine_id": d.machine_id,
            "telemetry_id": d.telemetry_id,
            "timestamp": d.timestamp.isoformat() if d.timestamp else None,
            "severity": d.severity,
            "root_cause": d.root_cause,
            "confidence": d.confidence,
            "recommended_action": d.recommended_action,
            "urgency": d.urgency,
            "shap_values": d.shap_values,
            "carbon_delta_kg": d.carbon_delta_kg,
            "sustainability_recommendation": d.sustainability_recommendation,
            "anomaly_flags": d.anomaly_flags,
            "z_scores": d.z_scores,
        }
        for d in diagnoses
    ]
