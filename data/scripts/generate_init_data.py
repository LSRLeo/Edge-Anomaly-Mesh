#!/usr/bin/env python3
"""
Edge-Anomaly-Mesh: Data Generation Script

Generates all data formats for the pipeline:
1. Hub Registry (config) - Static hub locations
2. Raw Sensor Data - What sensors produce → ML team consumes
3. ML Inference Results - What ML team produces → Database consumes
4. Node Control Messages - Manual override commands

Usage:
    python generate_init_data.py --duration 30
    python generate_init_data.py --duration 60 --nodes 5
    python generate_init_data.py --help
"""

import json
import csv
import argparse
import math
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import List, Optional
import numpy as np


# =============================================================================
# CONFIGURATION & CONSTANTS
# =============================================================================

GRAVITY = 9.81  # m/s²

# Sample rates by mode
SAMPLE_RATES = {
    "TRANSIT": 50,   # Hz - high resolution for motion classification
    "HOME": 10,      # Hz - less movement, save battery
    "SLEEP": 0.1     # Hz - just heartbeat
}

MOTION_CLASSES = ["IDLE", "TERRESTRIAL", "MARITIME", "LIFT", "UNKNOWN"]
LOCATION_STATES = ["HOME", "TRANSIT"]
ANOMALY_TYPES = ["IMPACT", "DRIFT", "ORIENTATION", "VIBRATION", None]


# =============================================================================
# HUB REGISTRY
# =============================================================================

def generate_hub_registry() -> dict:
    """Generate static hub configuration file"""
    return {
        "version": "1.0",
        "generated_at": datetime.now().isoformat(),
        "hubs": [
            {
                "hub_id": "hub_nyc_01",
                "name": "NYC Distribution Center",
                "lat": 40.7128,
                "lon": -74.0060,
                "altitude_m": 10.0,
                "radius_m": 500,
                "type": "distribution_center"
            },
            {
                "hub_id": "hub_la_01",
                "name": "LA Warehouse",
                "lat": 34.0522,
                "lon": -118.2437,
                "altitude_m": 85.0,
                "radius_m": 750,
                "type": "warehouse"
            },
            {
                "hub_id": "hub_chicago_01",
                "name": "Chicago Logistics Hub",
                "lat": 41.8781,
                "lon": -87.6298,
                "altitude_m": 180.0,
                "radius_m": 600,
                "type": "logistics_hub"
            },
            {
                "hub_id": "hub_miami_port_01",
                "name": "Miami Port Facility",
                "lat": 25.7617,
                "lon": -80.1918,
                "altitude_m": 2.0,
                "radius_m": 1000,
                "type": "port"
            }
        ]
    }


# =============================================================================
# RAW SENSOR DATA GENERATION
# =============================================================================

def generate_raw_sensor_message(
    node_id: str,
    timestamp: datetime,
    seq: int,
    gps: dict,
    accel: dict,
    gyro: dict,
    mode: str,
    battery_pct: int = 100
) -> dict:
    """Generate a single raw sensor data message"""
    return {
        "node_id": node_id,
        "timestamp": timestamp.isoformat(),
        "seq": seq,
        "gps": {
            "lat": round(gps["lat"], 6),
            "lon": round(gps["lon"], 6),
            "altitude_m": round(gps["altitude_m"], 1)
        },
        "accel": {
            "x": round(accel["x"], 4),
            "y": round(accel["y"], 4),
            "z": round(accel["z"], 4)
        },
        "gyro": {
            "x": round(gyro["x"], 4),
            "y": round(gyro["y"], 4),
            "z": round(gyro["z"], 4)
        },
        "meta": {
            "sample_rate_hz": SAMPLE_RATES[mode],
            "battery_pct": battery_pct,
            "mode": mode
        }
    }


