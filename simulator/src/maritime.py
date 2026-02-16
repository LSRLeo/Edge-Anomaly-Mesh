import math
import random

class Maritime:
    def __init__(self, sample_rate_hz):
        self.sample_rate_hz = sample_rate_hz
        # Typical cargo boat parameters
        self.cruise_speed_mean = 6.0  # m/s (~12 knots, typical cargo ship)
        self.cruise_speed_std = 1.0   # variation in speed
        self.acceleration = 0.3        # m/s² (typical boat acceleration)
        self.deceleration = 0.3       # m/s² (typical boat deceleration)
        self.gravity = 9.81           # m/s²
        
        # Wave motion parameters (pitch and roll)
        self.wave_period = 8.0        # seconds (typical ocean wave period)
        self.pitch_amplitude = 0.1    # radians (~6 degrees)
        self.roll_amplitude = 0.15    # radians (~9 degrees)
        self.yaw_amplitude = 0.05     # radians (~3 degrees)
    
    def haversine_distance(self, lat1, lon1, lat2, lon2):
        """
        Calculate distance between two GPS coordinates using haversine formula.
        Returns distance in meters.
        """
        R = 6371000  # Earth's radius in meters
        
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)
        
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        distance = R * c
        return distance
    
    def calculate_travel_parameters(self, distance_m):
        """
        Calculate travel parameters and determine if three-phase or triangular velocity.
        Returns: (use_three_phase, cruise_speed, accel_time, cruise_time, decel_time, total_time)
        """
        # Vary the cruise speed
        cruise_speed = random.gauss(self.cruise_speed_mean, self.cruise_speed_std)
        cruise_speed = max(3.0, min(9.0, cruise_speed))  # Clamp between 3-9 m/s
        
        # Calculate time to reach cruise speed
        accel_time = cruise_speed / self.acceleration
        decel_time = cruise_speed / self.deceleration
        
        # Distance covered during acceleration
        accel_distance = 0.5 * self.acceleration * accel_time ** 2
        
        # Distance covered during deceleration
        decel_distance = 0.5 * self.deceleration * decel_time ** 2
        
        # Distance available for cruising
        cruise_distance = distance_m - accel_distance - decel_distance
        
        # Determine if we can reach cruise speed
        if cruise_distance > 0:
            # Three-phase: accelerate, cruise, decelerate
            use_three_phase = True
            cruise_time = cruise_distance / cruise_speed
            total_time = accel_time + cruise_time + decel_time
        else:
            # Triangular: accelerate then immediately decelerate
            use_three_phase = False
            # Solve: distance = 0.5 * a * t_accel^2 + (v0 * t_decel - 0.5 * a * t_decel^2)
            # Where v0 = a * t_accel and t_decel = t_accel (symmetric)
            # distance = a * t_accel^2
            accel_time = math.sqrt(distance_m / self.acceleration)
            cruise_time = 0
            decel_time = accel_time
            total_time = accel_time + decel_time
            # Recalculate cruise speed for triangular case (peak speed reached)
            cruise_speed = self.acceleration * accel_time
        
        return use_three_phase, cruise_speed, accel_time, cruise_time, decel_time, total_time
    
    def get_wave_motion(self, time):
        """
        Generate wave motion (pitch, roll, yaw) at given time.
        Returns: (pitch, roll, yaw) in radians
        """
        # Use different phases for pitch and roll to make it more realistic
        pitch = self.pitch_amplitude * math.sin(2 * math.pi * time / self.wave_period)
        roll = self.roll_amplitude * math.cos(2 * math.pi * time / self.wave_period + math.pi/4)
        yaw = self.yaw_amplitude * math.sin(2 * math.pi * time / (self.wave_period * 1.5))
        
        return pitch, roll, yaw
    
    def generate_reading(self, current_hub, next_hub):
        """
        Generate sensor readings for maritime travel between two hubs.
        Uses boat's local frame: x=forward, y=starboard, z=up
        """
        # Calculate distance between hubs
        distance_m = self.haversine_distance(
            current_hub.lat, current_hub.lon,
            next_hub.lat, next_hub.lon
        )
        
        # Calculate travel parameters
        use_three_phase, cruise_speed, accel_time, cruise_time, decel_time, total_time = \
            self.calculate_travel_parameters(distance_m)
        
        # Calculate number of samples
        num_samples = int(self.sample_rate_hz * total_time)
        messages = []
        
        for i in range(num_samples):
            t = i / self.sample_rate_hz  # Current time in seconds
            
            # Determine current phase and calculate forward acceleration
            if use_three_phase:
                if t < accel_time:
                    # Acceleration phase
                    forward_accel = self.acceleration
                    current_speed = self.acceleration * t
                elif t < accel_time + cruise_time:
                    # Cruise phase
                    forward_accel = 0.0
                    current_speed = cruise_speed
                else:
                    # Deceleration phase
                    time_in_decel = t - (accel_time + cruise_time)
                    forward_accel = -self.deceleration
                    current_speed = cruise_speed - self.deceleration * time_in_decel
            else:
                # Triangular velocity profile
                if t < accel_time:
                    # Acceleration phase
                    forward_accel = self.acceleration
                    current_speed = self.acceleration * t
                else:
                    # Deceleration phase
                    time_in_decel = t - accel_time
                    forward_accel = -self.deceleration
                    current_speed = cruise_speed - self.deceleration * time_in_decel
            
            # Get wave motion (pitch, roll, yaw)
            pitch, roll, yaw = self.get_wave_motion(t)
            
            # Calculate accelerations in boat's local frame
            # Forward acceleration (x-axis)
            accel_x = forward_accel
            
            # Lateral acceleration from roll (y-axis)
            # Roll causes lateral component of gravity
            accel_y = self.gravity * math.sin(roll)
            
            # Vertical acceleration (z-axis)
            # Gravity component + pitch effect
            accel_z = self.gravity * math.cos(pitch) * math.cos(roll)
            
            # Gyroscope readings (angular velocities)
            # Roll rate (x-axis rotation)
            gyro_x = 2 * math.pi * self.roll_amplitude / self.wave_period * \
                     -math.sin(2 * math.pi * t / self.wave_period + math.pi/4)
            
            # Pitch rate (y-axis rotation)
            gyro_y = 2 * math.pi * self.pitch_amplitude / self.wave_period * \
                     math.cos(2 * math.pi * t / self.wave_period)
            
            # Yaw rate (z-axis rotation)
            gyro_z = 2 * math.pi * self.yaw_amplitude / (self.wave_period * 1.5) * \
                     math.cos(2 * math.pi * t / (self.wave_period * 1.5))
            
            # # Global frame (commented out)
            # # Convert to global frame: forward = north-east direction
            # # Calculate bearing from current_hub to next_hub
            # lat1_rad = math.radians(current_hub.lat)
            # lat2_rad = math.radians(next_hub.lat)
            # dlon = math.radians(next_hub.lon - current_hub.lon)
            # bearing = math.atan2(
            #     math.sin(dlon) * math.cos(lat2_rad),
            #     math.cos(lat1_rad) * math.sin(lat2_rad) - 
            #     math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(dlon)
            # )
            # # Rotate local frame to global frame
            # accel_north = accel_x * math.cos(bearing) - accel_y * math.sin(bearing)
            # accel_east = accel_x * math.sin(bearing) + accel_y * math.cos(bearing)
            # accel_up = accel_z
            
            messages.append({
                "accel_x": accel_x,
                "accel_y": accel_y,
                "accel_z": accel_z,
                "gyro_x": gyro_x,
                "gyro_y": gyro_y,
                "gyro_z": gyro_z,
            })
        
        return messages