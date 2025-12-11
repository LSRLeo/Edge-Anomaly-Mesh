
#To run this script: python3 scripts/generate_init_data.py --duration 30


#Download/generate starter simulation data for anomaly-mesh

import json
import os
from pathlib import Path
from datetime import datetime, timedelta
import numpy as np


def generate_starter_data():
    """Generate small sample datasets for each motion type"""
    
    data_dir = Path('data/generated_data')
    data_dir.mkdir(parents=True, exist_ok=True)
    
    print("=" * 60)
    print("anomaly-mesh: Generating Starter Data")
    print("=" * 60)
    print("\nThis generates sample data for testing without running\n"
          "the full simulator. Use for debugging and integration tests.\n")
    
    # Generate small samples (10 seconds each at 50Hz = 500 samples)
    motions = {
        'idle': generate_idle_data(),
        'terrestrial': generate_terrestrial_data(),
        'maritime': generate_maritime_data(),
        'lift': generate_lift_data(),
        'idle_with_anomaly': generate_idle_with_anomaly_data(),
    }
    
    for motion_type, data in motions.items():
        motion_dir = data_dir / motion_type
        motion_dir.mkdir(parents=True, exist_ok=True)
        
        # Save as JSON
        json_file = motion_dir / f'{motion_type}_starter.json'
        save_json(data, json_file, motion_type.replace('_with_anomaly', ''))
        
        # Save as CSV
        csv_file = motion_dir / f'{motion_type}_starter.csv'
        save_csv(data, csv_file, motion_type.replace('_with_anomaly', ''))
        
        print(f"✓ {motion_type:20s} -> {json_file.parent.name}/")
    
    print("\n" + "=" * 60)
    print("✓ Starter data generated successfully!")
    print("=" * 60)
    print("\nFiles created:")
    print(f"  Location: {data_dir}")
    print(f"  Each motion type has:")
    print(f"    - *_starter.json  (REDIS format)")
    print(f"    - *_starter.csv   (Table format)")
    print("\nUse for:")
    print("  - Testing Team 2 inference pipeline")
    print("  - Testing Team 3 database storage")
    print("  - Testing Team 4 UI visualization")
    print("  - Unit/integration testing")


def generate_idle_data():
    """Generate IDLE motion data"""
    g = 9.81
    data = []
    for i in range(500):  # 10 seconds at 50Hz
        t = i * 0.02
        reading = {
            'timestamp': t,
            'accel_x': np.random.normal(0.0, 0.05),
            'accel_y': np.random.normal(0.0, 0.05),
            'accel_z': g + np.random.normal(0.0, 0.05),
            'gyro_x': np.random.normal(0.0, 0.01),
            'gyro_y': np.random.normal(0.0, 0.01),
            'gyro_z': np.random.normal(0.0, 0.01),
        }
        data.append(reading)
    return data


def generate_terrestrial_data():
    """Generate TERRESTRIAL motion data"""
    g = 9.81
    frequency = 3.0
    data = []
    for i in range(500):
        t = i * 0.02
        reading = {
            'timestamp': t,
            'accel_x': 0.35 * np.sin(2 * np.pi * frequency * t) + np.random.normal(0, 0.08),
            'accel_y': 0.25 * np.sin(2 * np.pi * frequency * t + np.pi/4) + np.random.normal(0, 0.08),
            'accel_z': g + 0.12 * np.sin(2 * np.pi * frequency * t) + np.random.normal(0, 0.08),
            'gyro_x': 0.2 * np.sin(2 * np.pi * frequency * t) + np.random.normal(0, 0.05),
            'gyro_y': 0.15 * np.sin(2 * np.pi * frequency * t) + np.random.normal(0, 0.05),
            'gyro_z': 0.05 * np.sin(2 * np.pi * frequency * t) + np.random.normal(0, 0.05),
        }
        data.append(reading)
    return data


