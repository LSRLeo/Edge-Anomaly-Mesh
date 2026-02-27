class Hub:
    def __init__(self, hub_id, name, lat, lon, altitude, time_at_hub, mode,
                 radius, hub_type,
                 lift_time=0, label=None ):
        self.hub_id = hub_id
        self.name = name
        self.lat = lat
        self.lon = lon
        self.radius_m = radius
        self.hub_type = hub_type  # avoid clobbering built-in 'type'

        # IMPORTANT: Node expects .alt
        self.alt = altitude

        # your old behavior fields
        self.time_at_hub = time_at_hub
        self.mode = mode
        self.lift_time = lift_time
        self.label = label