#!/usr/bin/env python3
"""
feature_extraction.py

Feature extraction pipeline for motion classification.
Converts raw sensor windows into feature vectors for ML models.

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

Usage:
    # Run with defaults
    python feature_extraction.py
    
    # Custom settings
    python feature_extraction.py --window-size 150 --overlap 0.5 --data-dir data/generated_data

Requirements:
    pip install numpy scipy
"""

import argparse
import numpy as np
from scipy import fft
from pathlib import Path
import csv


# ============================================================================
# ARGUMENT PARSING
# ============================================================================

def parse_args():
    """
    Parse command-line arguments.
    
    This allows users to customize behavior without editing code.
    
    Returns:
        argparse.Namespace with all arguments as attributes
        Access like: args.window_size, args.overlap, etc.
    """
    parser = argparse.ArgumentParser(
        description='Extract features from motion sensor data',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter  # Shows defaults in --help
    )
    
    # Data arguments
    parser.add_argument('--data-dir', type=str, default='data/generated_data',
                        help='Directory containing sensor data CSV files')
    
    parser.add_argument('--output-dir', type=str, default='data/features',
                        help='Directory to save extracted features')
    
    # Windowing arguments
    parser.add_argument('--window-size', type=int, default=100,
                        help='Number of samples per window (100 = 2 sec at 50Hz)')
    
    parser.add_argument('--overlap', type=float, default=0.5,
                        help='Fraction of overlap between windows (0.0 to 0.99)')
    
    parser.add_argument('--sample-rate', type=int, default=50,
                        help='Sensor sample rate in Hz')
    
    # Output options
    parser.add_argument('--save', action='store_true',
                        help='Save extracted features to files')
    
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
# FEATURE EXTRACTOR CLASS
# ============================================================================

class FeatureExtractor:
    """
    Extracts features from sensor data windows.
    
    Converts a window of raw readings into a fixed-length feature vector
    that captures the important characteristics of the motion.
    
    Feature categories:
        1. Time-domain: Statistics computed directly on the signal
        2. Frequency-domain: Characteristics of the frequency spectrum (FFT)
        3. Cross-axis: Features combining multiple sensor axes
    """
    
    def __init__(self, sample_rate=50):
        """
        Initialize the feature extractor.
        
        Args:
            sample_rate: sensor sampling rate in Hz (default 50)
                         Needed for frequency calculations.
        """
        self.sample_rate = sample_rate
        self.feature_names = self._get_feature_names()
    
    def _get_feature_names(self):
        """
        Return list of feature names for documentation/debugging.
        
        This should match exactly what extract() produces.
        Useful for understanding which features are most important.
        
        Returns:
            List of strings, one name per feature.
        
        Example output:
            ['accel_x_mean', 'accel_x_std', 'accel_x_rms', ...]
        """
        pass  # TODO: Implement
    
    @property
    def n_features(self):
        """Return the total number of features extracted."""
        return len(self.feature_names)
    
    def extract(self, window):
        """
        Extract features from a single window.
        
        This is the core function that converts raw sensor data
        into a feature vector the ML model can use.
        
        Args:
            window: numpy array of shape (n_samples, 6)
                    Columns: [accel_x, accel_y, accel_z, gyro_x, gyro_y, gyro_z]
        
        Returns:
            numpy array of shape (n_features,)
        
        Implementation:
            1. Extract time-domain features for each of the 6 axes
            2. Extract frequency-domain features for accelerometer axes
            3. Extract cross-axis features
            4. Concatenate all into one vector
        """
        pass  # TODO: Implement
    
    def extract_batch(self, windows):
        """
        Extract features from multiple windows.
        
        Args:
            windows: numpy array of shape (n_windows, n_samples, 6)
        
        Returns:
            numpy array of shape (n_windows, n_features)
        
        Implementation hints:
            - Simply call extract() on each window
            - Use list comprehension or np.array([self.extract(w) for w in windows])
        """
        pass  # TODO: Implement
    
    def _time_domain_features(self, signal):
        """
        Extract time-domain features from a 1D signal.
        
        These features describe the statistical properties of the signal
        without considering frequency content.
        
        Args:
            signal: 1D numpy array of sensor readings
        
        Returns:
            List of 5 features:
                1. mean: Average value
                   - IDLE accel_z ≈ 9.81 (gravity)
                   - Useful for detecting orientation
                
                2. std: Standard deviation
                   - Low for IDLE, high for MARITIME
                   - Measures "how much movement"
                
                3. rms: Root Mean Square = sqrt(mean(signal²))
                   - Measures signal energy/intensity
                   - Similar to std but includes DC component
                
                4. peak_to_peak: max - min
                   - Range of motion
                   - LIFT has large Z-axis peak-to-peak
                
                5. zero_crossings: Number of times signal crosses zero
                   - Indicates oscillation frequency
                   - High for vibrating (TERRESTRIAL), low for IDLE
        
        Implementation hints:
            - np.mean(), np.std(), np.max(), np.min()
            - RMS: np.sqrt(np.mean(signal ** 2))
            - Zero crossings: np.sum(np.diff(np.sign(signal)) != 0)
        """
        pass  # TODO: Implement
    
    def _frequency_domain_features(self, signal):
        """
        Extract frequency-domain features using FFT.
        
        FFT (Fast Fourier Transform) reveals which frequencies are
        present in the signal. Different motions have different
        frequency signatures.
        
        Args:
            signal: 1D numpy array of sensor readings
        
        Returns:
            List of 2 features:
                1. dominant_freq: Frequency with highest magnitude (Hz)
                   - TERRESTRIAL: 2-5 Hz (road vibration)
                   - MARITIME: varies (wave frequencies)
                   - IDLE: ~0 (no dominant frequency)
                
                2. spectral_energy: Sum of squared FFT magnitudes
                   - Total energy across all frequencies
                   - High for active motion, low for IDLE
        
        Implementation hints:
            - Remove DC component first: signal_centered = signal - np.mean(signal)
            - Use scipy.fft.fft() for the transform
            - Use scipy.fft.fftfreq() to get frequency axis
            - Only use positive frequencies (first half of FFT output)
            - Skip index 0 when finding dominant frequency (that's DC)
        """
        pass  # TODO: Implement
    
    def _cross_axis_features(self, window):
        """
        Extract features that combine multiple sensor axes.
        
        Some patterns are better captured by looking at combined motion
        rather than individual axes.
        
        Args:
            window: numpy array of shape (n_samples, 6)
        
        Returns:
            List of 2 features:
                1. accel_magnitude_mean: Mean of sqrt(ax² + ay² + az²)
                   - Total acceleration regardless of direction
                   - IDLE ≈ 9.81, higher during active motion
                
                2. gyro_magnitude_mean: Mean of sqrt(gx² + gy² + gz²)
                   - Total rotational velocity
                   - High for tumbling/rotating motion
        
        Implementation hints:
            - accel_magnitude = np.sqrt(window[:,0]**2 + window[:,1]**2 + window[:,2]**2)
            - Take the mean of the magnitude array
        """
        pass  # TODO: Implement


