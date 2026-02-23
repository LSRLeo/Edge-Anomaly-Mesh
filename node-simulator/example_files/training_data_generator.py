"""
Training Data Generator

Generates labeled datasets for Team 2's ML model training.

This module creates:
1. Labeled training data for motion classification
2. Validation and test splits
3. Anomaly examples for anomaly detection training
4. Pre-windowed data ready for feature extraction

Data is saved in formats suitable for ML:
- CSV for easy inspection
- NumPy arrays for direct model input
- JSON for metadata

Directory structure created:
    data/training/
    ├── raw/                    # Raw sensor readings with labels
    │   ├── idle/
    │   ├── terrestrial/
    │   ├── maritime/
    │   └── lift/
    ├── windowed/               # Pre-windowed samples (2-5 sec windows)
    │   ├── train/
    │   ├── val/
    │   └── test/
    ├── anomalies/              # Anomaly examples
    │   ├── normal/
    │   └── anomalous/
    └── metadata.json           # Dataset statistics and parameters
"""

import os
import json
import csv
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum

# Would import from motion_generators
# from .motion_generators import (
#     get_generator,
#     BaseMotionGenerator,
#     SensorReading,
#     MOTION_GENERATORS
# )


class AnomalyType(Enum):
    """Types of anomalies that can be injected."""
    SPIKE = "spike"                 # Sudden acceleration spike (impact/drop)
    DROPOUT = "dropout"             # Sensor loses gravity signal
    DRIFT = "drift"                 # Gradual calibration drift
    HIGH_FREQUENCY = "high_freq"    # Unexpected vibration
    FLATLINE = "flatline"           # Sensor stuck at constant value
    NOISE_BURST = "noise_burst"     # Sudden increase in noise


@dataclass
class DatasetConfig:
    """
    Configuration for training dataset generation.
    
    Attributes:
        samples_per_class: Number of windows per motion class
        window_size_seconds: Duration of each window
        sample_rate_hz: Sensor sampling rate
        train_ratio: Fraction for training set
        val_ratio: Fraction for validation set
        test_ratio: Fraction for test set
        anomaly_ratio: Fraction of samples with anomalies (for anomaly dataset)
        random_seed: For reproducibility
    """
    samples_per_class: int = 1000
    window_size_seconds: float = 2.0
    sample_rate_hz: int = 50
    train_ratio: float = 0.7
    val_ratio: float = 0.15
    test_ratio: float = 0.15
    anomaly_ratio: float = 0.2
    random_seed: int = 42
    
    @property
    def window_size_samples(self) -> int:
        """Number of samples per window."""
        return int(self.window_size_seconds * self.sample_rate_hz)
    
    def validate(self) -> None:
        """Validate configuration values."""
        # TODO: Check ratios sum to 1.0
        # TODO: Check all values are positive
        # TODO: Raise ValueError if invalid
        pass


