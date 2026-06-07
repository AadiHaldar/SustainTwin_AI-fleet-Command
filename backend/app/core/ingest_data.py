import sys
import os
import random
from datetime import datetime, timedelta
import pandas as pd
from datasets import load_dataset
from sqlalchemy.orm import Session

# Add the parent directory to sys.path to import app modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app.core.database import SessionLocal, engine, Base
from app.models.machine import Machine, Telemetry

def init_db():
    Base.metadata.create_all(bind=engine)

def seed_machines(db: Session, num_machines=10):
    machine_types = ["Excavator", "Haul Truck", "Bulldozer", "Loader"]
    machines = []
    for i in range(num_machines):
        m = Machine(
            id=f"M-{100+i}",
            type=random.choice(machine_types),
            model="Sustain-Series-X",
            location_lat=37.7749 + random.uniform(-0.1, 0.1),
            location_lon=-122.4194 + random.uniform(-0.1, 0.1),
            operating_hours=random.uniform(1000, 5000),
            status="Active"
        )
        machines.append(m)
        db.add(m)
    db.commit()
    return machines

def ingest_telemetry_from_hf(db: Session, machines):
    print("Loading AI4I 2020 Predictive Maintenance Dataset from HuggingFace...")
    # The MohammedSohail/predictive-maintenance-dataset is tabular and has realistic fields
    try:
        dataset = load_dataset("MohammedSohail/predictive-maintenance-dataset", split="train")
        df = dataset.to_pandas()
    except Exception as e:
        print(f"Error loading dataset: {e}. Falling back to synthetic generation.")
        df = generate_synthetic_data()
    
    # We will sample rows and map them to our machines to simulate time-series telemetry
    print(f"Loaded {len(df)} rows. Simulating telemetry streams...")
    
    start_time = datetime.utcnow() - timedelta(days=7)
    
    telemetry_records = []
    # Map the dataset columns to our fields
    # Expected columns in Sohail dataset or synthetic:
    # Air temperature [K], Process temperature [K], Rotational speed [rpm], Torque [Nm], Tool wear [min], Machine failure, TWF, HDF, PWF, OSF, RNF
    
    for i, row in df.head(1000).iterrows(): # Ingest 1000 rows for mock
        machine = random.choice(machines)
        
        # Map fields (handle both HF schema and synthetic fallback schema)
        engine_rpm = float(row.get('Rotational speed [rpm]', random.uniform(1000, 2500)))
        engine_temp = float(row.get('Process temperature [K]', random.uniform(300, 380))) - 273.15 # convert to C
        
        vibration = float(row.get('Torque [Nm]', random.uniform(20, 100))) / 10.0 # Mock vibration from torque
        oil_pressure = random.uniform(30, 80) # Mocked if missing
        fuel_consumption = random.uniform(5, 25) # Mocked
        
        failure = bool(row.get('Machine failure', False))
        
        t = Telemetry(
            machine_id=machine.id,
            timestamp=start_time + timedelta(minutes=i*15),
            engine_rpm=engine_rpm,
            engine_temperature=engine_temp,
            oil_pressure=oil_pressure,
            vibration_level=vibration,
            fuel_consumption=fuel_consumption,
            is_anomaly=failure,
            failure_risk=1.0 if failure else random.uniform(0.0, 0.3)
        )
        telemetry_records.append(t)
    
    db.add_all(telemetry_records)
    db.commit()
    print("Telemetry successfully ingested!")

def generate_synthetic_data():
    """Fallback if HF download fails"""
    data = []
    for _ in range(1000):
        data.append({
            'Rotational speed [rpm]': random.uniform(1200, 2800),
            'Process temperature [K]': random.uniform(300, 360),
            'Torque [Nm]': random.uniform(10, 80),
            'Machine failure': 1 if random.random() > 0.95 else 0
        })
    return pd.DataFrame(data)

if __name__ == "__main__":
    init_db()
    db = SessionLocal()
    
    # Check if DB is already seeded
    existing = db.query(Machine).first()
    if not existing:
        machines = seed_machines(db, num_machines=5)
        ingest_telemetry_from_hf(db, machines)
    else:
        print("Database already seeded.")
    
    db.close()
