from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, JSON, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class Machine(Base):
    __tablename__ = "machines"

    id = Column(String, primary_key=True, index=True)
    machine_type = Column(String)
    status = Column(String, default="Nominal")
    
    # Relationships
    telemetry = relationship("Telemetry", back_populates="machine")

class Telemetry(Base):
    __tablename__ = "telemetry"

    id = Column(Integer, primary_key=True, index=True)
    machine_id = Column(String, ForeignKey("machines.id"))
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Generic JSON column to store ANY Kaggle dataset schema dynamically
    # e.g., {"engine_rpm": 1200, "vibration_level": 12} OR {"voltage": 160.2, "pressure": 101.4}
    sensor_data = Column(JSON)
    
    failure_risk = Column(Float, default=0.0)
    is_anomaly = Column(Boolean, default=False)
    
    machine = relationship("Machine", back_populates="telemetry")
