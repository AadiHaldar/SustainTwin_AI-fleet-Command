from sqlalchemy import Column, String, Float, DateTime, Integer, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class Machine(Base):
    __tablename__ = "machines"

    id = Column(String, primary_key=True, index=True)
    type = Column(String, index=True) # e.g., "Excavator", "Haul Truck"
    model = Column(String)
    location_lat = Column(Float)
    location_lon = Column(Float)
    operating_hours = Column(Float, default=0.0)
    status = Column(String, default="Active") # Active, Maintenance, Offline
    
    telemetry = relationship("Telemetry", back_populates="machine")

class Telemetry(Base):
    __tablename__ = "telemetry"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    machine_id = Column(String, ForeignKey("machines.id"))
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Telemetry metrics
    engine_rpm = Column(Float)
    engine_temperature = Column(Float)
    oil_pressure = Column(Float)
    vibration_level = Column(Float)
    fuel_consumption = Column(Float)
    
    # Target / Anomaly flag
    failure_risk = Column(Float, default=0.0)
    is_anomaly = Column(Boolean, default=False)
    
    machine = relationship("Machine", back_populates="telemetry")
