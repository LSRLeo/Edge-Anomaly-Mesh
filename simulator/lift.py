# from .base import BaseMotionGenerator, SensorReading
from typing import List, Tuple
from enum import Enum

from .base import BaseMotionGenerator, SensorReading
from typing import List, Tuple


class Lift:
        def set_hub(self, hub_lat, hub_lon, radius_m):
            """
            Set hub location and radius for package constraint.
            """
            self.hub_lat = hub_lat
            self.hub_lon = hub_lon
            self.hub_radius_m = radius_m

        def is_within_hub_radius(self, gps_lat, gps_lon):
            """
            Check if the package is within the hub radius.
            """
            from math import radians, sin, cos, sqrt, atan2
            lat1 = radians(self.hub_lat)
            lon1 = radians(self.hub_lon)
            lat2 = radians(gps_lat)
            lon2 = radians(gps_lon)
            dlat = lat2 - lat1
            dlon = lon2 - lon1
            #make sure to set acceptable radius to be in. Furthermore, look at Lily's test code and see how big of error we can accept.
            distance = 0
            return distance <= self.hub_radius_m

        def check_location(self, gps_lat, gps_lon):
            if not self.is_within_hub_radius(gps_lat, gps_lon):
                print(f"Warning: Package outside hub radius! Lat: {gps_lat}, Lon: {gps_lon}")
            # Optionally, handle violation (log, alert, etc.)
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
        # Call parent __init__
        super().__init__()
        # Set cycle_duration (8-10 seconds typical)
        self.cycle_duration = cycle_duration
        # Set lift_acceleration (suggested: 3.5 m/s²)
        self.lift_acceleration = 3.5  # m/s²
        # Define phase boundaries as fractions of cycle
        self.phase_boundaries = {
            "LIFT_UP": (0.0, 0.15),
            "HOLD_MOVE": (0.15, 0.50),
            "LOWER_DOWN": (0.50, 0.65),
            "REST": (0.65, 1.0)
        }
        # Set horizontal movement amplitude during hold
        self.horizontal_amplitude = 0.2  # meters (example value for forklift vibration)
        # Initialize time counter
        self.time_counter = 0.0
        pass


    pass


class SensorReading:
    def __init__(self, accel_x, accel_y, accel_z, gyro_x, gyro_y, gyro_z):
        self.accel_x = accel_x
        self.accel_y = accel_y
        self.accel_z = accel_z
        self.gyro_x = gyro_x
        self.gyro_y = gyro_y
        self.gyro_z = gyro_z
