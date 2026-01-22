"""
TERRESTRIAL Motion Generator

Simulates cargo in a truck or train moving on roads/rails.

Characteristics:
- Horizontal shaking from road bumps and surface irregularities
- Regular, periodic vibration pattern (typically 2-5 Hz)
- Less vertical movement than horizontal (suspension absorbs)
- Occasional larger bumps/potholes
- Speed-dependent vibration intensity

Example output:
- accel_x: Sinusoidal pattern ± 0.35 m/s² + noise
- accel_y: Sinusoidal pattern ± 0.25 m/s² + noise (phase shifted)
- accel_z: ~9.81 with smaller oscillation ± 0.12 m/s²
- gyro: Correlated with acceleration, smaller magnitude
"""

from .base import BaseMotionGenerator, SensorReading
from typing import Optional


class TerrestrialMotionGenerator(BaseMotionGenerator):
    """
    Generates sensor data for road/rail transport.
    
    Models the characteristic vibration pattern of vehicles on roads:
    - Primary vibration frequency (road texture, wheel rotation)
    - Secondary harmonics
    - Random bumps and potholes
    - Speed-dependent intensity
    
    Attributes:
        frequency: Primary vibration frequency in Hz
        amplitude_x: X-axis vibration amplitude
        amplitude_y: Y-axis vibration amplitude  
        amplitude_z: Z-axis vibration amplitude
        speed: Simulated vehicle speed (affects intensity)
    """
    
    def __init__(self, sample_rate: int = 50, frequency: float = 3.0):
        """
        Initialize the TERRESTRIAL motion generator.
        
        Args:
            sample_rate: Readings per second (Hz)
            frequency: Primary vibration frequency (default 3 Hz typical for trucks)
        """
        # TODO: Call parent __init__
        # TODO: Store primary frequency (2-5 Hz range typical)
        # TODO: Set amplitude_x (suggested: 0.35 m/s²)
        # TODO: Set amplitude_y (suggested: 0.25 m/s²)
        # TODO: Set amplitude_z (suggested: 0.12 m/s²)
        # TODO: Set noise standard deviations
        # TODO: Initialize time counter
        # TODO: Initialize phase offsets for each axis
        pass
    
    @property
    def motion_type(self) -> str:
        """Return 'TERRESTRIAL' as the motion type identifier."""
        # TODO: Return "TERRESTRIAL"
        pass
    
    def generate_reading(self) -> SensorReading:
        """
        Generate a single TERRESTRIAL sensor reading.
        
        Physics model:
        - X-axis: Primary sinusoidal vibration (road bumps)
        - Y-axis: Phase-shifted sinusoid (lateral sway)
        - Z-axis: Gravity + smaller vertical oscillation
        - Random bump probability (~5% chance of spike)
        - Gyroscope correlated with body rotation from bumps
        
        Returns:
            SensorReading with road transport values
        """
        # TODO: Get current timestamp
        
        # TODO: Calculate base sinusoidal vibration for X-axis
        #   accel_x = amplitude_x * sin(2 * pi * frequency * t) + noise
        
        # TODO: Calculate Y-axis with phase offset (pi/4 typical)
        #   accel_y = amplitude_y * sin(2 * pi * frequency * t + phase_y) + noise
        
        # TODO: Calculate Z-axis (smaller amplitude)
        #   accel_z = GRAVITY + amplitude_z * sin(2 * pi * frequency * t) + noise
        
        # TODO: Add random bump with ~5% probability
        #   if random() < 0.05:
        #       add spike to appropriate axis
        
        # TODO: Calculate gyroscope values (correlated with tilting)
        #   gyro_x = scaled from accel_y (roll)
        #   gyro_y = scaled from accel_x (pitch)
        #   gyro_z = small yaw component
        
        # TODO: Advance time counter
        
        # TODO: Return SensorReading
        pass
    
    def set_speed(self, speed_kmh: float) -> None:
        """
        Adjust vibration intensity based on vehicle speed.
        
        Higher speeds generally mean more vibration and higher frequencies.
        
        Args:
            speed_kmh: Vehicle speed in km/h
        """
        # TODO: Scale amplitudes based on speed
        #   - Low speed (<30 km/h): reduce amplitude by 50%
        #   - Medium speed (30-80 km/h): normal amplitude
        #   - High speed (>80 km/h): increase amplitude by 25%
        # TODO: Optionally adjust frequency slightly with speed
        pass
    
    def set_road_quality(self, quality: str) -> None:
        """
        Adjust vibration based on road surface quality.
        
        Args:
            quality: One of "smooth", "normal", "rough", "offroad"
        """
        # TODO: Map quality to amplitude multipliers
        #   smooth: 0.5x amplitude
        #   normal: 1.0x amplitude
        #   rough: 1.5x amplitude
        #   offroad: 2.0x amplitude, add secondary frequencies
        pass
    
    def add_pothole(self) -> None:
        """
        Inject a pothole event into the next few readings.
        
        Simulates hitting a pothole with sudden vertical displacement
        followed by settling oscillation.
        """
        # TODO: Set flag to inject pothole in next reading
        # TODO: Store pothole magnitude and duration
        pass
    
    def _add_secondary_harmonics(self, base_value: float, t: float) -> float:
        """
        Add secondary vibration harmonics for more realistic motion.
        
        Real road vibration has multiple frequency components.
        
        Args:
            base_value: The primary vibration value
            t: Current timestamp
            
        Returns:
            Value with added harmonic content
        """
        # TODO: Add 2nd harmonic (2x frequency, 0.3x amplitude)
        # TODO: Add 3rd harmonic (3x frequency, 0.1x amplitude)
        # TODO: Return combined value
        pass
