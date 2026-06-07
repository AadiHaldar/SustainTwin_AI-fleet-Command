import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app.core.database import engine, Base
from app.models.machine import Machine, Telemetry

print("Dropping existing tables in Supabase to apply new schema...")
Base.metadata.drop_all(bind=engine)
print("Tables dropped successfully!")