def generate_idle_sensor_data(
    node_id: str,
    duration_sec: int,
    start_time: datetime,
    gps_base: dict,
    mode: str = "HOME"
) -> List[dict]:
    """Generate IDLE motion sensor data"""
    sample_rate = SAMPLE_RATES[mode]
    num_samples = int(duration_sec * sample_rate)
    messages = []
    
    for i in range(num_samples):
        t = i / sample_rate
        timestamp = start_time + timedelta(seconds=t)
        
        # Idle: minimal movement, just sensor noise
        accel = {
            "x": np.random.normal(0.0, 0.05),
            "y": np.random.normal(0.0, 0.05),
            "z": GRAVITY + np.random.normal(0.0, 0.05)
        }
        gyro = {
            "x": np.random.normal(0.0, 0.01),
            "y": np.random.normal(0.0, 0.01),
            "z": np.random.normal(0.0, 0.01)
        }
        # GPS stays fixed with tiny drift
        gps = {
            "lat": gps_base["lat"] + np.random.normal(0, 0.00001),
            "lon": gps_base["lon"] + np.random.normal(0, 0.00001),
            "altitude_m": gps_base["altitude_m"] + np.random.normal(0, 0.5)
        }
        
        msg = generate_raw_sensor_message(
            node_id, timestamp, i, gps, accel, gyro, mode
        )
        messages.append(msg)
    
    return messages


def generate_terrestrial_sensor_data(
    node_id: str,
    duration_sec: int,
    start_time: datetime,
    gps_start: dict,
    gps_end: dict
) -> List[dict]:
    """Generate TERRESTRIAL motion sensor data (truck/train)"""
    sample_rate = SAMPLE_RATES["TRANSIT"]
    num_samples = int(duration_sec * sample_rate)
    messages = []
    
    vibration_freq = 3.0  # Hz - road vibration frequency
    
    for i in range(num_samples):
        t = i / sample_rate
        progress = t / duration_sec  # 0 to 1
        timestamp = start_time + timedelta(seconds=t)
        
        # Terrestrial: road vibration pattern
        accel = {
            "x": 0.35 * np.sin(2 * np.pi * vibration_freq * t) + np.random.normal(0, 0.08),
            "y": 0.25 * np.sin(2 * np.pi * vibration_freq * t + np.pi/4) + np.random.normal(0, 0.08),
            "z": GRAVITY + 0.12 * np.sin(2 * np.pi * vibration_freq * t) + np.random.normal(0, 0.08)
        }
        gyro = {
            "x": 0.2 * np.sin(2 * np.pi * vibration_freq * t) + np.random.normal(0, 0.05),
            "y": 0.15 * np.sin(2 * np.pi * vibration_freq * t) + np.random.normal(0, 0.05),
            "z": 0.05 * np.sin(2 * np.pi * vibration_freq * t) + np.random.normal(0, 0.05)
        }
        # GPS interpolates from start to end
        gps = {
            "lat": gps_start["lat"] + (gps_end["lat"] - gps_start["lat"]) * progress,
            "lon": gps_start["lon"] + (gps_end["lon"] - gps_start["lon"]) * progress,
            "altitude_m": gps_start["altitude_m"] + (gps_end["altitude_m"] - gps_start["altitude_m"]) * progress
        }
        
        msg = generate_raw_sensor_message(
            node_id, timestamp, i, gps, accel, gyro, "TRANSIT"
        )
        messages.append(msg)
    
    return messages


