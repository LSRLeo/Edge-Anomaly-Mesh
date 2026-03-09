"""
Integration test for streamer and pipeline.

Covers:
  - Simulated Redis messages
  - RedisSubscriber buffer logic
  - Data pipeline windowing
  - Inference chain functional check
"""

import sys
from pathlib import Path
import numpy as np
import pytest
import torch

ML_DIR = Path(__file__).parent.parent.parent / "ml"
sys.path.insert(0, str(ML_DIR))

from redis_insteam import RedisSubscriber  # noqa: E402
from data_pipeline import create_windows, windows_to_features  # noqa: E402
from train_classifier import MotionClassifier  # noqa: E402

class _TestableRedisSubscriber(RedisSubscriber):
    def __init__(self, window_size=3, stride=0, classifier=None, scaler=None):
        self.channel = "sensor:raw:*"
        self.window_size = window_size
        self.stride = stride
        self.classifier = classifier
        self.scaler = scaler
        self.node_states = {}
        self.seen_seqs = {}

@pytest.fixture
def subscriber():
    return _TestableRedisSubscriber()

def load_classifier(model_path):
    config = {
        'input_dim': 38,
        'hidden_dims': [64, 32],
        'dropout': 0.3,
        'num_classes': 8
    }
    classifier = MotionClassifier(
        input_dim=config['input_dim'],
        hidden_dims=tuple(config['hidden_dims']),
        dropout=config['dropout'],
        num_classes=config['num_classes'],
    )
    state_dict = torch.load(model_path, weights_only=False)
    classifier.load_state_dict(state_dict)
    classifier.eval()
    return classifier

def test_streamer_pipeline_full_chain(subscriber):
    """Simulates Redis messages flowing through RedisSubscriber into data_pipeline and checks inference chain."""
    model_path = Path(__file__).parent.parent.parent / "models" / "motion_classifier.pt"
    classifier = load_classifier(model_path)
    # Simulate incoming messages
    events = [
        {"node_id": "node_001", "seq": 1, "accel_x": 0.1, "accel_y": 0.2, "accel_z": 9.8, "gyro_x": 0.01, "gyro_y": 0.02, "gyro_z": 0.03},
        {"node_id": "node_001", "seq": 2, "accel_x": 0.2, "accel_y": 0.3, "accel_z": 9.7, "gyro_x": 0.02, "gyro_y": 0.03, "gyro_z": 0.04},
        {"node_id": "node_001", "seq": 3, "accel_x": 0.3, "accel_y": 0.4, "accel_z": 9.6, "gyro_x": 0.03, "gyro_y": 0.04, "gyro_z": 0.05},
    ]
    buffer = []
    for event in events:
        subscriber.insert_event_in_order(buffer, event)
    # Convert buffer to data dict for pipeline
    data = {k: np.array([e[k] for e in buffer]) for k in ['accel_x','accel_y','accel_z','gyro_x','gyro_y','gyro_z']}
    windows = create_windows(data, window_size=3, overlap=0.0)
    assert windows.shape == (1, 3, 6)
    features = windows_to_features(windows)
    features_tensor = torch.FloatTensor(features)
    predicted, _, probabilities = classifier.predict(features_tensor)
    assert isinstance(predicted.item(), int)
    assert probabilities.shape[1] == 8  # 8 classes

def test_streamer_pipeline_multiple_nodes(subscriber):
    """Simulate messages from multiple nodes and check buffer isolation."""
    events = [
        {"node_id": "node_001", "seq": 1, "accel_x": 0.1, "accel_y": 0.2, "accel_z": 9.8, "gyro_x": 0.01, "gyro_y": 0.02, "gyro_z": 0.03},
        {"node_id": "node_002", "seq": 1, "accel_x": 0.5, "accel_y": 0.6, "accel_z": 9.5, "gyro_x": 0.05, "gyro_y": 0.06, "gyro_z": 0.07},
        {"node_id": "node_001", "seq": 2, "accel_x": 0.2, "accel_y": 0.3, "accel_z": 9.7, "gyro_x": 0.02, "gyro_y": 0.03, "gyro_z": 0.04},
        {"node_id": "node_002", "seq": 2, "accel_x": 0.6, "accel_y": 0.7, "accel_z": 9.4, "gyro_x": 0.06, "gyro_y": 0.07, "gyro_z": 0.08},
    ]
    buffer1, buffer2 = [], []
    for event in events:
        if event["node_id"] == "node_001":
            subscriber.insert_event_in_order(buffer1, event)
        else:
            subscriber.insert_event_in_order(buffer2, event)
    assert len(buffer1) == 2
    assert len(buffer2) == 2
    assert buffer1[0]["seq"] == 1 and buffer1[1]["seq"] == 2
    assert buffer2[0]["seq"] == 1 and buffer2[1]["seq"] == 2

def test_streamer_pipeline_duplicate_seq(subscriber):
    """Test that duplicate seq numbers are not inserted."""
    buffer = []
    event = {"node_id": "node_001", "seq": 1, "accel_x": 0.1, "accel_y": 0.2, "accel_z": 9.8, "gyro_x": 0.01, "gyro_y": 0.02, "gyro_z": 0.03}
    subscriber.insert_event_in_order(buffer, event)
    subscriber.insert_event_in_order(buffer, event)
    assert len(buffer) == 1

def test_streamer_pipeline_out_of_order(subscriber):
    """Test that out-of-order seq numbers are inserted correctly."""
    buffer = []
    event1 = {"node_id": "node_001", "seq": 2, "accel_x": 0.2, "accel_y": 0.3, "accel_z": 9.7, "gyro_x": 0.02, "gyro_y": 0.03, "gyro_z": 0.04}
    event2 = {"node_id": "node_001", "seq": 1, "accel_x": 0.1, "accel_y": 0.2, "accel_z": 9.8, "gyro_x": 0.01, "gyro_y": 0.02, "gyro_z": 0.03}
    subscriber.insert_event_in_order(buffer, event1)
    subscriber.insert_event_in_order(buffer, event2)
    assert buffer[0]["seq"] == 1
    assert buffer[1]["seq"] == 2

def test_streamer_pipeline_window_overlap(subscriber):
    """Test windowing with overlap."""
    data = {
        'accel_x': np.arange(6),
        'accel_y': np.arange(6),
        'accel_z': np.arange(6),
        'gyro_x': np.arange(6),
        'gyro_y': np.arange(6),
        'gyro_z': np.arange(6),
    }
    windows = create_windows(data, window_size=3, overlap=0.5)
    assert windows.shape == (4, 3, 6)
    assert np.array_equal(windows[0][1], windows[1][0])

def test_streamer_pipeline_inference_output(subscriber):
    """Test inference output structure and values."""
    model_path = Path(__file__).parent.parent.parent / "models" / "motion_classifier.pt"
    classifier = load_classifier(model_path)
    data = {
        'accel_x': np.array([0.1, 0.2, 0.3]),
        'accel_y': np.array([0.2, 0.3, 0.4]),
        'accel_z': np.array([9.8, 9.7, 9.6]),
        'gyro_x': np.array([0.01, 0.02, 0.03]),
        'gyro_y': np.array([0.02, 0.03, 0.04]),
        'gyro_z': np.array([0.03, 0.04, 0.05]),
    }
    windows = create_windows(data, window_size=3, overlap=0.0)
    features = windows_to_features(windows)
    features_tensor = torch.FloatTensor(features)
    predicted, _, probabilities = classifier.predict(features_tensor)
    assert isinstance(predicted.item(), int)
    assert probabilities.shape[1] == 8
    assert np.isclose(probabilities.sum().item(), 1.0, atol=1e-5)