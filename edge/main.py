"""SustainTwin AI -- Smart Edge Node

Simulates an IoT edge device (e.g. NVIDIA Jetson) attached to heavy machinery.
Runs a local IsolationForest model to filter normal readings and only syncs
anomalies to the cloud backend, dramatically reducing bandwidth.
"""

import argparse
import os
import sys
import time
import random
import json
import logging
from datetime import datetime, timezone

import numpy as np
import requests
from sklearn.ensemble import IsolationForest

logging.basicConfig(level=logging.INFO, format="%(asctime)s [EDGE] %(message)s")
logger = logging.getLogger(__name__)

API_URL = os.environ.get("BACKEND_URL", "http://localhost:8000/api/v1/telemetry/sync")
AUTH_TOKEN = os.environ.get("EDGE_AUTH_TOKEN", "")

# Sensor simulation ranges (realistic heavy machinery)
SENSOR_RANGES = {
    "engine_rpm": (1200, 2800),
    "engine_temperature": (75, 115),
    "vibration_level": (5, 55),
    "oil_pressure": (25, 85),
    "fuel_consumption": (5, 28),
}


def generate_training_data(n_samples: int = 500) -> np.ndarray:
    """Generate synthetic 'normal' sensor data to train the local model."""
    data = []
    for _ in range(n_samples):
        row = [
            random.gauss(1800, 200),   # engine_rpm
            random.gauss(88, 6),       # engine_temperature
            random.gauss(18, 5),       # vibration_level
            random.gauss(55, 10),      # oil_pressure
            random.gauss(14, 3),       # fuel_consumption
        ]
        data.append(row)
    return np.array(data)


def generate_sensor_reading() -> dict:
    """Simulate reading from physical CAN bus sensors."""
    reading = {}
    for sensor, (low, high) in SENSOR_RANGES.items():
        reading[sensor] = round(random.uniform(low, high), 2)

    # 8% chance of injecting a genuine anomaly spike
    if random.random() < 0.08:
        spike_sensor = random.choice(list(SENSOR_RANGES.keys()))
        _, high = SENSOR_RANGES[spike_sensor]
        reading[spike_sensor] = round(high * random.uniform(1.3, 1.8), 2)

    return reading


def run_edge_node(machine_id: str, interval: float = 5.0):
    """Main edge node loop with local ML inference."""

    # --- Phase 1: Train local IsolationForest on startup ---
    logger.info("Fitting local IsolationForest on %d synthetic readings...", 500)
    training_data = generate_training_data(500)
    feature_names = list(SENSOR_RANGES.keys())

    model = IsolationForest(
        contamination=0.05,
        n_estimators=100,
        random_state=42,
    )
    model.fit(training_data)
    logger.info("Local anomaly model ready. Starting telemetry loop for %s", machine_id)

    # --- Phase 2: Continuous monitoring loop ---
    total_readings = 0
    anomalies_synced = 0
    cycle_readings = 0
    cycle_anomalies = 0
    cycle_start = time.time()

    headers = {}
    if AUTH_TOKEN:
        headers["Authorization"] = f"Bearer {AUTH_TOKEN}"

    while True:
        try:
            reading = generate_sensor_reading()
            total_readings += 1
            cycle_readings += 1

            # Local ML inference
            feature_vector = np.array([[reading[f] for f in feature_names]])
            anomaly_score = model.decision_function(feature_vector)[0]
            is_anomaly = anomaly_score < -0.1

            if is_anomaly:
                anomalies_synced += 1
                cycle_anomalies += 1

                payload = {
                    "machine_id": machine_id,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "sensor_data": reading,
                    "is_anomaly": True,
                }

                logger.info(
                    "ANOMALY DETECTED (score=%.3f) | RPM=%.0f Temp=%.1f Vib=%.1f | Syncing to cloud...",
                    anomaly_score,
                    reading["engine_rpm"],
                    reading["engine_temperature"],
                    reading["vibration_level"],
                )

                try:
                    resp = requests.post(API_URL, json=payload, headers=headers, timeout=5)
                    if resp.status_code == 200:
                        result = resp.json()
                        if result.get("agent_analysis"):
                            diag = result["agent_analysis"].get("diagnosis", {})
                            if diag:
                                logger.info(
                                    "Agent diagnosis: %s (confidence: %.0f%%)",
                                    diag.get("root_cause", "N/A"),
                                    diag.get("confidence", 0) * 100,
                                )
                    else:
                        logger.warning("Sync failed: HTTP %d", resp.status_code)
                except requests.exceptions.RequestException as exc:
                    logger.warning("OFFLINE -- cannot reach backend: %s", exc)

            # Log compression ratio every 20 readings
            if cycle_readings >= 20:
                elapsed = time.time() - cycle_start
                filtered_pct = ((cycle_readings - cycle_anomalies) / cycle_readings) * 100
                logger.info(
                    "Compression: Filtered %.0f%% of readings -- %d anomalies synced out of %d in %.0fs",
                    filtered_pct,
                    cycle_anomalies,
                    cycle_readings,
                    elapsed,
                )
                cycle_readings = 0
                cycle_anomalies = 0
                cycle_start = time.time()

        except KeyboardInterrupt:
            logger.info("Edge node shutting down. Total: %d readings, %d anomalies synced.", total_readings, anomalies_synced)
            break
        except Exception as exc:
            logger.error("Unexpected error: %s", exc)

        time.sleep(interval)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SustainTwin Edge Node")
    parser.add_argument("--machine-id", default="M-999", help="Machine ID for this edge node")
    parser.add_argument("--interval", type=float, default=5.0, help="Seconds between readings")
    args = parser.parse_args()

    run_edge_node(machine_id=args.machine_id, interval=args.interval)