def generate_maritime_sensor_data(
    node_id: str,
    duration_sec: int,
    start_time: datetime,
    gps_start: dict,
    gps_end: dict
) -> List[dict]:
    """Generate MARITIME motion sensor data (ship)"""
    sample_rate = SAMPLE_RATES["TRANSIT"]
    num_samples = int(duration_sec * sample_rate)
    messages = []
    
    # Multiple wave frequencies for realistic ocean motion
    wave_frequencies = [0.7, 1.3, 2.1, 3.2]
    
    for i in range(num_samples):
        t = i / sample_rate
        progress = t / duration_sec
        timestamp = start_time + timedelta(seconds=t)
        
        # Maritime: chaotic multi-frequency motion
        accel_x, accel_y, accel_z = 0.0, 0.0, GRAVITY
        
        for freq in wave_frequencies:
            phase = np.random.rand() * 2 * np.pi
            amplitude = 0.3
            accel_x += amplitude * np.sin(2 * np.pi * freq * t + phase)
            accel_y += amplitude * np.sin(2 * np.pi * freq * t + phase + np.pi/3)
            accel_z += amplitude * np.sin(2 * np.pi * freq * t + phase + 2*np.pi/3)
        
        # Random wave impacts (5% chance)
        if np.random.rand() < 0.05:
            spike = np.random.uniform(0.5, 1.5)
            accel_x += spike * np.random.uniform(-1, 1)
            accel_y += spike * np.random.uniform(-1, 1)
            accel_z += spike * np.random.uniform(-0.5, 0.5)
        
        accel = {
            "x": accel_x + np.random.normal(0, 0.15),
            "y": accel_y + np.random.normal(0, 0.15),
            "z": accel_z + np.random.normal(0, 0.15)
        }
        gyro = {
            "x": (accel_x / GRAVITY) * 0.8 + np.random.normal(0, 0.1),
            "y": (accel_y / GRAVITY) * 0.8 + np.random.normal(0, 0.1),
            "z": np.random.normal(0, 0.1)
        }
        gps = {
            "lat": gps_start["lat"] + (gps_end["lat"] - gps_start["lat"]) * progress,
            "lon": gps_start["lon"] + (gps_end["lon"] - gps_start["lon"]) * progress,
            "altitude_m": 2.0 + np.random.normal(0, 0.5)  # Sea level
        }
        
        msg = generate_raw_sensor_message(
            node_id, timestamp, i, gps, accel, gyro, "TRANSIT"
        )
        messages.append(msg)
    
    return messages


def generate_lift_sensor_data(
    node_id: str,
    duration_sec: int,
    start_time: datetime,
    gps_base: dict,
    mode: str = "TRANSIT"
) -> List[dict]:
    """Generate LIFT motion sensor data (forklift operation)"""
    sample_rate = SAMPLE_RATES[mode]
    num_samples = int(duration_sec * sample_rate)
    messages = []
    
    cycle_duration = 8.0  # seconds per lift cycle
    
    for i in range(num_samples):
        t = i / sample_rate
        timestamp = start_time + timedelta(seconds=t)
        cycle_pos = (t % cycle_duration) / cycle_duration
        
        # Lift cycle phases
        if cycle_pos < 0.15:  # Rising
            progress = cycle_pos / 0.15
            accel_z = GRAVITY + progress * 3.5
            accel_x = 0.15
            accel_y = 0.1
        elif cycle_pos < 0.5:  # Holding/moving horizontally
            accel_z = GRAVITY
            accel_x = 0.2 * np.sin(2 * np.pi * (cycle_pos - 0.15) / 0.35)
            accel_y = 0.15 * np.sin(2 * np.pi * (cycle_pos - 0.15) / 0.35 + np.pi/4)
        elif cycle_pos < 0.65:  # Descending
            progress = (cycle_pos - 0.5) / 0.15
            accel_z = GRAVITY - progress * 3.5
            accel_x = 0.15
            accel_y = 0.1
        else:  # Resting
            accel_z = GRAVITY
            accel_x = np.random.normal(0, 0.05)
            accel_y = np.random.normal(0, 0.05)
        
        accel = {
            "x": accel_x + np.random.normal(0, 0.1),
            "y": accel_y + np.random.normal(0, 0.1),
            "z": accel_z + np.random.normal(0, 0.1)
        }
        gyro = {
            "x": 0.1 * np.cos(2 * np.pi * cycle_pos),
            "y": 0.1 * np.sin(2 * np.pi * cycle_pos + np.pi/4),
            "z": 0.3 * np.sin(2 * np.pi * cycle_pos)
        }
        gps = {
            "lat": gps_base["lat"] + np.random.normal(0, 0.00002),
            "lon": gps_base["lon"] + np.random.normal(0, 0.00002),
            "altitude_m": gps_base["altitude_m"] + np.random.normal(0, 1.0)
        }
        
        msg = generate_raw_sensor_message(
            node_id, timestamp, i, gps, accel, gyro, mode
        )
        messages.append(msg)
    
    return messages


