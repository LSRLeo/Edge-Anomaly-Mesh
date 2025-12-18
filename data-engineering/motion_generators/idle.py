"""
IDLE Motion Generator

Simulates cargo sitting stationary in a warehouse or storage facility.

Characteristics:
- Device is completely still
- Only gravity acts on Z-axis (~9.81 m/s²)
- Minimal noise/vibration from environment
- X and Y acceleration near zero
- Gyroscope readings near zero (no rotation)

Example output:
- accel_x: ~0.0 ± 0.05
- accel_y: ~0.0 ± 0.05  
- accel_z: ~9.81 ± 0.05
- gyro_x/y/z: ~0.0 ± 0.01
"""

from .base import BaseMotionGenerator, SensorReading


class IdleMotionGenerator(BaseMotionGenerator):
    """
    Generates sensor data for stationary cargo.
    
    This is the simplest motion type - the cargo is at rest, so we only
    see gravity on the Z-axis plus small environmental vibrations and
    sensor noise.
    
    Attributes:
        noise_std_accel: Standard deviation of accelerometer noise
        noise_std_gyro: Standard deviation of gyroscope noise
    """
    
    def __init__(self, sample_rate: int = 50):
        """
        Initialize the IDLE motion generator.
        
        Args:
            sample_rate: Readings per second (Hz)
        """
        # TODO: Call parent __init__
        # TODO: Set noise_std_accel (suggested: 0.05 m/s²)
        # TODO: Set noise_std_gyro (suggested: 0.01 rad/s)
        # TODO: Initialize time counter to 0
        pass
    
    @property
    def motion_type(self) -> str:
        """Return 'IDLE' as the motion type identifier."""
        # TODO: Return "IDLE"
        pass
    
    def generate_reading(self) -> SensorReading:
        """
        Generate a single IDLE sensor reading.
        
        Physics model:
        - Accelerometer X: 0 + noise
        - Accelerometer Y: 0 + noise
        - Accelerometer Z: gravity (9.81) + noise
        - Gyroscope X/Y/Z: 0 + noise
        
        Returns:
            SensorReading with stationary cargo values
        """
        # TODO: Get current timestamp from internal counter
        
        # TODO: Generate accelerometer values
        #   accel_x = add_noise(0.0, noise_std_accel)
        #   accel_y = add_noise(0.0, noise_std_accel)
        #   accel_z = add_noise(GRAVITY, noise_std_accel)
        
        # TODO: Generate gyroscope values (all near zero)
        #   gyro_x = add_noise(0.0, noise_std_gyro)
        #   gyro_y = add_noise(0.0, noise_std_gyro)
        #   gyro_z = add_noise(0.0, noise_std_gyro)
        
        # TODO: Advance time by 1/sample_rate
        
        # TODO: Return SensorReading with all values
        pass
    
    def set_vibration_level(self, level: float) -> None:
        """
        Adjust environmental vibration level.
        
        Warehouses may have different vibration levels depending on
        nearby machinery, HVAC systems, etc.
        
        Args:
            level: Vibration multiplier (1.0 = normal, 2.0 = double)
        """
        # TODO: Multiply noise_std_accel by level
        # TODO: Store adjusted value
        pass
