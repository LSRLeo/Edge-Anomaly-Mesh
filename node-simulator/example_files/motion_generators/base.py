"""
Abstract base class for motion generators.

All motion generators (idle, terrestrial, maritime, lift) must inherit
from this class and implement the required methods.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class SensorReading:
    """
    Represents a single sensor reading with accelerometer and gyroscope data.
    
    Attributes:
        timestamp: Time of reading in seconds since start
        accel_x: X-axis acceleration in m/s²
        accel_y: Y-axis acceleration in m/s²
        accel_z: Z-axis acceleration in m/s² (includes gravity ~9.81)
        gyro_x: X-axis angular velocity in rad/s
        gyro_y: Y-axis angular velocity in rad/s
        gyro_z: Z-axis angular velocity in rad/s
    """
    timestamp: float
    accel_x: float
    accel_y: float
    accel_z: float
    gyro_x: float
    gyro_y: float
    gyro_z: float


class BaseMotionGenerator(ABC):
    """
    Abstract base class for all motion generators.
    
    Each motion type (IDLE, TERRESTRIAL, MARITIME, LIFT) should subclass
    this and implement the generate_reading() method with physics-appropriate
    sensor data simulation.
    
    Attributes:
        motion_type: String identifier for the motion type
        sample_rate: Sampling frequency in Hz (default 50)
        gravity: Gravitational acceleration constant (9.81 m/s²)
    """
    
    def __init__(self, sample_rate: int = 50):
        """
        Initialize the motion generator.
        
        Args:
            sample_rate: How many readings per second to generate (Hz)
        """
        # TODO: Store sample_rate
        # TODO: Initialize gravity constant (9.81)
        # TODO: Initialize internal time counter
        # TODO: Set motion_type identifier
        pass
    
    @property
    @abstractmethod
    def motion_type(self) -> str:
        """
        Return the motion type identifier string.
        
        Returns:
            One of: "IDLE", "TERRESTRIAL", "MARITIME", "LIFT"
        """
        pass
    
    @abstractmethod
    def generate_reading(self) -> SensorReading:
        """
        Generate a single sensor reading based on the motion physics.
        
        This is the core method each subclass must implement. It should:
        1. Calculate appropriate accelerometer values for this motion type
        2. Calculate appropriate gyroscope values for this motion type
        3. Add realistic sensor noise
        4. Advance internal time by 1/sample_rate seconds
        
        Returns:
            SensorReading with all 6 sensor values populated
        """
        pass
    
    def generate_batch(self, num_readings: int) -> list:
        """
        Generate multiple readings at once.
        
        Useful for generating data windows for testing or batch processing.
        
        Args:
            num_readings: Number of consecutive readings to generate
            
        Returns:
            List of SensorReading objects
        """
        # TODO: Loop num_readings times calling generate_reading()
        # TODO: Collect results in a list
        # TODO: Return the list
        pass
    
    def generate_duration(self, seconds: float) -> list:
        """
        Generate readings for a specified duration.
        
        Args:
            seconds: Duration in seconds to generate data for
            
        Returns:
            List of SensorReading objects spanning the duration
        """
        # TODO: Calculate number of readings from seconds * sample_rate
        # TODO: Call generate_batch with calculated count
        # TODO: Return results
        pass
    
    def reset(self) -> None:
        """
        Reset the generator to initial state.
        
        Resets internal time counter and any state variables.
        Useful when starting a new simulation run.
        """
        # TODO: Reset internal time counter to 0
        # TODO: Reset any motion-specific state variables
        pass
    
    def add_noise(self, value: float, std_dev: float) -> float:
        """
        Add Gaussian noise to a sensor value.
        
        Real sensors have measurement noise. This method adds realistic
        noise to simulated readings.
        
        Args:
            value: The base sensor value
            std_dev: Standard deviation of the noise
            
        Returns:
            Value with added Gaussian noise
        """
        # TODO: Use numpy.random.normal(value, std_dev)
        # TODO: Return noisy value
        pass
    
    def to_dict(self, reading: SensorReading) -> Dict[str, Any]:
        """
        Convert a SensorReading to a dictionary for JSON serialization.
        
        Args:
            reading: The SensorReading to convert
            
        Returns:
            Dictionary with all sensor fields
        """
        # TODO: Create dict with timestamp, accel_x/y/z, gyro_x/y/z
        # TODO: Round values to 3 decimal places
        # TODO: Return dictionary
        pass
    
    def inject_anomaly(self, reading: SensorReading, magnitude: float = 2.0) -> SensorReading:
        """
        Inject an anomaly into a reading (for testing anomaly detection).
        
        Simulates sudden impacts, sensor glitches, or unexpected events.
        
        Args:
            reading: The original reading to modify
            magnitude: How strong the anomaly should be (multiplier)
            
        Returns:
            Modified SensorReading with anomalous values
        """
        # TODO: Randomly select which axes to affect
        # TODO: Add spike to selected accelerometer values
        # TODO: Optionally affect gyroscope values
        # TODO: Return modified reading
        pass