def inject_anomalies(messages: List[dict], anomaly_count: int = 3) -> List[dict]:
    """Inject anomalies into sensor data"""
    if len(messages) < anomaly_count:
        return messages
    
    indices = np.random.choice(len(messages), anomaly_count, replace=False)
    
    for idx in indices:
        anomaly_type = np.random.choice(["IMPACT", "DRIFT", "VIBRATION"])
        
        if anomaly_type == "IMPACT":
            # Sudden shock
            magnitude = np.random.uniform(2.0, 5.0)
            messages[idx]["accel"]["x"] += magnitude * np.random.uniform(-1, 1)
            messages[idx]["accel"]["y"] += magnitude * np.random.uniform(-1, 1)
            messages[idx]["accel"]["z"] += magnitude * np.random.uniform(-1, 1)
        
        elif anomaly_type == "DRIFT":
            # Sensor calibration issue - gravity reading off
            messages[idx]["accel"]["z"] = np.random.uniform(7.0, 8.5)
        
        elif anomaly_type == "VIBRATION":
            # Unusual high-frequency component
            messages[idx]["accel"]["x"] += np.random.uniform(1.0, 2.0)
            messages[idx]["accel"]["y"] += np.random.uniform(1.0, 2.0)
    
    return messages


# =============================================================================
# ML INFERENCE RESULTS (Example output for Database team)
# =============================================================================

def generate_inference_result(
    node_id: str,
    timestamp: datetime,
    window_start: datetime,
    window_end: datetime,
    samples: int,
    location_state: str,
    motion_class: str,
    confidence: float,
    anomaly_detected: bool,
    anomaly_score: float,
    anomaly_type: Optional[str],
    nearest_hub_id: str,
    nearest_hub_distance_m: float,
    features: dict,
    processing_time_ms: int
) -> dict:
    """Generate an ML inference result message"""
    return {
        "node_id": node_id,
        "timestamp": timestamp.isoformat(),
        "window": {
            "start": window_start.isoformat(),
            "end": window_end.isoformat(),
            "samples": samples
        },
        "location_state": location_state,
        "motion_class": motion_class,
        "confidence": round(confidence, 3),
        "anomaly": {
            "detected": anomaly_detected,
            "score": round(anomaly_score, 3),
            "type": anomaly_type
        },
        "nearest_hub": {
            "hub_id": nearest_hub_id,
            "distance_m": round(nearest_hub_distance_m, 1)
        },
        "features": {
            "rms_accel": round(features.get("rms_accel", 0), 4),
            "peak_accel": round(features.get("peak_accel", 0), 4),
            "dominant_freq_hz": round(features.get("dominant_freq_hz", 0), 2),
            "variance_x": round(features.get("variance_x", 0), 4),
            "variance_y": round(features.get("variance_y", 0), 4),
            "variance_z": round(features.get("variance_z", 0), 4)
        },
        "processing_time_ms": processing_time_ms
    }


