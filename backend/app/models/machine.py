from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, JSON, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.core.database import Base


class Machine(Base):
    __tablename__ = "machines"

    id = Column(String, primary_key=True, index=True)
    machine_type = Column(String)
    status = Column(String, default="Nominal")

    # Relationships
    telemetry = relationship("Telemetry", back_populates="machine")
    diagnoses = relationship("Diagnosis", back_populates="machine")


class Telemetry(Base):
    __tablename__ = "telemetry"

    id = Column(Integer, primary_key=True, index=True)
    machine_id = Column(String, ForeignKey("machines.id"), index=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    # Generic JSON column to store ANY dataset schema dynamically
    sensor_data = Column(JSON)

    failure_risk = Column(Float, default=0.0)
    is_anomaly = Column(Boolean, default=False)

    machine = relationship("Machine", back_populates="telemetry")
