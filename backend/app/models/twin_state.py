from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.core.database import Base

class TwinState(Base):
    __tablename__ = "twin_states"

    id = Column(Integer, primary_key=True, index=True)
    machine_id = Column(String, ForeignKey("machines.id"), index=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    # What the twin predicts given current inputs
    predicted_engine_temperature = Column(Float)
    predicted_vibration_level = Column(Float)
    predicted_oil_pressure = Column(Float)
    predicted_fuel_consumption = Column(Float)

    # Actual readings at this moment
    actual_engine_temperature = Column(Float)
    actual_vibration_level = Column(Float)
    actual_oil_pressure = Column(Float)
    actual_fuel_consumption = Column(Float)

    # Residuals (actual - predicted) per sensor
    residuals = Column(JSON)  # {"engine_temperature": 4.2, "vibration_level": -0.3, ...}

    # Kalman-filtered estimated true state
    kalman_state = Column(JSON)  # {"engine_temperature": 85.1, "vibration_level": 3.2, ...}

    # Divergence score (0 = perfect match, higher = more anomalous)
    divergence_score = Column(Float, default=0.0)

    # Did the twin flag this as a divergence event?
    twin_anomaly = Column(String, default="none")  # "none", "warning", "critical"

    machine = relationship("Machine")