@dataclass
class WindowedSample:
    """
    A single windowed sample ready for ML.
    
    Attributes:
        window_id: Unique identifier
        motion_class: Label (IDLE, TERRESTRIAL, MARITIME, LIFT)
        readings: List of sensor readings in the window
        has_anomaly: Whether this window contains an anomaly
        anomaly_type: Type of anomaly if present
        metadata: Additional information
    """
    window_id: str
    motion_class: str
    readings: List[Dict[str, float]]
    has_anomaly: bool = False
    anomaly_type: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class TrainingDataGenerator:
    """
    Generates labeled training data for ML model development.
    
    Creates balanced datasets across all motion classes with
    configurable train/val/test splits.
    
    Attributes:
        config: DatasetConfig instance
        output_dir: Base directory for generated data
        generators: Dict of motion type -> generator instance
    """
    
    def __init__(self, config: DatasetConfig = None, output_dir: str = "data/training"):
        """
        Initialize the training data generator.
        
        Args:
            config: Dataset configuration (uses defaults if None)
            output_dir: Base directory for output files
        """
        # TODO: Use default config if None provided
        # TODO: Store config
        # TODO: Store output_dir as Path
        # TODO: Initialize empty generators dict
        # TODO: Set random seed for reproducibility
        pass
    
    def setup(self) -> None:
        """
        Set up generators and create output directories.
        
        Creates directory structure and initializes motion generators.
        """
        # TODO: Create directory structure:
        #   output_dir/
        #   ├── raw/{idle,terrestrial,maritime,lift}/
        #   ├── windowed/{train,val,test}/
        #   └── anomalies/{normal,anomalous}/
        
        # TODO: Initialize motion generators for each type
        #   for motion_type in MOTION_GENERATORS:
        #       generators[motion_type] = get_generator(motion_type)
        pass
    
    def generate_full_dataset(self) -> Dict[str, Any]:
        """
        Generate complete training dataset.
        
        This is the main method - generates all data needed for training.
        
        Returns:
            Dictionary with dataset statistics and file paths
        """
        # TODO: Call setup() if not already done
        
        # TODO: Generate raw labeled data for each motion class
        #   for motion_type in MOTION_GENERATORS:
        #       generate_raw_class_data(motion_type)
        
        # TODO: Generate windowed samples
        #   generate_windowed_dataset()
        
        # TODO: Generate anomaly dataset
        #   generate_anomaly_dataset()
        
        # TODO: Save metadata
        #   save_metadata()
        
        # TODO: Return statistics dictionary
        pass
    
    def generate_raw_class_data(self, motion_class: str, num_seconds: int = None) -> Path:
        """
        Generate raw sensor data for a single motion class.
        
        Args:
            motion_class: One of IDLE, TERRESTRIAL, MARITIME, LIFT
            num_seconds: Duration in seconds (calculated from config if None)
            
        Returns:
            Path to the generated CSV file
        """
        # TODO: Calculate num_seconds if not provided
        #   num_seconds = samples_per_class * window_size_seconds
        
        # TODO: Get generator for this motion class
        
        # TODO: Generate readings for full duration
        #   readings = generator.generate_duration(num_seconds)
        
        # TODO: Save to CSV with columns:
        #   timestamp, accel_x, accel_y, accel_z, gyro_x, gyro_y, gyro_z, label
        
        # TODO: Return file path
        pass
    
    def generate_windowed_dataset(self) -> Dict[str, int]:
        """
        Generate pre-windowed samples with train/val/test splits.
        
        Creates WindowedSample objects and saves to appropriate split folders.
        
        Returns:
            Dictionary with counts per split: {"train": N, "val": N, "test": N}
        """
        # TODO: For each motion class:
        #   - Generate samples_per_class windows
        #   - Shuffle windows
        #   - Split according to train_ratio, val_ratio, test_ratio
        #   - Save to appropriate directories
        
        # TODO: Return counts dictionary
        pass
    
    def generate_single_window(
        self, 
        motion_class: str, 
        inject_anomaly: bool = False,
        anomaly_type: AnomalyType = None
    ) -> WindowedSample:
        """
        Generate a single windowed sample.
        
        Args:
            motion_class: Motion type to generate
            inject_anomaly: Whether to inject an anomaly
            anomaly_type: Type of anomaly (random if None and inject_anomaly=True)
            
        Returns:
            WindowedSample instance
        """
        # TODO: Get generator for motion class
        
        # TODO: Generate window_size_samples readings
        
        # TODO: If inject_anomaly:
        #   - Select anomaly_type randomly if not provided
        #   - Call _inject_anomaly() on readings
        
        # TODO: Create and return WindowedSample
        pass
    
    def generate_anomaly_dataset(self) -> Dict[str, int]:
        """
        Generate dataset specifically for anomaly detection training.
        
        Creates balanced set of normal and anomalous windows.
        
        Returns:
            Dictionary with counts: {"normal": N, "anomalous": N}
        """
        # TODO: Calculate number of each type based on anomaly_ratio
        
        # TODO: Generate normal windows (from all motion classes)
        
        # TODO: Generate anomalous windows with various anomaly types
        
        # TODO: Save to anomalies/normal/ and anomalies/anomalous/
        
        # TODO: Return counts
        pass
    
    def _inject_anomaly(
        self, 
        readings: List[Dict[str, float]], 
        anomaly_type: AnomalyType
    ) -> List[Dict[str, float]]:
        """
        Inject an anomaly into a window of readings.
        
        Args:
            readings: List of sensor readings
            anomaly_type: Type of anomaly to inject
            
        Returns:
            Modified readings with anomaly
        """
        # TODO: Based on anomaly_type:
        
        #   SPIKE:
        #       - Pick random index
        #       - Add large value to accel values (simulate impact)
        
        #   DROPOUT:
        #       - Pick range of indices
        #       - Set accel_z to ~0 (lost gravity signal)
        
        #   DRIFT:
        #       - Gradually increase/decrease values over window
        #       - Simulates calibration drift
        
        #   HIGH_FREQUENCY:
        #       - Add high-frequency sine wave
        #       - Simulates unexpected vibration
        
        #   FLATLINE:
        #       - Set range of readings to constant value
        #       - Simulates stuck sensor
        
        #   NOISE_BURST:
        #       - Increase noise dramatically for portion of window
        
        # TODO: Return modified readings
        pass
    
    def _inject_spike_anomaly(
        self, 
        readings: List[Dict], 
        magnitude: float = 5.0
    ) -> List[Dict]:
        """
        Inject a spike anomaly (sudden impact).
        
        Args:
            readings: Sensor readings
            magnitude: Spike magnitude in m/s²
            
        Returns:
            Modified readings
        """
        # TODO: Select random position in window
        # TODO: Add spike to acceleration values
        # TODO: Optionally affect 1-3 consecutive readings
        # TODO: Return modified readings
        pass
    
    def _inject_dropout_anomaly(
        self, 
        readings: List[Dict], 
        duration_fraction: float = 0.1
    ) -> List[Dict]:
        """
        Inject a dropout anomaly (sensor failure).
        
        Args:
            readings: Sensor readings
            duration_fraction: Fraction of window affected
            
        Returns:
            Modified readings
        """
        # TODO: Calculate number of readings to affect
        # TODO: Select random start position
        # TODO: Set accel_z to near 0 (no gravity = sensor failure)
        # TODO: Optionally zero out other values
        # TODO: Return modified readings
        pass
    
    def _inject_drift_anomaly(
        self, 
        readings: List[Dict], 
        drift_rate: float = 0.01
    ) -> List[Dict]:
        """
        Inject a drift anomaly (calibration drift).
        
        Args:
            readings: Sensor readings
            drift_rate: Rate of drift per sample
            
        Returns:
            Modified readings
        """
        # TODO: Select axis to drift (or multiple)
        # TODO: Apply cumulative drift over window
        # TODO: Return modified readings
        pass
    
    def save_windowed_sample(self, sample: WindowedSample, split: str) -> Path:
        """
        Save a windowed sample to disk.
        
        Args:
            sample: WindowedSample to save
            split: One of "train", "val", "test"
            
        Returns:
            Path to saved file
        """
        # TODO: Determine output path based on split
        # TODO: Save as JSON or CSV
        # TODO: Return file path
        pass
    
    def save_metadata(self) -> Path:
        """
        Save dataset metadata and statistics.
        
        Returns:
            Path to metadata.json
        """
        # TODO: Compile statistics:
        #   - Total samples per class
        #   - Samples per split
        #   - Anomaly counts by type
        #   - Generation timestamp
        #   - Config parameters
        
        # TODO: Save as JSON
        # TODO: Return path
        pass
    
    def export_to_numpy(self, split: str = "train") -> Tuple[Any, Any]:
        """
        Export windowed data as NumPy arrays for direct ML use.
        
        Args:
            split: Which split to export
            
        Returns:
            Tuple of (X, y) where:
            - X: shape (num_samples, window_size, 6) - sensor data
            - y: shape (num_samples,) - labels as integers
        """
        # TODO: Load all samples for the split
        # TODO: Convert to numpy arrays
        # TODO: Encode labels as integers:
        #   IDLE=0, TERRESTRIAL=1, MARITIME=2, LIFT=3
        # TODO: Return (X, y)
        pass
    
    def get_class_distribution(self, split: str = "train") -> Dict[str, int]:
        """
        Get the class distribution for a split.
        
        Args:
            split: Which split to analyze
            
        Returns:
            Dictionary of motion_class -> count
        """
        # TODO: Count samples per class in the split
        # TODO: Return counts dictionary
        pass


