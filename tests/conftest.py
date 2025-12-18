"""
Pytest fixtures shared across all test modules.
"""

import pytest
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture
def sample_sensor_reading():
    """Sample sensor reading for testing."""
    return {
        "node_id": "node_001",
        "timestamp": "2024-01-15T10:30:00",
        "accel_x": 0.05,
        "accel_y": -0.02,
        "accel_z": 9.81,
        "gyro_x": 0.01,
        "gyro_y": 0.01,
        "gyro_z": 0.00,
    }


@pytest.fixture
def sample_inference_result():
    """Sample inference result for testing."""
    return {
        "node_id": "node_001",
        "timestamp": 1702656000.123456,
        "window_start": 1702655998.123456,
        "window_end": 1702656000.123456,
        "motion_class": "IDLE",
        "motion_confidence": 0.95,
        "anomaly_flag": False,
        "anomaly_score": 0.12,
        "feature_vector": [0.05, 0.02, 9.81],
        "processing_time_ms": 45,
    }


@pytest.fixture
def sample_window_data():
    """Sample window of sensor data (100 samples = 2 seconds at 50Hz)."""
    import numpy as np
    
    g = 9.81
    samples = []
    for i in range(100):
        samples.append({
            "timestamp": i * 0.02,
            "accel_x": np.random.normal(0.0, 0.05),
            "accel_y": np.random.normal(0.0, 0.05),
            "accel_z": g + np.random.normal(0.0, 0.05),
            "gyro_x": np.random.normal(0.0, 0.01),
            "gyro_y": np.random.normal(0.0, 0.01),
            "gyro_z": np.random.normal(0.0, 0.01),
        })
    return samples
