import time
import json
import math
from datetime import datetime, timedelta

from lift import Lift
from maritime import Maritime
# from terrestrial import Terrestrial
from idle import Idle

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
        except FileNotFoundError:
            raise FileNotFoundError(f"Node configuration file {node_file} not found")
        except json.JSONDecodeError:
            raise ValueError(f"Error decoding node configuration file {node_file}")
    
    def generate(self):
        for i in range(len(self.route.hubs)):
            if i < len(self.route.hubs) - 1:
                current_hub = self.route.hubs[i]
                next_hub = self.route.hubs[i + 1]

                idleResults = self.idle.generate_reading(current_hub)
                self.messages += self.add_metadata(idleResults, "IDLE", current_hub, current_hub)
                
                if current_hub.mode == "lift":
                    self.lift.set_hub(current_hub.lat, current_hub.lon, 20)
                    liftResults = self.lift.generate_reading(current_hub.lift_time)
                    self.messages += self.add_metadata(liftResults, "LIFT", current_hub, next_hub)
                elif current_hub.mode == "maritime":
                    maritimeResults = self.maritime.generate_reading(current_hub, next_hub)
                    self.messages += self.add_metadata(maritimeResults, "MARITIME", current_hub, next_hub)
                elif current_hub.mode == "terrestrial":
                    pass
                #     self.messages += Terrestrial.generate_reading(current_hub, next_hub, self.sample_rate_hz)
                else:
                    raise ValueError(f"Invalid mode: {current_hub.mode}")
            else:
                current_hub = self.route.hubs[i]
                idleResults = self.idle.generate_reading(current_hub)
                self.messages += self.add_metadata(idleResults, "IDLE", current_hub, current_hub)

    def calculate_gps(self, current_hub, next_hub, mode, message_index, total_messages):
        if mode == "IDLE":
            return {
                "lat_deg": current_hub.lat,
                "lon_deg": current_hub.lon,
                "altitude_m": current_hub.alt
            }
        elif mode in ["LIFT", "MARITIME", "TERRESTRIAL"]:
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
    
    def add_metadata(self, messages, mode, current_hub, next_hub):
        polished_messages = []
        total_messages = len(messages)
        for message_index, message in enumerate(messages):
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