def generate_example_inference_results(duration_sec: int, start_time: datetime) -> List[dict]:
    """Generate example inference results for each motion type"""
    results = []
    window_duration = 2.0  # seconds
    num_windows = int(duration_sec / window_duration)
    
    # Example: node at hub (HOME + IDLE)
    for i in range(num_windows):
        window_start = start_time + timedelta(seconds=i * window_duration)
        window_end = window_start + timedelta(seconds=window_duration)
        
        result = generate_inference_result(
            node_id="node_001",
            timestamp=window_end,
            window_start=window_start,
            window_end=window_end,
            samples=int(window_duration * SAMPLE_RATES["HOME"]),
            location_state="HOME",
            motion_class="IDLE",
            confidence=0.95 + np.random.uniform(-0.05, 0.05),
            anomaly_detected=False,
            anomaly_score=np.random.uniform(0.05, 0.15),
            anomaly_type=None,
            nearest_hub_id="hub_nyc_01",
            nearest_hub_distance_m=np.random.uniform(10, 50),
            features={
                "rms_accel": 0.05,
                "peak_accel": 0.12,
                "dominant_freq_hz": 0.0,
                "variance_x": 0.002,
                "variance_y": 0.002,
                "variance_z": 0.003
            },
            processing_time_ms=np.random.randint(30, 60)
        )
        results.append(result)
    
    # Example: node in transit (TRANSIT + TERRESTRIAL)
    for i in range(num_windows):
        window_start = start_time + timedelta(seconds=i * window_duration)
        window_end = window_start + timedelta(seconds=window_duration)
        
        result = generate_inference_result(
            node_id="node_002",
            timestamp=window_end,
            window_start=window_start,
            window_end=window_end,
            samples=int(window_duration * SAMPLE_RATES["TRANSIT"]),
            location_state="TRANSIT",
            motion_class="TERRESTRIAL",
            confidence=0.88 + np.random.uniform(-0.08, 0.08),
            anomaly_detected=False,
            anomaly_score=np.random.uniform(0.10, 0.25),
            anomaly_type=None,
            nearest_hub_id="hub_chicago_01",
            nearest_hub_distance_m=np.random.uniform(5000, 50000),
            features={
                "rms_accel": 0.42,
                "peak_accel": 1.15,
                "dominant_freq_hz": 3.2,
                "variance_x": 0.12,
                "variance_y": 0.08,
                "variance_z": 0.015
            },
            processing_time_ms=np.random.randint(40, 80)
        )
        results.append(result)
    
    # Example: anomaly detected
    anomaly_result = generate_inference_result(
        node_id="node_003",
        timestamp=start_time + timedelta(seconds=5),
        window_start=start_time + timedelta(seconds=3),
        window_end=start_time + timedelta(seconds=5),
        samples=100,
        location_state="TRANSIT",
        motion_class="TERRESTRIAL",
        confidence=0.72,
        anomaly_detected=True,
        anomaly_score=0.85,
        anomaly_type="IMPACT",
        nearest_hub_id="hub_la_01",
        nearest_hub_distance_m=12450.5,
        features={
            "rms_accel": 2.35,
            "peak_accel": 5.8,
            "dominant_freq_hz": 3.1,
            "variance_x": 1.85,
            "variance_y": 1.42,
            "variance_z": 0.95
        },
        processing_time_ms=52
    )
    results.append(anomaly_result)
    
    return results


# =============================================================================
# NODE CONTROL MESSAGES
# =============================================================================

def generate_control_message(
    node_id: str,
    command: str,
    payload: dict,
    issued_by: str = "system"
) -> dict:
    """Generate a node control message"""
    return {
        "node_id": node_id,
        "timestamp": datetime.now().isoformat(),
        "command": command,
        "payload": payload,
        "issued_by": issued_by
    }


def generate_example_control_messages() -> List[dict]:
    """Generate example control messages"""
    return [
        generate_control_message(
            node_id="node_001",
            command="SET_MODE",
            payload={
                "mode": "SLEEP",
                "reason": "delivered_to_destination",
                "resume_at": (datetime.now() + timedelta(hours=12)).isoformat()
            },
            issued_by="operator_jane"
        ),
        generate_control_message(
            node_id="node_002",
            command="WAKE",
            payload={
                "mode": "TRANSIT",
                "reason": "shipment_departure"
            },
            issued_by="operator_bob"
        ),
        generate_control_message(
            node_id="node_003",
            command="SET_SAMPLE_RATE",
            payload={
                "sample_rate_hz": 100,
                "reason": "debugging_anomaly",
                "duration_sec": 300
            },
            issued_by="engineer_alice"
        ),
        generate_control_message(
            node_id="node_004",
            command="SHUTDOWN",
            payload={
                "reason": "maintenance_required",
                "alert_sent": True
            },
            issued_by="system"
        ),
        generate_control_message(
            node_id="node_005",
            command="CALIBRATE",
            payload={
                "reason": "drift_detected",
                "baseline_reset": True
            },
            issued_by="ml_system"
        )
    ]


