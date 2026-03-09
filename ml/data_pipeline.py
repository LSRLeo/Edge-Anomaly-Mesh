#!/usr/bin/env python3
"""
data_pipeline.py

Handles loading motion sensor data, creating sliding windows, and saving them
for later feature extraction or ML training.

WINDOWING EXPLAINED:
====================
Sensors produce continuous data at 50Hz (50 samples/second).
ML models need fixed-size inputs. Windowing solves this by:

1. Taking a "window" of consecutive samples (e.g., 100 samples = 2 seconds)
2. Extracting features from that window (mean, std, FFT, etc.)
3. Sliding the window forward and repeating

Example with 50% overlap:
    Raw data:  ════════════════════════════════════════
    Window 1:  [████████████]
    Window 2:        [████████████]
    Window 3:              [████████████]
    
    Each window becomes one feature vector → one classification

This file is responsible for:
- Argument parsing
- Data loading
- Windowing
- Saving processed data
- Demo / orchestration

Feature extraction logic lives in feature_extraction.py
"""

import argparse
import numpy as np
from pathlib import Path
import json

from feature_extraction import FeatureExtractor

# ============================================================================
# TERRAIN CONSTANTS (shared with redis_insteam.py)
# ============================================================================

TERRAIN_MAP = {
    "IDLE": 0,
    "TERRESTRIAL": 1,
    "TRANSIT": 1,  # TRANSIT is the same as TERRESTRIAL
    "MARITIME": 2,
    "LIFT": 3
}
TERRAIN_NAMES = ['IDLE', 'TERRESTRIAL', 'MARITIME', 'LIFT']

# ============================================================================
# ARGUMENT PARSING
# ============================================================================

