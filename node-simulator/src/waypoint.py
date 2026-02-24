
class Waypoint:
    def __init__(self, name, lat, lon, alt, time_at_hub, lift_time, mode):
        self.name = name
        self.lat = lat
        self.lon = lon
        self.alt = alt

        # kept for uniform JSON shape / compatibility
        self.time_at_hub = time_at_hub
        self.lift_time = lift_time

        # waypoints usually won't define this directly
        self.mode = mode