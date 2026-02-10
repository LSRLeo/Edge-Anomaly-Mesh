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



# ============================================================================
# WINDOWING
# ============================================================================



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
        feature_names = []
        axes = ['accel_x', 'accel_y', 'accel_z', 'gyro_x', 'gyro_y', 'gyro_z']
        time_features = ['mean', 'std', 'rms', 'peak_to_peak', 'zero_crossings']
        freq_features = ['dominant_freq', 'spectral_energy']

        # Time-domain features for each axis
        for axis in axes:
            for feat in time_features:
                feature_names.append(f"{axis}_{feat}")

        # Frequency-domain features for accelerometer axes
        for axis in axes[:3]:  # accel_x, accel_y, accel_z
            for feat in freq_features:
                feature_names.append(f"{axis}_{feat}")

        # Cross-axis features
        feature_names.append("accel_magnitude_mean")
        feature_names.append("gyro_magnitude_mean")

        return feature_names
    
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
        features = []

        # 1. Time-domain features for each of the 6 axes
        for i in range(6):
            features.extend(self._time_domain_features(window[:, i]))

        # 2. Frequency-domain features for accelerometer axes (columns 0,1,2)
        for i in range(3):
            features.extend(self._frequency_domain_features(window[:, i]))

        # 3. Cross-axis features
        features.extend(self._cross_axis_features(window))

        # 4. Concatenate all into one vector
        return np.array(features)
    
    def extract_batch(self, windows):
        """
        Extract features from multiple windows.
        
        Args:
            windows: numpy array of shape (n_windows, n_samples, 6)
        
        Returns:
            numpy array of shape (n_windows, n_features)
        """
        return np.array([self.extract(w) for w in windows])
    
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
        #mean
        mean = np.mean(signal)

        #standard deviation
        std = np.std(signal)
        #root mean square
        rms = np.sqrt(np.mean(signal ** 2))
        #peak to peak
        peak_to_peak = np.max(signal) - np.min(signal)

        #zero crossings
        zero_crossings = np.sum(np.diff(np.sign(signal)) != 0)
        
        return [mean, std, rms, peak_to_peak, zero_crossings]

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
        # Remove DC component
        signal_centered = signal - np.mean(signal)
        n = len(signal_centered)

        # FFT transform
        fft_vals = fft.fft(signal_centered)
        freqs = fft.fftfreq(n, d=1/self.sample_rate)

        # Only positive frequencies
        pos_mask = freqs > 0
        fft_mags = np.abs(fft_vals)[pos_mask]
        pos_freqs = freqs[pos_mask]

        # Spectral energy
        spectral_energy = np.sum(fft_mags ** 2)
        
        # Dominant frequency (skip DC)
        if len(fft_mags) > 0:
            dominant_idx = np.argmax(fft_mags)
            dominant_freq = pos_freqs[dominant_idx]
        else:
            dominant_freq = 0.0
        return [dominant_freq, spectral_energy]
    
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
        # Accelerometer magnitude mean
        accel_magnitude = np.sqrt(window[:, 0]**2 + window[:, 1]**2 + window[:, 2]**2)
        accel_magnitude_mean = np.mean(accel_magnitude)

        # Gyroscope magnitude mean
        gyro_magnitude = np.sqrt(window[:, 3]**2 + window[:, 4]**2 + window[:, 5]**2)
        gyro_magnitude_mean = np.mean(gyro_magnitude)

        return [accel_magnitude_mean, gyro_magnitude_mean]

# ============================================================================
# NORMALIZATION
# ============================================================================

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

# ============================================================================
# DEMO / MAIN
# ============================================================================

def main():
    """
    Main entry point.
    """
    print("Feature extraction module loaded. No CLI or demo available.")


if __name__ == '__main__':
    main()
