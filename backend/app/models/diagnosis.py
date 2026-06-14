from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from app.core.database import Base


class Diagnosis(Base):
    __tablename__ = "diagnoses"
    __table_args__ = (
        Index('idx_diagnosis_machine_time', 'machine_id', 'timestamp'),
    )

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    machine_id = Column(String, ForeignKey("machines.id"), index=True)
    telemetry_id = Column(Integer, ForeignKey("telemetry.id"), nullable=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    # Agent outputs
    severity = Column(String)  # low, medium, critical
    root_cause = Column(String, nullable=True)
    confidence = Column(Float, nullable=True)
    recommended_action = Column(String, nullable=True)
    urgency = Column(String, nullable=True)

    # XAI
    shap_values = Column(JSON, nullable=True)  # {"vibration_level": 0.43, ...}

    # Sustainability
    carbon_delta_kg = Column(Float, default=0.0)
    sustainability_recommendation = Column(String, nullable=True)

    # Raw agent state
    anomaly_flags = Column(JSON, nullable=True)
    z_scores = Column(JSON, nullable=True)

    # Relationships
    machine = relationship("Machine", back_populates="diagnoses")
