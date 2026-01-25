from generators import Idle, Lift, Maritime, Terrestrial
import time
import json

class Node:
    def __init__(self, node_id: str, mode: str):
        self.node_id = node_id
        self.gps_lat = 0
        self.gps_lon = 0
        self.gps_altitude_m = 0
        self.sample_rate_hz = 50
        self.battery_pct = 100
        self.mode = "IDLE"
        self.seq = 0
        # self.running_state = 0 # 1 = running, 2 = paused, 0 = stopped
    
    def generate_message(self) -> json:
        if self.mode == "IDLE":
            readings = Idle.generate_reading()
        elif self.mode == "LIFT":
            readings = Lift.generate_reading()
        elif self.mode == "MARITIME":
            readings = Maritime.generate_reading()
        elif self.mode == "TERRESTRIAL":
            readings = Terrestrial.generate_reading()
        else:
            raise ValueError(f"Invalid mode: {self.mode}")
        
        return json.dump({            
            "node_id": self.node_id,
            "timestamp": time.time(),
            "seq": self.seq,
            "gps_lat": self.gps_lat,
            "gps_lon": self.gps_lon,
            "gps_altitude_m": self.gps_altitude_m,
            "accel_x": readings.accel_x,
            "accel_y": readings.accel_y,
            "accel_z": readings.accel_z,
            "gyro_x": readings.gyro_x,
            "gyro_y": readings.gyro_y,
            "gyro_z": readings.gyro_z,
            "sample_rate_hz": self.sample_rate_hz,
            "battery_pct": self.battery_pct,
            "mode": self.mode
        })



    # def start(self):
    #     self.running_state = 1
    
    # def stop(self):
    #     self.running_state = 0
    #     self.seq = 0
    
    # def pause(self):
    #     self.running_state = 2

    
#         node_id, gps_lat, gps_lon, gps_altitude_m, sample_rate_hz, battery_pct, mode
# Implement generate_message() that returns the flat JSON structure
# Add sequence number tracking (seq increments each message)
# Add start(), stop(), pause() controls