# ============================================================================
# NORMALIZATION
# ============================================================================

def normalize_features(features, scaler=None):
    """
    Normalize features to zero mean and unit variance.
    
    Normalization is important because:
        - Features have different scales (accel in m/s², gyro in rad/s)
        - Neural networks train better with normalized inputs
        - Prevents features with large values from dominating
    
    Args:
        features: numpy array of shape (n_samples, n_features)
        scaler: optional tuple of (mean, std) from training data
                If None, compute from the input features.
                If provided, use these values (for test data).
    
    Returns:
        normalized: numpy array of same shape, normalized
        scaler: tuple of (mean, std) arrays for reuse
    
    Formula:
        normalized = (features - mean) / std
    
    Implementation hints:
        - Compute mean and std along axis=0 (per feature)
        - Handle std=0 case: set to 1 to avoid division by zero
        - Save scaler during training, reuse for inference
    """
    pass  # TODO: Implement


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def load_csv_data(filepath):
    """
    Load sensor data from CSV file.
    
    Args:
        filepath: path to CSV file
    
    Returns:
        dict with numpy arrays for each sensor channel
    """
    pass  # TODO: Implement


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
# DEMO / MAIN
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


def main():
    """
    Main entry point.
    
    Parses arguments and runs the demo.
    """
    args = parse_args()
    
    if args.verbose:
        print("=" * 60)
        print("Feature Extraction")
        print("=" * 60)
        print(f"  Data directory:  {args.data_dir}")
        print(f"  Window size:     {args.window_size} samples")
        print(f"  Overlap:         {args.overlap * 100}%")
        print(f"  Sample rate:     {args.sample_rate} Hz")
        print(f"  Save features:   {args.save}")
        print("=" * 60)
    
    demo(args)


if __name__ == '__main__':
    main()
