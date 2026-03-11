class Waypoint:
    def __init__(self,lat, lon, alt, progress, hub_id):
        self.lat = lat
        self.hub_id = hub_id
        self.lon = lon
        self.alt = alt
        self.progress = progress