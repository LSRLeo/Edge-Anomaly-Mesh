# from .base import BaseMotionGenerator, SensorReading
from typing import List, Tuple
from enum import Enum

class Idle:
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
    noise_std_accel = 0 #Standard deviation of accelerometer noise
    noise_std_gyro = 0 #Standard deviation of gyroscope noise


    def generate_reading():
        accel_x = 0
        accel_y = 0
        accel_z = 9.81
        gyro_x = 0
        gyro_y = 0
        gyro_z = 0

        return SensorReading(accel_x, accel_y, accel_z, gyro_x, gyro_y, gyro_z)
    
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
    

    pass

class Lift:
    """
LIFT Motion Generator

Simulates cargo being lifted and moved by a forklift.

Characteristics:
- Clear vertical acceleration/deceleration phases
- Distinctive 8-10 second cycle: lift → hold → lower → rest
- Z-axis shows trapezoid acceleration pattern
- Minimal horizontal movement during lift
- Small oscillations during hold phase (forklift vibration)

Cycle phases:
1. LIFT UP (0-15%): Positive Z acceleration (feel heavier)
2. HOLD/MOVE (15-50%): Constant height, may move horizontally
3. LOWER DOWN (50-65%): Negative Z acceleration (feel lighter)
4. REST (65-100%): Stationary, waiting for next cycle

Example output:
- accel_z: Trapezoid pattern with gravity baseline
  - Lifting: 9.81 + 3.5 = ~13.3 m/s²
  - Holding: ~9.81 m/s²
  - Lowering: 9.81 - 3.5 = ~6.3 m/s²
- accel_x/y: Small during lift/lower, may increase during horizontal move
"""
class LiftPhase(Enum):
    """Phases of a forklift lift cycle."""
    LIFT_UP = "lift_up"
    HOLD_MOVE = "hold_move"
    LOWER_DOWN = "lower_down"
    REST = "rest"

    def __init__(self, sample_rate: int = 50, cycle_duration: float = 8.0):
        """
        Initialize the LIFT motion generator.
        
        Args:
            sample_rate: Readings per second (Hz)
            cycle_duration: Total lift cycle duration in seconds
        """
        # TODO: Call parent __init__
        # TODO: Set cycle_duration (8-10 seconds typical)
        # TODO: Set lift_acceleration (suggested: 3.5 m/s²)
        # TODO: Define phase boundaries as fractions of cycle:
        #   LIFT_UP: 0.0 - 0.15 (15% of cycle)
        #   HOLD_MOVE: 0.15 - 0.50 (35% of cycle)
        #   LOWER_DOWN: 0.50 - 0.65 (15% of cycle)
        #   REST: 0.65 - 1.0 (35% of cycle)
        # TODO: Set horizontal movement amplitude during hold
        # TODO: Initialize time counter
        pass


    pass

class Maritime:
    """
MARITIME Motion Generator

Simulates cargo on a ship in various sea conditions.

Characteristics:
- Chaotic 3D motion (all axes equally affected by waves)
- Multiple overlapping wave frequencies (0.5-4 Hz)
- Random wave impacts (sudden spikes)
- Non-periodic, unpredictable pattern
- Slow rolling motion mixed with faster wave slaps
- Sea state dependent intensity

Example output:
- accel_x/y/z: Multiple superimposed sine waves + random spikes
- Pattern appears more chaotic than terrestrial
- Longer wavelength oscillations with occasional sharp impacts
- Gyroscope shows significant rotation on all axes
"""
    def __init__(self, sample_rate: int = 50, sea_state: int = 4):
        """
        Initialize the MARITIME motion generator.
        
        Args:
            sample_rate: Readings per second (Hz)
            sea_state: Sea condition 1-9 (4 = moderate waves)
        """
        # TODO: Call parent __init__
        # TODO: Define wave frequencies list [0.7, 1.3, 2.1, 3.2] Hz
        # TODO: Generate random phase offsets for each frequency
        # TODO: Set base amplitude (suggested: 0.3 m/s² per component)
        # TODO: Set sea_state and scale amplitude accordingly
        # TODO: Set spike probability (suggested: 0.05 = 5%)
        # TODO: Set noise standard deviation (higher than terrestrial)
        # TODO: Initialize time counter
        pass
    
    pass

class Terrestrial:
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

    
    pass
class Lift:
    pass

class Maritime:
    pass

class Terrestrial:
    pass

class SensorReading:
    def __init__(self, accel_x, accel_y, accel_z, gyro_x, gyro_y, gyro_z):
        self.accel_x = accel_x
        self.accel_y = accel_y
        self.accel_z = accel_z
        self.gyro_x = gyro_x
        self.gyro_y = gyro_y
        self.gyro_z = gyro_z
