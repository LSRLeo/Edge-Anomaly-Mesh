class Hub:
    def __init__(self, name, lat, lon, alt, time_at_hub, mode, lift_time = 0, label = None):
        self.name = name
        self.lat = lat
        self.lon = lon
        self.alt = alt
        #only need for Idle class
        self.time_at_hub = time_at_hub
        self.mode = mode
        self.lift_time = lift_time
        self.label = label