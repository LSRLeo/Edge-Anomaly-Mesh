

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
        self.running_state = 0 # 1 = running, 2 = paused, 0 = stopped
    
    def generate_message(self):
        pass

    def start(self):
        pass
    
    def stop(self):
        pass
    
    def pause(self):
        pass

    
#         node_id, gps_lat, gps_lon, gps_altitude_m, sample_rate_hz, battery_pct, mode
# Implement generate_message() that returns the flat JSON structure
# Add sequence number tracking (seq increments each message)
# Add start(), stop(), pause() controls