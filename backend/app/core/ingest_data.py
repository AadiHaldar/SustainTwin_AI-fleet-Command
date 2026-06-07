"""Data ingestion script -- seeds machines, users, telemetry, and trains anomaly model.

Run standalone:  python -m app.core.ingest_data
"""

import os
import sys
import random
from datetime import datetime, timedelta, timezone

import pandas as pd
from datasets import load_dataset
from sqlalchemy.orm import Session

# Ensure app is importable when run as script
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app.core.database import SessionLocal, engine, Base
from app.core.security import get_password_hash
from app.models.machine import Machine, Telemetry
from app.models.user import User


# ---------------------------------------------------------------------------
# DB bootstrap
# ---------------------------------------------------------------------------

def init_db():
    import app.models.machine     # noqa: F401
    import app.models.user        # noqa: F401
    import app.models.diagnosis   # noqa: F401
    Base.metadata.create_all(bind=engine)


# ---------------------------------------------------------------------------
# Seed machines
# ---------------------------------------------------------------------------

def seed_machines(db: Session, num_machines: int = 5):
    machine_types = ["Excavator", "Haul Truck", "Bulldozer", "Loader", "Crane"]
    machines = []
    for i in range(num_machines):
        m = Machine(
            id=f"M-{100 + i}",
            machine_type=machine_types[i % len(machine_types)],
            status="Nominal",
        )
        machines.append(m)
        db.add(m)
    db.commit()
    print(f"[SEED] Created {len(machines)} machines")
    return machines


# ---------------------------------------------------------------------------
# Seed users
# ---------------------------------------------------------------------------

def seed_users(db: Session):
    users = [
        {"username": "operator", "password": "operator123", "role": "operator"},
        {"username": "engineer", "password": "engineer123", "role": "engineer"},
        {"username": "admin", "password": "admin123", "role": "admin"},
    ]
    created = 0
    for u in users:
        existing = db.query(User).filter(User.username == u["username"]).first()
        if existing:
            continue
        user = User(
            username=u["username"],
            hashed_password=get_password_hash(u["password"]),
            role=u["role"],
            is_active=True,
        )
        db.add(user)
        created += 1

    db.commit()
    print(f"[SEED] Created {created} test users (operator, engineer, admin)")


# ---------------------------------------------------------------------------
# Telemetry ingestion from HuggingFace
# ---------------------------------------------------------------------------

def ingest_telemetry_from_hf(db: Session, machines):
    print("[INGEST] Loading AI4I 2020 Predictive Maintenance Dataset from HuggingFace...")
    try:
        dataset = load_dataset(
            "MohammedSohail/predictive-maintenance-dataset", split="train"
        )
        df = dataset.to_pandas()
    except Exception as e:
        print(f"[INGEST] HuggingFace download failed: {e}. Using synthetic fallback.")
        df = generate_synthetic_data()

    print(f"[INGEST] Loaded {len(df)} rows. Ingesting 1000 telemetry readings...")

    start_time = datetime.now(timezone.utc) - timedelta(days=7)

    telemetry_records = []
    for i, row in df.head(1000).iterrows():
        machine = random.choice(machines)

        engine_rpm = float(row.get("Rotational speed [rpm]", random.uniform(1000, 2500)))
        engine_temp = (
            float(row.get("Process temperature [K]", random.uniform(300, 380))) - 273.15
        )
        vibration = float(row.get("Torque [Nm]", random.uniform(20, 100))) / 10.0
        oil_pressure = random.uniform(30, 80)
        fuel_consumption = random.uniform(5, 25)

        failure = bool(row.get("Machine failure", False))

        t = Telemetry(
            machine_id=machine.id,
            timestamp=start_time + timedelta(minutes=i * 15),
            sensor_data={
                "engine_rpm": round(engine_rpm, 2),
                "engine_temperature": round(engine_temp, 2),
                "oil_pressure": round(oil_pressure, 2),
                "vibration_level": round(vibration, 2),
                "fuel_consumption": round(fuel_consumption, 2),
            },
            is_anomaly=failure,
            failure_risk=1.0 if failure else round(random.uniform(0.0, 0.3), 3),
        )
        telemetry_records.append(t)

    db.add_all(telemetry_records)
    db.commit()
    print(f"[INGEST] {len(telemetry_records)} telemetry rows saved to database")
    return telemetry_records


def generate_synthetic_data():
    """Fallback when HuggingFace download is unavailable."""
    data = []
    for _ in range(1000):
        data.append(
            {
                "Rotational speed [rpm]": random.uniform(1200, 2800),
                "Process temperature [K]": random.uniform(300, 360),
                "Torque [Nm]": random.uniform(10, 80),
                "Machine failure": 1 if random.random() > 0.95 else 0,
            }
        )
    return pd.DataFrame(data)


# ---------------------------------------------------------------------------
# Anomaly model training
# ---------------------------------------------------------------------------

def train_anomaly_model(db: Session):
    """Fit an IsolationForest on ingested sensor data and save to disk."""
    print("[MODEL] Training IsolationForest anomaly detector...")

    rows = db.query(Telemetry).all()
    if not rows:
        print("[MODEL] No telemetry data found -- skipping model training")
        return

    # Extract features from the JSON sensor_data column
    features = []
    for r in rows:
        sd = r.sensor_data or {}
        features.append(
            [
                sd.get("engine_rpm", 0.0),
                sd.get("engine_temperature", 0.0),
                sd.get("oil_pressure", 0.0),
                sd.get("vibration_level", 0.0),
                sd.get("fuel_consumption", 0.0),
            ]
        )

    import numpy as np
    from sklearn.ensemble import IsolationForest
    import joblib

    X = np.array(features)
    model = IsolationForest(contamination=0.05, random_state=42)
    model.fit(X)

    # Ensure output directory exists
    model_dir = os.path.join(os.path.dirname(__file__), "..", "..", "models")
    os.makedirs(model_dir, exist_ok=True)
    model_path = os.path.join(model_dir, "anomaly_model.joblib")
    joblib.dump(model, model_path)
    print(f"[MODEL] IsolationForest saved to {os.path.abspath(model_path)}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    init_db()
    db = SessionLocal()

    try:
        # Check if DB is already seeded
        existing_machine = db.query(Machine).first()
        if not existing_machine:
            machines = seed_machines(db, num_machines=5)
            ingest_telemetry_from_hf(db, machines)
        else:
            print("[SEED] Machines already seeded -- skipping telemetry ingestion")
            machines = db.query(Machine).all()

        # Always ensure users exist
        seed_users(db)

        # Train anomaly model
        train_anomaly_model(db)

        print("[DONE] Data ingestion complete")

    finally:
        db.close()