class AnomalyDataGenerator:
    """
    Specialized generator for anomaly detection training data.
    
    Creates paired normal/anomalous samples to help Team 2
    train their anomaly detector.
    """
    
    def __init__(self, base_generator: TrainingDataGenerator):
        """
        Initialize anomaly data generator.
        
        Args:
            base_generator: TrainingDataGenerator for normal data
        """
        # TODO: Store base_generator
        # TODO: Define anomaly type weights (how often each type appears)
        pass
    
    def generate_paired_samples(
        self, 
        num_pairs: int = 100
    ) -> List[Tuple[WindowedSample, WindowedSample]]:
        """
        Generate pairs of (normal, anomalous) samples.
        
        Each pair has the same base motion with one having an anomaly.
        Useful for contrastive learning approaches.
        
        Args:
            num_pairs: Number of pairs to generate
            
        Returns:
            List of (normal_sample, anomalous_sample) tuples
        """
        # TODO: For each pair:
        #   - Pick random motion class
        #   - Generate normal window
        #   - Copy and inject anomaly
        #   - Return both
        pass
    
    def generate_anomaly_examples(
        self, 
        anomaly_type: AnomalyType, 
        num_examples: int = 50
    ) -> List[WindowedSample]:
        """
        Generate examples of a specific anomaly type.
        
        Args:
            anomaly_type: Type of anomaly to generate
            num_examples: Number of examples
            
        Returns:
            List of anomalous WindowedSamples
        """
        # TODO: Generate examples with specified anomaly type
        # TODO: Vary the underlying motion class
        # TODO: Return list of samples
        pass
    
    def get_anomaly_type_distribution(self) -> Dict[str, float]:
        """
        Get the target distribution of anomaly types.
        
        Returns:
            Dictionary of anomaly_type -> probability
        """
        # TODO: Return configured distribution
        pass


def generate_training_data(
    output_dir: str = "data/training",
    samples_per_class: int = 1000,
    window_size: float = 2.0,
    random_seed: int = 42
) -> Dict[str, Any]:
    """
    Convenience function to generate a complete training dataset.
    
    Args:
        output_dir: Where to save the data
        samples_per_class: Number of windows per motion class
        window_size: Window duration in seconds
        random_seed: For reproducibility
        
    Returns:
        Dictionary with paths and statistics
    """
    # TODO: Create config
    # TODO: Create generator
    # TODO: Run generate_full_dataset()
    # TODO: Return results
    pass


def main():
    """
    Command-line interface for training data generation.
    
    Usage:
        python training_data_generator.py --samples 1000 --output data/training
    """
    # TODO: Parse arguments:
    #   --samples: samples per class
    #   --window-size: window duration
    #   --output: output directory
    #   --seed: random seed
    #   --anomaly-ratio: ratio of anomalous samples
    
    # TODO: Create config from arguments
    
    # TODO: Run generation
    
    # TODO: Print summary statistics
    pass


if __name__ == "__main__":
    main()
