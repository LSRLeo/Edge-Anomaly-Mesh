from src.hub import Hub
from src.waypoint import Waypoint

class Segment:
    def __init__(self, start: Hub, end: Hub, mode: str, points:list[Waypoint]):
        self.start = start
        self.end = end
        self.mode = mode
        self.points = points

    def is_motion(self) -> bool:
        return self.mode.upper() not in {"IDLE", "LIFT"}