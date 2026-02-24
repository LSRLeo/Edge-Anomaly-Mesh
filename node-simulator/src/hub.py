from src.waypoint import Waypoint

class Hub(Waypoint):
    def __init__(self, name, lat, lon, alt=0, time_at_hub=0, mode="idle", lift_time=0):
        super().__init__(
            name=name,
            lat=lat,
            lon=lon,
            alt=alt,
            time_at_hub=time_at_hub,
            lift_time=lift_time,
            mode=mode
        )