def parse_args():
    """
    Parse command-line arguments.
    """
    parser = argparse.ArgumentParser(
        description='Data pipeline for motion sensor data',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    # Data arguments
    parser.add_argument('--data-dir', type=str, default='data/generated_data',
                        help='Directory containing sensor data files')

    parser.add_argument('--output-dir', type=str, default='data/features',
                        help='Directory to save processed data')

    # Windowing arguments
    parser.add_argument('--window-size', type=int, default=100,
                        help='Number of samples per window')

    parser.add_argument('--overlap', type=float, default=0.5,
                        help='Fraction of overlap between windows')

    parser.add_argument('--sample-rate', type=int, default=50,
                        help='Sensor sample rate in Hz')

    # Output options
    parser.add_argument('--save', action='store_true',
                        help='Save processed data')

    parser.add_argument('--verbose', action='store_true',
                        help='Print detailed progress information')

    return parser.parse_args()

# ============================================================================
# WINDOWING
# ============================================================================

def create_windows(data, window_size=100, overlap=0.0, labels=None):
    """
    Create sliding windows from continuous sensor data.
    
    This is how we convert streaming sensor data into discrete chunks
    that can be classified individually.
    
    Args:
        data: dict with keys 'accel_x', 'accel_y', 'accel_z', 
              'gyro_x', 'gyro_y', 'gyro_z'
              Each value is a 1D numpy array of sensor readings.
        
        window_size: number of samples per window
                     At 50Hz: 100 samples = 2 seconds
                              250 samples = 5 seconds
        
        overlap: fraction of overlap between consecutive windows (0.0 to 0.99)
                 0.5 = 50% overlap (recommended)
                 0.0 = no overlap (windows are adjacent)
        
        labels: optional numpy array of shape (n_samples,)
    
    Returns:
        windows: numpy array of shape (n_windows, window_size, 6)
        window_labels: numpy array of shape (n_windows,) if labels provided
        The 6 channels are: [accel_x, accel_y, accel_z, gyro_x, gyro_y, gyro_z]
    
    Example:
        If data has 500 samples, window_size=100, overlap=0.5:
        - Step size = 100 * (1 - 0.5) = 50 samples
        - Windows start at: 0, 50, 100, 150, 200, 250, 300, 350, 400
        - That's 9 windows
    
    Implementation hints:
        - Calculate step size: step = int(window_size * (1 - overlap))
        - Loop: for start in range(0, n_samples - window_size + 1, step)
        - Use np.column_stack() to combine the 6 axes
    """
    # Type check and cast
    try:
        window_size = int(window_size)
        overlap = float(overlap)
    except (ValueError, TypeError):
        raise ValueError("window_size must be int and overlap must be float.")
    
    # Validate overlap
    if overlap < 0 or overlap >= 1:
        raise ValueError("Overlap must be between 0 (inclusive) and 1 (exclusive).")
    
    # Validate window_size
    if window_size < 1:
        raise ValueError("Window size must be at least 1.")
    
    # Stack sensor axes into (n_samples, 6) array
    stacked = np.column_stack([
        data['accel_x'],
        data['accel_y'],
        data['accel_z'],
        data['gyro_x'],
        data['gyro_y'],
        data['gyro_z']
    ])
    
    n_samples = stacked.shape[0]
    step = int(window_size * (1 - overlap))

    if step < 1:
        raise ValueError("Step size must be at least 1.")
    
    windows, window_labels = [], []

    for start in range(0, n_samples - window_size + 1, step):
        # Extract window
        window = stacked[start:start + window_size, :]
        windows.append(window)
        # Assign majority label if labels provided
        if labels is not None:
            label_slice = labels[start:start + window_size]
            label_counts = {}

            for label in label_slice:
                label_counts[label] = label_counts.get(label, 0) + 1

            majority_label = max(label_counts, key=label_counts.get)
            window_labels.append(majority_label)

    windows = np.array(windows)
    if labels is not None:
        return windows, np.array(window_labels)
    
    return windows

def windows_to_features(windows, sample_rate=50):
    """
    Convert sliding windows into feature vectors.

    Args:
        windows: numpy array (n_windows, window_size, 6)
        sample_rate: sensor sample rate in Hz

    Returns:
        features: numpy array (n_windows, n_features)
    """
    extractor = FeatureExtractor(sample_rate=sample_rate)
    features = extractor.extract_batch(windows)
    return features

def stream_window_to_features(buffer, window_size, sample_rate=50):
    """
    Given a list of sensor dicts, extract a window and return features.

    Handles both nested ('accel', 'gyro') and flat ('accel_x', ...) formats.

    Args:
        buffer: list of sensor dicts (each may be nested or flat)
        window_size: number of samples per window
        sample_rate: sensor sample rate in Hz

    Returns:
        features: numpy array (1, n_features) for the window
    """
    window_events = buffer[-window_size:]
    data = json_events_to_numpy(window_events)
    # Stack into (window_size, 6)
    window = np.column_stack([
        data['accel_x'], data['accel_y'], data['accel_z'],
        data['gyro_x'], data['gyro_y'], data['gyro_z']
    ])
    window = window.reshape(1, window_size, 6)
    features = windows_to_features(window, sample_rate=sample_rate)
    return features

# ============================================================================
# DATA LOADING
# ============================================================================

def load_json_data(filepath):
    """
    Load sensor data from a JSON file (single object or list of objects).

    Handles both nested ('accel', 'gyro') and flat ('accel_x', ...) formats.

    Args:
        filepath: path to JSON sensor file

    Returns:
        data: dict of numpy arrays (accel_x, accel_y, accel_z, gyro_x, gyro_y, gyro_z)
        labels: numpy array of combined terrain+anomaly labels (0-7)
                Labels 0-3: IDLE, TERRESTRIAL, MARITIME, LIFT (no anomaly)
                Labels 4-7: IDLE, TERRESTRIAL, MARITIME, LIFT (with anomaly)
    """
    filepath = Path(filepath)
    with open(filepath, "r") as f:
        raw = json.load(f)

    # Always work with a list of events
    if type(raw) is dict:
        events = [raw]
    elif type(raw) is list:
        events = raw
    else:
        raise ValueError("Unsupported JSON format")

    def get_sequence_number(event):
        """Helper function for sorting (if happens to be out of order)."""
        return event["seq"] if "seq" in event else -1

    # Sort by 'seq' if present
    if events and "seq" in events[0]:
        events = sorted(events, key=get_sequence_number)

    data = json_events_to_numpy(events)
    labels = []

    for event in events:
        meta = event.get("meta", {})
        label_field = event.get("label", {})
        terrain_str = (meta.get("sim_mode") or meta.get("mode") or meta.get("motion_type") or
                       event.get("mode") or label_field.get("motion_type"))
        if terrain_str is None:
            terrain_idx = None
        else:
            terrain_idx = TERRAIN_MAP.get(terrain_str.upper())
            if terrain_idx is None:
                raise ValueError(f"Unknown terrain type: {terrain_str}")

        raw_anomaly = (meta.get("anomaly") or meta.get("has_anomaly") or meta.get("is_anomaly") or
                       event.get("anomaly") or label_field.get("is_anomaly"))
        has_anomaly = str(raw_anomaly).lower() == "true" if raw_anomaly is not None else False
        if terrain_idx is not None:
            combined_label = terrain_idx + (4 if has_anomaly else 0)
        else:
            combined_label = None

        labels.append(combined_label)

    labels = np.array(labels)
    return data, labels

def json_events_to_numpy(events):
    """
    Convert a list of sensor dicts to NumPy arrays for each axis.
    Handles both nested ('accel', 'gyro') and flat ('accel_x', ...) formats.
    Handles partial nested keys and non-numeric values gracefully.
    """
    def safe_get(event, nested, flat):
        val = None
        if nested and isinstance(nested, dict):
            val = nested.get(flat[-1], None)
        if val is None:
            val = event.get(flat, 0)
        # Treat "NaN" (case-insensitive) as 0
        if isinstance(val, str) and val.strip().lower() == "nan":
            return 0.0
        try:
            return float(val)
        except (TypeError, ValueError):
            return 0.0

    accel_x, accel_y, accel_z = [], [], []
    gyro_x, gyro_y, gyro_z = [], [], []
    for event in events:
        accel = event.get("accel_mss") or event.get("accel")
        gyro = event.get("gyro_rads") or event.get("gyro")
        accel_x.append(safe_get(event, accel, "accel_x"))
        accel_y.append(safe_get(event, accel, "accel_y"))
        accel_z.append(safe_get(event, accel, "accel_z"))
        gyro_x.append(safe_get(event, gyro, "gyro_x"))
        gyro_y.append(safe_get(event, gyro, "gyro_y"))
        gyro_z.append(safe_get(event, gyro, "gyro_z"))
    return {
        "accel_x": np.array(accel_x, dtype=np.float32),
        "accel_y": np.array(accel_y, dtype=np.float32),
        "accel_z": np.array(accel_z, dtype=np.float32),
        "gyro_x":  np.array(gyro_x,  dtype=np.float32),
        "gyro_y":  np.array(gyro_y,  dtype=np.float32),
        "gyro_z":  np.array(gyro_z,  dtype=np.float32),
    }

def process_file(filepath, window_size=100, overlap=0.0, sample_rate=50):
    """
    Full pipeline from raw sensor file to features.

    Args:
        filepath: path to JSON sensor file
        window_size: number of samples per window
        overlap: window overlap fraction
        sample_rate: sensor sample rate in Hz

    Returns:
        features: numpy array (n_windows, n_features)
        labels: numpy array (n_windows,)
    """
    # 1. Load raw data
    data, labels = load_json_data(filepath)

    # 2. Create windows
    windows, window_labels = create_windows(data, window_size=window_size, overlap=overlap, labels=labels)

    # 3. Extract features
    features = windows_to_features(windows, sample_rate=sample_rate)

    return features, window_labels


def save_features(features, labels, output_path):
    """
    Save extracted features to a file.
    
    Args:
        features: numpy array of shape (n_samples, n_features)
        labels: numpy array of shape (n_samples,)
        output_path: path to save the file (e.g., .npz format)
    """
    # Save the features and labels as a compressed .npz file
    np.savez(output_path, features=features, labels=labels)


# ============================================================================
# DEMO / PIPELINE
# ============================================================================

def demo(args):
    """
    Demonstrate feature extraction on generated data.
    
    Args:
        args: parsed command-line arguments
    
    This function should:
        1. Load data from each motion type
        2. Create windows from the data
        3. Extract features from windows
        4. Print shapes and statistics
        5. Show that features differ between motion types
        6. Optionally save features if --save flag is set
    
    Use this to verify your implementation works correctly.
    Running our example program:
    python -m ml.data_pipeline --data-dir data/examples/raw_sensor_data --output-dir ml --window-size 100 --overlap 0.0 --save
    """
    
    # Step 1: Load data from the files in the data directory
    data_files = list(Path(args.data_dir).rglob("*.json"))
    
    # If no data files are found, print a message and return
    if not data_files:
        print("No data files found in the specified directory.")
        return
    
    for filepath in data_files:
        print(f"Processing file: {filepath}")
        
        # Step 2: Load raw sensor data and labels from the file
        data, labels = load_json_data(filepath)
        
        # Step 3: Create sliding windows from the data
        windows, window_labels = create_windows(data, window_size=args.window_size, 
                                                 overlap=args.overlap, labels=labels)
        
        # Step 4: Extract features from the windows
        features = windows_to_features(windows, sample_rate=args.sample_rate)
        
        # Step 5: Print the shapes of the features and the labels
        print(f"Features shape: {features.shape}")
        print(f"Window labels (first 5): {window_labels[:5]}")
        if features.shape[0] > 0:
            print(f"First feature vector (first 5 values): {features[0][:5]}")
            
            # Step 6: Print feature statistics (min, max, mean)
            print("Feature statistics (min, max, mean):")
            print(f"  Min values: {features.min(axis=0)}")
            print(f"  Max values: {features.max(axis=0)}")
            print(f"  Mean values: {features.mean(axis=0)}")
        else:
            print("No features extracted from this file.")
        
        # Step 7: Check for the unique motion labels in this file
        unique_labels = np.unique(window_labels)
        print(f"Unique labels in this file: {unique_labels}")

        # Save features and labels if the --save flag is set
        if args.save:
            output_path = Path(args.output_dir) / f"{filepath.stem}_features.npz"
            save_features(features, window_labels, output_path)
        
        print("=" * 60)


def process_data(args):
    """
    Main data processing pipeline.
    """
    demo(args)


def main():
    args = parse_args()

    if args.verbose:
        print("=" * 60)
        print("Data Pipeline")
        print("=" * 60)
        print(f"  Data directory:  {args.data_dir}")
        print(f"  Output directory:{args.output_dir}")
        print(f"  Window size:     {args.window_size}")
        print(f"  Overlap:         {args.overlap * 100}%")
        print(f"  Sample rate:     {args.sample_rate} Hz")
        print(f"  Save data:       {args.save}")
        print("=" * 60)

    process_data(args)


if __name__ == '__main__':
    main()