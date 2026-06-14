import logging
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import require_role
from app.models.machine import Machine, Telemetry
from app.models.diagnosis import Diagnosis

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/")
def get_fleet_stats(
    db: Session = Depends(get_db),
    current_user=Depends(require_role("operator", "engineer", "admin")),
):
    """Compute and return fleet-wide statistics for the dashboard."""
    total_machines = db.query(Machine).count()

    one_day_ago = datetime.now(timezone.utc) - timedelta(days=1)
    
    active_anomalies_24h = (
        db.query(Telemetry)
        .filter(Telemetry.is_anomaly == True, Telemetry.timestamp >= one_day_ago)
        .count()
    )

    avg_confidence = db.query(func.avg(Diagnosis.confidence)).scalar() or 0.0

    total_carbon_saved_kg = db.query(func.sum(Diagnosis.carbon_delta_kg)).scalar() or 0.0

    total_telemetry_24h = (
        db.query(Telemetry)
        .filter(Telemetry.timestamp >= one_day_ago)
        .count()
    )
    
    anomaly_rate_percent = 0.0
    if total_telemetry_24h > 0:
        anomaly_rate_percent = (active_anomalies_24h / total_telemetry_24h) * 100.0

    fleet_health_score = 100.0
    if total_machines > 0:
        # Base it on anomalies per machine. 10 anomalies per machine drops score to 0
        penalty = (active_anomalies_24h / total_machines) * 10 
        fleet_health_score = max(0.0, 100.0 - penalty)

    return {
        "total_machines": total_machines,
        "active_anomalies_24h": active_anomalies_24h,
        "avg_confidence": float(avg_confidence),
        "total_carbon_saved_kg": float(total_carbon_saved_kg),
        "anomaly_rate_percent": float(anomaly_rate_percent),
        "fleet_health_score": float(fleet_health_score),
    }
