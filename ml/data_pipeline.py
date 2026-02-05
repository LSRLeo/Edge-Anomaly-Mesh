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

from ml.feature_extraction import FeatureExtractor

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

def create_windows(data, window_size=100, overlap=0.5):
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
    
    Returns:
        numpy array of shape (n_windows, window_size, 6)
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
    pass  # TODO: Implement


# ============================================================================
# DATA LOADING
# ============================================================================

def load_json_data(filepath):
    """
    Load sensor data from a JSON file (single object or list of objects).
    Handles both accel/accel_mss and gyro/gyro_rads keys.

    Returns:
        data: dict of numpy arrays (accel_x, ..., gyro_z)
        label: motion label (sim_mode / mode) or None
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

    accel_x, accel_y, accel_z = [], [], []
    gyro_x, gyro_y, gyro_z = [], [], []
    labels = []

    for event in events:
        accel = event.get("accel_mss") or event.get("accel")
        gyro = event.get("gyro_rads") or event.get("gyro")
        if accel is None:
            raise KeyError("Missing accel data")
        if gyro is None:
            raise KeyError("Missing gyro data")

        accel_x.append(accel["x"])
        accel_y.append(accel["y"])
        accel_z.append(accel["z"])
        gyro_x.append(gyro["x"])
        gyro_y.append(gyro["y"])
        gyro_z.append(gyro["z"])

        meta = event.get("meta", {})
        if "sim_mode" in meta:
            labels.append(meta["sim_mode"])
        elif "mode" in meta:
            labels.append(meta["mode"])
        else:
            labels.append(None)

    data = {
        "accel_x": np.array(accel_x, dtype=np.float32),
        "accel_y": np.array(accel_y, dtype=np.float32),
        "accel_z": np.array(accel_z, dtype=np.float32),
        "gyro_x":  np.array(gyro_x,  dtype=np.float32),
        "gyro_y":  np.array(gyro_y,  dtype=np.float32),
        "gyro_z":  np.array(gyro_z,  dtype=np.float32),
    }
    labels = np.array(labels)

    return data, labels


def save_features(features, labels, output_path):
    """
    Save extracted features to a file.
    
    Args:
        features: numpy array of shape (n_samples, n_features)
        labels: numpy array of shape (n_samples,)
        output_path: path to save the file (e.g., .npz format)
    
    Implementation hints:
        - Use np.savez(output_path, features=features, labels=labels)
        - This creates a compressed file that can be loaded with np.load()
    """
    pass  # TODO: Implement


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
    """
    pass  # TODO: Implement


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
