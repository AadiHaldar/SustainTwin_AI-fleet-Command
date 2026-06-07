import time
import random
import requests
import json
from datetime import datetime

# Simulated Edge Node for Heavy Machinery
# In a real environment, this would run on an NVIDIA Jetson or Raspberry Pi, 
# interface with physical CAN bus sensors, and send MQTT payloads.

API_URL = "http://localhost:8000/api/v1/telemetry/sync"
MACHINE_ID = "M-999" # Test Edge Machine

def get_sensor_readings():
    # Simulate reading from physical sensors
    return {
        "machine_id": MACHINE_ID,
        "timestamp": datetime.utcnow().isoformat(),
        "engine_rpm": random.uniform(1500, 2600),
        "engine_temperature": random.uniform(80, 110),
        "vibration_level": random.uniform(10, 50),
        "fuel_consumption": random.uniform(8, 20),
    }

def run_edge_node():
    print(f"Starting Edge Node for Machine: {MACHINE_ID}")
    print(f"Syncing data to Cloud Backend: {API_URL}")
    
    while True:
        try:
            payload = get_sensor_readings()
            
            # Simulated local Edge AI Inference
            # If vibration is very high, flag anomaly locally before sending to cloud
            if payload["vibration_level"] > 40:
                print("[EDGE AI] Local anomaly detected! High vibration.")
                payload["is_anomaly"] = True
            else:
                payload["is_anomaly"] = False
                
            response = requests.post(API_URL, json=payload, timeout=5)
            
            if response.status_code == 200:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Sync successful. Payload: {payload['engine_rpm']:.1f} RPM")
            else:
                print(f"Sync failed with status code: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"[OFFLINE] Cannot reach cloud backend. Storing payload locally... ({e})")
            # In a real scenario, we'd queue this to a local SQLite/Redis buffer
            
        time.sleep(5) # Send telemetry every 5 seconds

if __name__ == "__main__":
    run_edge_node()