# =============================================================================
# FILE SAVING UTILITIES
# =============================================================================

def save_json(data, filepath: Path):
    """Save data as JSON"""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"  ✓ {filepath}")


def save_csv(messages: List[dict], filepath: Path, flat_format: bool = True):
    """Save sensor messages as CSV"""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    if not messages:
        return
    
    # Flatten nested structure for CSV
    if flat_format:
        flat_rows = []
        for msg in messages:
            row = {
                "node_id": msg["node_id"],
                "timestamp": msg["timestamp"],
                "seq": msg["seq"],
                "gps_lat": msg["gps"]["lat"],
                "gps_lon": msg["gps"]["lon"],
                "gps_altitude_m": msg["gps"]["altitude_m"],
                "accel_x": msg["accel"]["x"],
                "accel_y": msg["accel"]["y"],
                "accel_z": msg["accel"]["z"],
                "gyro_x": msg["gyro"]["x"],
                "gyro_y": msg["gyro"]["y"],
                "gyro_z": msg["gyro"]["z"],
                "meta_sample_rate_hz": msg["meta"]["sample_rate_hz"],
                "meta_battery_pct": msg["meta"]["battery_pct"],
                "meta_mode": msg["meta"]["mode"]
            }
            flat_rows.append(row)
        
        with open(filepath, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=flat_rows[0].keys())
            writer.writeheader()
            writer.writerows(flat_rows)
    
    print(f"  ✓ {filepath}")