def generate_maritime_data():
    """Generate MARITIME motion data"""
    g = 9.81
    frequencies = [0.7, 1.3, 2.1, 3.2]
    data = []
    for i in range(500):
        t = i * 0.02
        accel_x = 0.0
        accel_y = 0.0
        accel_z = g
        
        for freq in frequencies:
            phase = np.random.rand() * 2 * np.pi
            amplitude = 0.3
            accel_x += amplitude * np.sin(2 * np.pi * freq * t + phase)
            accel_y += amplitude * np.sin(2 * np.pi * freq * t + phase + np.pi/3)
            accel_z += amplitude * np.sin(2 * np.pi * freq * t + phase + 2*np.pi/3)
        
        if np.random.rand() < 0.05:
            spike = np.random.uniform(0.5, 1.5)
            accel_x += spike * np.random.uniform(-1, 1)
            accel_y += spike * np.random.uniform(-1, 1)
            accel_z += spike * np.random.uniform(-0.5, 0.5)
        
        reading = {
            'timestamp': t,
            'accel_x': accel_x + np.random.normal(0, 0.15),
            'accel_y': accel_y + np.random.normal(0, 0.15),
            'accel_z': accel_z + np.random.normal(0, 0.15),
            'gyro_x': (accel_x / g) * 0.8 + np.random.normal(0, 0.1),
            'gyro_y': (accel_y / g) * 0.8 + np.random.normal(0, 0.1),
            'gyro_z': (accel_z / g) * 0.8 + np.random.normal(0, 0.1),
        }
        data.append(reading)
    return data


def generate_lift_data():
    """Generate LIFT motion data"""
    g = 9.81
    cycle_duration = 8.0
    data = []
    for i in range(500):
        t = i * 0.02
        cycle_pos = (t % cycle_duration) / cycle_duration
        
        if cycle_pos < 0.15:
            progress = cycle_pos / 0.15
            accel_z = g + progress * 3.5
            accel_x = 0.15
            accel_y = 0.1
        elif cycle_pos < 0.5:
            accel_z = g
            accel_x = 0.2 * np.sin(2 * np.pi * (cycle_pos - 0.15) / 0.35)
            accel_y = 0.15 * np.sin(2 * np.pi * (cycle_pos - 0.15) / 0.35 + np.pi/4)
        elif cycle_pos < 0.65:
            progress = (cycle_pos - 0.5) / 0.15
            accel_z = g - progress * 3.5
            accel_x = 0.15
            accel_y = 0.1
        else:
            accel_z = g
            accel_x = np.random.normal(0, 0.05)
            accel_y = np.random.normal(0, 0.05)
        
        reading = {
            'timestamp': t,
            'accel_x': accel_x + np.random.normal(0, 0.1),
            'accel_y': accel_y + np.random.normal(0, 0.1),
            'accel_z': accel_z + np.random.normal(0, 0.1),
            'gyro_x': 0.1 * np.cos(2 * np.pi * cycle_pos),
            'gyro_y': 0.1 * np.sin(2 * np.pi * cycle_pos + np.pi/4),
            'gyro_z': 0.3 * np.sin(2 * np.pi * cycle_pos),
        }
        data.append(reading)
    return data


def generate_idle_with_anomaly_data():
    """Generate IDLE data with injected anomalies"""
    data = generate_idle_data()
    
    # Inject 2 shocks
    for _ in range(2):
        idx = np.random.randint(0, len(data))
        magnitude = np.random.uniform(1.0, 2.0)
        data[idx]['accel_x'] += magnitude * np.random.uniform(-1, 1)
        data[idx]['accel_y'] += magnitude * np.random.uniform(-1, 1)
        data[idx]['accel_z'] += magnitude * np.random.uniform(-1, 1)
    
    return data


def save_json(data, filepath, motion_type):
    """Save as JSON (REDIS format)"""
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)
    
    messages = []
    base_time = datetime.now()
    
    for i, reading in enumerate(data):
        timestamp = base_time + timedelta(seconds=reading['timestamp'])
        msg = {
            'node_id': 'node_1',
            'timestamp': timestamp.isoformat(),
            'accel_x': round(reading['accel_x'], 3),
            'accel_y': round(reading['accel_y'], 3),
            'accel_z': round(reading['accel_z'], 3),
            'gyro_x': round(reading['gyro_x'], 3),
            'gyro_y': round(reading['gyro_y'], 3),
            'gyro_z': round(reading['gyro_z'], 3),
            'motion_type': motion_type
        }
        messages.append(msg)
    
    with open(filepath, 'w') as f:
        json.dump(messages, f, indent=2)


def save_csv(data, filepath, motion_type):
    """Save as CSV"""
    import csv
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)
    
    with open(filepath, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['timestamp', 'accel_x', 'accel_y', 'accel_z',
                        'gyro_x', 'gyro_y', 'gyro_z', 'motion_type'])
        
        for reading in data:
            writer.writerow([
                reading['timestamp'],
                round(reading['accel_x'], 3),
                round(reading['accel_y'], 3),
                round(reading['accel_z'], 3),
                round(reading['gyro_x'], 3),
                round(reading['gyro_y'], 3),
                round(reading['gyro_z'], 3),
                motion_type
            ])


if __name__ == '__main__':
    generate_starter_data()