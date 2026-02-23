
from src.waypoint import Waypoint   

class Hub(Waypoint):
    def __init__(self, name, lat, lon, alt, time_at_hub, mode, lift_time):
        super().__init__(name, lat, lon, alt)
        self.time_at_hub = time_at_hub
        self.mode = mode
        self.lift_time = lift_time