# =============================================================================
# MAIN GENERATION
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Generate simulation data for edge-anomaly-mesh"
    )
    parser.add_argument(
        "--duration", type=int, default=10,
        help="Duration in seconds for each motion type (default: 10)"
    )
    parser.add_argument(
        "--nodes", type=int, default=3,
        help="Number of simulated nodes (default: 3)"
    )
    parser.add_argument(
        "--output-dir", type=str, default="data",
        help="Output directory (default: data)"
    )
    
    args = parser.parse_args()
    
    output_dir = Path(args.output_dir)
    start_time = datetime.now()
    
    print("=" * 60)
    print("Edge-Anomaly-Mesh: Data Generation")
    print("=" * 60)
    print(f"\nDuration: {args.duration}s per motion type")
    print(f"Nodes: {args.nodes}")
    print(f"Output: {output_dir}/\n")
    
    # -------------------------------------------------------------------------
    # 1. Generate Hub Registry
    # -------------------------------------------------------------------------
    print("1. Hub Registry (config)")
    hub_registry = generate_hub_registry()
    config_dir = output_dir / "config"
    save_json(hub_registry, config_dir / "hubs.json")
    
    # -------------------------------------------------------------------------
    # 2. Generate Raw Sensor Data
    # -------------------------------------------------------------------------
    print("\n2. Raw Sensor Data (for ML team)")
    sensor_dir = output_dir / "raw_sensor_data"
    
    # Get hub locations for GPS references
    hubs = hub_registry["hubs"]
    nyc_hub = next(h for h in hubs if h["hub_id"] == "hub_nyc_01")
    la_hub = next(h for h in hubs if h["hub_id"] == "hub_la_01")
    miami_hub = next(h for h in hubs if h["hub_id"] == "hub_miami_port_01")
    
    # IDLE (at hub - HOME mode)
    idle_data = generate_idle_sensor_data(
        node_id="node_001",
        duration_sec=args.duration,
        start_time=start_time,
        gps_base={"lat": nyc_hub["lat"], "lon": nyc_hub["lon"], "altitude_m": nyc_hub["altitude_m"]},
        mode="HOME"
    )
    save_json(idle_data, sensor_dir / "idle" / "idle_home.json")
    save_csv(idle_data, sensor_dir / "idle" / "idle_home.csv")
    
    # TERRESTRIAL (truck transport)
    terrestrial_data = generate_terrestrial_sensor_data(
        node_id="node_002",
        duration_sec=args.duration,
        start_time=start_time,
        gps_start={"lat": nyc_hub["lat"], "lon": nyc_hub["lon"], "altitude_m": 50},
        gps_end={"lat": 40.9, "lon": -73.8, "altitude_m": 60}
    )
    save_json(terrestrial_data, sensor_dir / "terrestrial" / "terrestrial_truck.json")
    save_csv(terrestrial_data, sensor_dir / "terrestrial" / "terrestrial_truck.csv")
    
    # MARITIME (ship transport)
    maritime_data = generate_maritime_sensor_data(
        node_id="node_003",
        duration_sec=args.duration,
        start_time=start_time,
        gps_start={"lat": miami_hub["lat"], "lon": miami_hub["lon"], "altitude_m": 2},
        gps_end={"lat": 26.0, "lon": -79.5, "altitude_m": 2}
    )
    save_json(maritime_data, sensor_dir / "maritime" / "maritime_ship.json")
    save_csv(maritime_data, sensor_dir / "maritime" / "maritime_ship.csv")
    
    # LIFT (forklift at warehouse)
    lift_data = generate_lift_sensor_data(
        node_id="node_004",
        duration_sec=args.duration,
        start_time=start_time,
        gps_base={"lat": la_hub["lat"], "lon": la_hub["lon"], "altitude_m": la_hub["altitude_m"]},
        mode="TRANSIT"
    )
    save_json(lift_data, sensor_dir / "lift" / "lift_forklift.json")
    save_csv(lift_data, sensor_dir / "lift" / "lift_forklift.csv")
    
    # ANOMALY (idle with injected anomalies)
    anomaly_data = generate_idle_sensor_data(
        node_id="node_005",
        duration_sec=args.duration,
        start_time=start_time,
        gps_base={"lat": nyc_hub["lat"], "lon": nyc_hub["lon"], "altitude_m": nyc_hub["altitude_m"]},
        mode="HOME"
    )
    anomaly_data = inject_anomalies(anomaly_data, anomaly_count=3)
    save_json(anomaly_data, sensor_dir / "anomaly" / "idle_with_anomalies.json")
    save_csv(anomaly_data, sensor_dir / "anomaly" / "idle_with_anomalies.csv")
    
    # -------------------------------------------------------------------------
    # 3. Generate Example ML Inference Results
    # -------------------------------------------------------------------------
    print("\n3. ML Inference Results (example output for DB team)")
    inference_dir = output_dir / "inference_results"
    
    inference_results = generate_example_inference_results(args.duration, start_time)
    save_json(inference_results, inference_dir / "example_inference_results.json")
    
    # -------------------------------------------------------------------------
    # 4. Generate Example Node Control Messages
    # -------------------------------------------------------------------------
    print("\n4. Node Control Messages (examples)")
    control_dir = output_dir / "control_messages"
    
    control_messages = generate_example_control_messages()
    save_json(control_messages, control_dir / "example_control_messages.json")
    
    # -------------------------------------------------------------------------
    # Summary
    # -------------------------------------------------------------------------
    print("\n" + "=" * 60)
    print("✓ Data generation complete!")
    print("=" * 60)
    print(f"""
Directory structure created:
{output_dir}/
├── config/
│   └── hubs.json                    # Hub registry (shared config)
├── raw_sensor_data/
│   ├── idle/                        # IDLE motion samples
│   ├── terrestrial/                 # TERRESTRIAL motion samples
│   ├── maritime/                    # MARITIME motion samples
│   ├── lift/                        # LIFT motion samples
│   └── anomaly/                     # Data with injected anomalies
├── inference_results/
│   └── example_inference_results.json  # ML output examples for DB team
└── control_messages/
    └── example_control_messages.json   # Node control examples

REDIS Channels:
  sensor:raw:{{node_id}}      <- Raw sensor data (JSON)
  inference:results:{{node_id}} <- ML inference results (JSON)
  node:control:{{node_id}}    <- Control commands (JSON)
""")


if __name__ == "__main__":
    main()
