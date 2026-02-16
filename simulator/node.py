import time
import json
import math
from datetime import datetime, timedelta

from lift import Lift
from maritime import Maritime
from terrestrial import Terrestrial
from idle import Idle
from noise import apply_idle_node_noise, apply_lift_node_noise, apply_maritime_node_noise, apply_terrestrial_node_noise

class Node:
    def __init__(self, node_file, route):
        self.route = route
        self.origin = route.hubs[0]
        self.destination = route.hubs[-1]
        self.messages = []

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
            self.gravity = 9.81  # m/s²

        except FileNotFoundError:
            raise FileNotFoundError(f"Node configuration file {node_file} not found")
        except json.JSONDecodeError:
            raise ValueError(f"Error decoding node configuration file {node_file}")
    
    def generate(self):
        for i in range(len(self.route.hubs)):
            if i < len(self.route.hubs) - 1:
                current_hub = self.route.hubs[i]
                next_hub = self.route.hubs[i + 1]

                # Generate idle readings and apply noise 
                idleResults = self.idle.generate_reading(current_hub)
                idleResults_noisy = [apply_idle_node_noise(message) for message in idleResults]
                self.messages += self.add_metadata(idleResults_noisy, "IDLE", current_hub, current_hub)

                if current_hub.mode == "lift":
                    self.lift.set_hub(current_hub.lat, current_hub.lon, 20)
                    liftResults = self.lift.generate_reading(current_hub, current_hub.lift_time)
                    liftResults_noisy = [apply_lift_node_noise(message) for message in liftResults]
                    self.messages += self.add_metadata(liftResults_noisy, "LIFT", current_hub, next_hub)
                elif current_hub.mode == "maritime":
                    maritimeResults = self.maritime.generate_reading(current_hub, next_hub)
                    maritimeResults_noisy = [apply_maritime_node_noise(message) for message in maritimeResults]
                    self.messages += self.add_metadata(maritimeResults_noisy, "MARITIME", current_hub, next_hub)
                elif current_hub.mode == "terrestrial":
                    terrestrialResults = self.terrestrial.generate_reading(current_hub, next_hub, self.sample_rate_hz)
                    terrestrialResults_noisy = [apply_terrestrial_node_noise(message) for message in terrestrialResults]
                    self.messages += self.add_metadata(terrestrialResults_noisy, "TERRESTRIAL", current_hub, next_hub)
                else:
                    raise ValueError(f"Invalid mode: {current_hub.mode}")
            else:
                current_hub = self.route.hubs[i]
                idleResults = self.idle.generate_reading(current_hub)
                idleResults_noisy = [apply_idle_node_noise(message) for message in idleResults]
                self.messages += self.add_metadata(idleResults_noisy, "IDLE", current_hub, current_hub)

    def calculate_gps(self, current_hub, next_hub, mode, message_index, total_messages, accel_x=0.0, accel_y=0.0, accel_z=0.0):
        if mode == "IDLE":
            return {
                "lat_deg": current_hub.lat,
                "lon_deg": current_hub.lon,
                "altitude_m": current_hub.alt
            }
        elif mode == "LIFT":
            # Calculate GPS from accelerations for LIFT mode
            return self._calculate_gps_from_accel(current_hub, accel_x, accel_y, accel_z)
        elif mode in ["MARITIME", "TERRESTRIAL"]:
            if total_messages == 0:
                progress = 0.0
            else:
                progress = message_index / total_messages
            
            lat = current_hub.lat + (next_hub.lat - current_hub.lat) * progress
            lon = current_hub.lon + (next_hub.lon - current_hub.lon) * progress
            alt = current_hub.alt + (next_hub.alt - current_hub.alt) * progress
            
            return {
                "lat_deg": lat,
                "lon_deg": lon,
                "altitude_m": alt
            }
        else:
            return {
                "lat_deg": current_hub.lat,
                "lon_deg": current_hub.lon,
                "altitude_m": current_hub.alt
            }
    
    def _calculate_gps_from_accel(self, start_hub, accel_x, accel_y, accel_z):
        # Reset state if this is the first message in a LIFT sequence
        if self.lift_start_hub is None or (self.lift_start_hub.lat != start_hub.lat or 
                                           self.lift_start_hub.lon != start_hub.lon):
            self.lift_start_hub = start_hub
            self.lift_velocity = {"x": 0.0, "y": 0.0, "z": 0.0}
            self.lift_position = {"x": 0.0, "y": 0.0, "z": 0.0}
        
        # Time step in seconds
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
        # Earth's radius in meters
        R = 6371000.0
        
        # Convert meters to degrees
        # 1 degree latitude ≈ 111,000 meters
        # 1 degree longitude ≈ 111,000 * cos(latitude) meters
        lat_offset = self.lift_position["y"] / 111000.0  # Assuming y is North-South
        lon_offset = self.lift_position["x"] / (111000.0 * math.cos(math.radians(start_hub.lat)))  # Assuming x is East-West
        
        # Calculate new GPS coordinates
        new_lat = start_hub.lat + lat_offset
        new_lon = start_hub.lon + lon_offset
        new_alt = start_hub.alt + self.lift_position["z"]  # z is vertical (altitude)
        
        return {
            "lat_deg": new_lat,
            "lon_deg": new_lon,
            "altitude_m": new_alt
        }
    
    def add_metadata(self, messages, mode, current_hub, next_hub):
        polished_messages = []
        total_messages = len(messages)
        
        # Reset LIFT state tracking when starting a new LIFT sequence
        if mode == "LIFT":
            self.lift_start_hub = None
        
        for message_index, message in enumerate(messages):
            # For LIFT mode, pass accelerations to calculate GPS from them
            if mode == "LIFT":
                gps = self.calculate_gps(
                    current_hub, next_hub, mode, message_index, total_messages,
                    accel_x=message['accel_x'],
                    accel_y=message['accel_y'],
                    accel_z=message['accel_z']
                )
            else:
                gps = self.calculate_gps(current_hub, next_hub, mode, message_index, total_messages)
            
            polished_message = {
                "m_type": "raw-data",
                "m_id": f"{self.node_id}_{self.seq}",
                "event_id": f"{self.node_id}_{self.timestamp.isoformat()}",
                "node_id": self.node_id,
                "timestamp": self.timestamp.isoformat(),
                "seq": self.seq,
                "gps": gps,
                "accel_mss": {
                    "x": message['accel_x'],
                    "y": message['accel_y'],
                    "z": message['accel_z']
                },
                "gyro_rads": {
                    "x": message['gyro_x'],
                    "y": message['gyro_y'],
                    "z": message['gyro_z']
                },
                "meta": {
                    "sample_rate_hz": self.sample_rate_hz,
                    "battery_pct": 95,
                    "sim_mode": mode,
                    "sim_anomaly": False
                },
                "origin": {
                    "lat_deg": self.origin.lat,
                    "lon_deg": self.origin.lon,
                    "altitude_m": self.origin.alt
                },
                "dest": {
                    "lat_deg": self.destination.lat,
                    "lon_deg": self.destination.lon,
                    "altitude_m": self.destination.alt
                }
            }
            self.seq += 1
            self.timestamp += timedelta(1 / self.sample_rate_hz)
            polished_messages.append(polished_message)
        return polished_messages
            
    def publish(self):
        with open('raw_data.json', 'w') as f:
            json.dump(self.messages, f, indent=2)