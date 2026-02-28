import time
import json
import math
from datetime import datetime, timedelta

from src.lift import Lift
from src.maritime import Maritime
from src.terrestrial import Terrestrial
from src.idle import Idle
from src.hub import Hub
from src.waypoint import Waypoint
from src.noise import apply_idle_node_noise, apply_lift_node_noise, apply_maritime_node_noise, apply_terrestrial_node_noise

class Node:
    def __init__(self, node_file, route, data_mode):
        self.route = route
        self.origin = route.points[0]
        self.destination = route.points[-1]
        self.messages = []
        self.data_mode = data_mode

        #segment information for calculating progress 
        self.segments = self.route.segments

        try:
            with open(node_file, 'r') as f:
                node_config = json.load(f)

            self.node_id = node_config['node_id']
            self.sample_rate_hz = node_config['sample_rate_hz']
            self.seq = 0
            self.timestamp = datetime.now()
            self.idle = Idle(self.sample_rate_hz)
            self.lift = Lift(self.sample_rate_hz)
            self.maritime = Maritime(self.sample_rate_hz)
            self.terrestrial = Terrestrial(self.sample_rate_hz)

            self.lift_velocity = {"x": 0.0, "y": 0.0, "z": 0.0}  # m/s
            self.lift_position = {"x": 0.0, "y": 0.0, "z": 0.0}  # meters relative to start
            self.lift_start_hub = None
            
            # Velocity and position tracking for terrestrial and maritime
            self.terrestrial_velocity = {"north": 0.0, "east": 0.0, "up": 0.0}  # m/s in global frame
            self.terrestrial_position = {"north": 0.0, "east": 0.0, "up": 0.0}  # meters relative to start
            self.terrestrial_start_hub = None
            self.terrestrial_bearing = None  # bearing from start to destination
            
            self.maritime_velocity = {"north": 0.0, "east": 0.0, "up": 0.0}  # m/s in global frame
            self.maritime_position = {"north": 0.0, "east": 0.0, "up": 0.0}  # meters relative to start
            self.maritime_start_hub = None
            self.maritime_bearing = None  # bearing from start to destination
            
            self.gravity = 9.81  # m/s²

        except FileNotFoundError:
            raise FileNotFoundError(f"Node configuration file {node_file} not found")
        except json.JSONDecodeError:
            raise ValueError(f"Error decoding node configuration file {node_file}")
    
    def generate(self):
        recent_hub_mode = None

        for i in range(len(self.route.points)):
            if i < len(self.route.points) - 1:
                current_point = self.route.points[i]
                next_point = self.route.points[i + 1]

                # Update mode if the current point has one (waypoints may carry terrestrial/maritime;
                # hubs are guaranteed to be "hub" or "lift")
                if hasattr(current_point, "mode"):
                    recent_hub_mode = current_point.mode.lower()

                # HUB: always emit IDLE, then optional LIFT
                if isinstance(current_point, Hub):
                    idleResults = self.idle.generate_reading(current_point)
                    idleResults_noisy = [apply_idle_node_noise(m) for m in idleResults]
                    self.messages += self.add_metadata(idleResults_noisy, "IDLE", current_point, current_point)

                    if recent_hub_mode == "lift" and current_point.lift_time > 0:
                        self.lift.set_hub(current_point.lat, current_point.lon, 20)
                        liftResults = self.lift.generate_reading(current_point, current_point.lift_time)
                        liftResults_noisy = [apply_lift_node_noise(m) for m in liftResults]
                        self.messages += self.add_metadata(liftResults_noisy, "LIFT", current_point, current_point)

                # TRANSIT: only generate when we're not at a hub
                if not isinstance(current_point, Hub):
                    if recent_hub_mode == "maritime":
                        maritimeResults = self.maritime.generate_reading(current_point, next_point)
                        maritimeResults_noisy = [apply_maritime_node_noise(m) for m in maritimeResults]
                        self.messages += self.add_metadata(maritimeResults_noisy, "MARITIME", current_point, next_point)

                    elif recent_hub_mode == "terrestrial":
                        terrestrialResults = self.terrestrial.generate_reading(current_point, next_point, self.sample_rate_hz)
                        terrestrialResults_noisy = [apply_terrestrial_node_noise(m) for m in terrestrialResults]
                        self.messages += self.add_metadata(terrestrialResults_noisy, "TERRESTRIAL", current_point, next_point)

                    else:
                        raise ValueError(f"Invalid mode: {recent_hub_mode}")

            else:
                # Final point: ending IDLE at destination hub
                current_point = self.route.points[i]
                idleResults = self.idle.generate_reading(current_point)
                idleResults_noisy = [apply_idle_node_noise(m) for m in idleResults]
                self.messages += self.add_metadata(idleResults_noisy, "IDLE", current_point, current_point)
    def calculate_gps(self, current_point, next_point, mode, message_index, total_messages, accel_x=0.0, accel_y=0.0, accel_z=0.0):
        if mode == "IDLE":
            return {
                "lat": current_point.lat,
                "lon": current_point.lon,
                "altitude_m": current_point.alt
            }
        elif mode == "LIFT":
            # Calculate GPS from accelerations for LIFT mode
            return self._calculate_gps_from_accel_lift(current_point, accel_x, accel_y, accel_z)
        elif mode == "TERRESTRIAL":
            # Calculate GPS from accelerations for TERRESTRIAL mode
            return self._calculate_gps_from_accel_terrestrial(current_point, next_point, accel_x, accel_y, accel_z)
        elif mode == "MARITIME":
            # Calculate GPS from accelerations for MARITIME mode
            return self._calculate_gps_from_accel_maritime(current_point, next_point, accel_x, accel_y, accel_z)
        else:
            return {
                "lat": current_point.lat,
                "lon": current_point.lon,
                "altitude_m": current_point.alt
            }
    
    def _calculate_bearing(self, start_hub, end_hub):
        """
        Calculate bearing from start_hub to end_hub in radians.
        Returns bearing in radians (0 = North, π/2 = East, etc.)
        """
        lat1_rad = math.radians(start_hub.lat)
        lat2_rad = math.radians(end_hub.lat)
        dlon = math.radians(end_hub.lon - start_hub.lon)
        
        y = math.sin(dlon) * math.cos(lat2_rad)
        x = math.cos(lat1_rad) * math.sin(lat2_rad) - math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(dlon)
        
        bearing = math.atan2(y, x)
        return bearing
    
    def _calculate_gps_from_accel_lift(self, start_hub, accel_x, accel_y, accel_z):
        """
        Calculate GPS from accelerations for LIFT mode.
        LIFT uses local frame: x, y, z relative to starting position.
        """
        # Reset state if this is the first message in a LIFT sequence
        if self.lift_start_hub is None or (self.lift_start_hub.lat != start_hub.lat or 
                                           self.lift_start_hub.lon != start_hub.lon):
            self.lift_start_hub = start_hub
            self.lift_velocity = {"x": 0.0, "y": 0.0, "z": 0.0}
            self.lift_position = {"x": 0.0, "y": 0.0, "z": 0.0}
        
        # Time step in seconds (works for any sample rate, including < 1 Hz)
        dt = 1.0 / self.sample_rate_hz
        
        # Calculate net vertical acceleration (subtract gravity since accel_z includes it)
        # If accel_z > gravity, we're accelerating upward
        # If accel_z < gravity, we're accelerating downward
        net_accel_z = accel_z - self.gravity
        
        # Update velocity using Euler integration: v = v0 + a * dt
        self.lift_velocity["x"] += accel_x * dt
        self.lift_velocity["y"] += accel_y * dt
        self.lift_velocity["z"] += net_accel_z * dt
        
        # Update position using Euler integration: p = p0 + v * dt
        self.lift_position["x"] += self.lift_velocity["x"] * dt
        self.lift_position["y"] += self.lift_velocity["y"] * dt
        self.lift_position["z"] += self.lift_velocity["z"] * dt
        
        # Convert displacement in meters to GPS coordinates
        # 1 degree latitude ≈ 111,000 meters
        # 1 degree longitude ≈ 111,000 * cos(latitude) meters
        lat_offset = self.lift_position["y"] / 111000.0  # Assuming y is North-South
        lon_offset = self.lift_position["x"] / (111000.0 * math.cos(math.radians(start_hub.lat)))  # Assuming x is East-West
        
        # Calculate new GPS coordinates
        new_lat = start_hub.lat + lat_offset
        new_lon = start_hub.lon + lon_offset
        new_alt = start_hub.alt + self.lift_position["z"]  # z is vertical (altitude)
        
        return {
            "lat": new_lat,
            "lon": new_lon,
            "altitude_m": new_alt
        }
    
    def _calculate_gps_from_accel_terrestrial(self, start_hub, end_hub, accel_x, accel_y, accel_z):
        """
        Calculate GPS from accelerations for TERRESTRIAL mode.
        Terrestrial uses local frame: x=forward (toward destination), y=lateral, z=up.
        We need to convert to global frame (North/East/Up) based on bearing.
        """
        # Reset state if this is the first message in a TERRESTRIAL sequence
        if (self.terrestrial_start_hub is None or 
            self.terrestrial_start_hub.lat != start_hub.lat or 
            self.terrestrial_start_hub.lon != start_hub.lon):
            self.terrestrial_start_hub = start_hub
            self.terrestrial_velocity = {"north": 0.0, "east": 0.0, "up": 0.0}
            self.terrestrial_position = {"north": 0.0, "east": 0.0, "up": 0.0}
            self.terrestrial_bearing = self._calculate_bearing(start_hub, end_hub)
        
        # Time step in seconds (works for any sample rate, including < 1 Hz)
        dt = 1.0 / self.sample_rate_hz
        
        # Convert local frame accelerations to global frame (North/East/Up)
        # Local: x = forward (along bearing), y = lateral (perpendicular), z = up
        # Global: north, east, up
        bearing = self.terrestrial_bearing
        accel_north = accel_x * math.cos(bearing) - accel_y * math.sin(bearing)
        accel_east = accel_x * math.sin(bearing) + accel_y * math.cos(bearing)
        # For z, subtract gravity to get net vertical acceleration
        accel_up = accel_z - self.gravity
        
        # Update velocity using Euler integration: v = v0 + a * dt
        self.terrestrial_velocity["north"] += accel_north * dt
        self.terrestrial_velocity["east"] += accel_east * dt
        self.terrestrial_velocity["up"] += accel_up * dt
        
        # Update position using Euler integration: p = p0 + v * dt
        self.terrestrial_position["north"] += self.terrestrial_velocity["north"] * dt
        self.terrestrial_position["east"] += self.terrestrial_velocity["east"] * dt
        self.terrestrial_position["up"] += self.terrestrial_velocity["up"] * dt
        
        # Convert displacement in meters to GPS coordinates
        # 1 degree latitude ≈ 111,000 meters
        # 1 degree longitude ≈ 111,000 * cos(latitude) meters
        lat_offset = self.terrestrial_position["north"] / 111000.0
        lon_offset = self.terrestrial_position["east"] / (111000.0 * math.cos(math.radians(start_hub.lat)))
        
        # Calculate new GPS coordinates
        new_lat = start_hub.lat + lat_offset
        new_lon = start_hub.lon + lon_offset
        new_alt = start_hub.alt + self.terrestrial_position["up"]
        
        return {
            "lat": new_lat,
            "lon": new_lon,
            "altitude_m": new_alt
        }
    
    def _calculate_gps_from_accel_maritime(self, start_hub, end_hub, accel_x, accel_y, accel_z):
        """
        Calculate GPS from accelerations for MARITIME mode.
        Maritime uses local frame: x=forward (toward destination), y=starboard, z=up.
        We need to convert to global frame (North/East/Up) based on bearing.
        """
        # Reset state if this is the first message in a MARITIME sequence
        if (self.maritime_start_hub is None or 
            self.maritime_start_hub.lat != start_hub.lat or 
            self.maritime_start_hub.lon != start_hub.lon):
            self.maritime_start_hub = start_hub
            self.maritime_velocity = {"north": 0.0, "east": 0.0, "up": 0.0}
            self.maritime_position = {"north": 0.0, "east": 0.0, "up": 0.0}
            self.maritime_bearing = self._calculate_bearing(start_hub, end_hub)
        
        # Time step in seconds (works for any sample rate, including < 1 Hz)
        dt = 1.0 / self.sample_rate_hz
        
        # Convert local frame accelerations to global frame (North/East/Up)
        # Local: x = forward (along bearing), y = starboard (perpendicular), z = up
        # Global: north, east, up
        bearing = self.maritime_bearing
        accel_north = accel_x * math.cos(bearing) - accel_y * math.sin(bearing)
        accel_east = accel_x * math.sin(bearing) + accel_y * math.cos(bearing)
        # For z, subtract gravity to get net vertical acceleration
        accel_up = accel_z - self.gravity
        
        # Update velocity using Euler integration: v = v0 + a * dt
        self.maritime_velocity["north"] += accel_north * dt
        self.maritime_velocity["east"] += accel_east * dt
        self.maritime_velocity["up"] += accel_up * dt
        
        # Update position using Euler integration: p = p0 + v * dt
        self.maritime_position["north"] += self.maritime_velocity["north"] * dt
        self.maritime_position["east"] += self.maritime_velocity["east"] * dt
        self.maritime_position["up"] += self.maritime_velocity["up"] * dt
        
        # Convert displacement in meters to GPS coordinates
        # 1 degree latitude ≈ 111,000 meters
        # 1 degree longitude ≈ 111,000 * cos(latitude) meters
        lat_offset = self.maritime_position["north"] / 111000.0
        lon_offset = self.maritime_position["east"] / (111000.0 * math.cos(math.radians(start_hub.lat)))
        
        # Calculate new GPS coordinates
        new_lat = start_hub.lat + lat_offset
        new_lon = start_hub.lon + lon_offset
        new_alt = start_hub.alt + self.maritime_position["up"]
        
        return {
            "lat": new_lat,
            "lon": new_lon,
            "altitude_m": new_alt
        }
    
    def add_metadata(self, messages, mode, current_point, next_point):
        polished_messages = []
        total_messages = len(messages)
        
        # Reset state tracking when starting a new sequence
        if mode == "LIFT":
            self.lift_start_hub = None
        elif mode == "TERRESTRIAL":
            self.terrestrial_start_hub = None
        elif mode == "MARITIME":
            self.maritime_start_hub = None
        
        for message_index, message in enumerate(messages):
            # For LIFT, TERRESTRIAL, and MARITIME modes, pass accelerations to calculate GPS from them
            if mode in ["LIFT", "TERRESTRIAL", "MARITIME"]:
                gps = self.calculate_gps(
                    current_point, next_point, mode, message_index, total_messages,
                    accel_x=message['accel_x'],
                    accel_y=message['accel_y'],
                    accel_z=message['accel_z']
                )
            else:
                gps = self.calculate_gps(current_point, next_point, mode, message_index, total_messages)
            

            # Update label with segment information
            if isinstance(current_point, Hub):
                label_seg_or_hub = "location"
                seq_or_hub = current_point.hub_id
                mode = "IDLE"

            elif isinstance(current_point, Waypoint):
                label_seg_or_hub = "segment_progress"
                seq_or_hub = round(message_index / (total_messages - 1), 3) if total_messages > 1 else 0.0

            if self.data_mode == "live":
                
                label = {
                    "motion_type": mode,
                    "is_anomaly": "",
                    "anomaly_type": "",
                    label_seg_or_hub: seq_or_hub
                }
            else:
                # NOTE: This is where we will add the anomaly label
                label = {
                    "motion_type": mode,
                    "is_anomaly": False,
                    "anomaly_type": "impact",
                    label_seg_or_hub: seq_or_hub
                }
            
            

            polished_message = {
                "node_id": self.node_id,
                "timestamp": self.timestamp.isoformat(),
                "seq": self.seq,
                "gps": gps,
                "accel": {
                    "x": message['accel_x'],
                    "y": message['accel_y'],
                    "z": message['accel_z']
                },
                "gyro": {
                    "x": message['gyro_x'],
                    "y": message['gyro_y'],
                    "z": message['gyro_z']
                },
                "label": label
            }
            self.seq += 1
            self.timestamp += timedelta(1 / self.sample_rate_hz)
            polished_messages.append(polished_message)
        return polished_messages
            
    def publish(self):
        with open('raw_data.json', 'w') as f:
            json.dump(self.messages, f, indent=2)