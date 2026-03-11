import math, random
from typing import List, Tuple

from src.hub import Hub
from src.waypoint import Waypoint



class BezierCurve:
    def __init__(self, p0: Tuple[float, float], p1: Tuple[float, float],
                 p2: Tuple[float, float], p3: Tuple[float, float]):
        self.p0, self.p1, self.p2, self.p3 = p0, p1, p2, p3

    def evaluate(self, t: float) -> Tuple[float, float]:
        t = max(0.0, min(1.0, t))
        mt = 1 - t

        x = (mt**3 * self.p0[0] +
             3 * mt**2 * t * self.p1[0] +
             3 * mt * t**2 * self.p2[0] +
             t**3 * self.p3[0])

        y = (mt**3 * self.p0[1] +
             3 * mt**2 * t * self.p1[1] +
             3 * mt * t**2 * self.p2[1] +
             t**3 * self.p3[1])

        return (x, y)

    def generate_points(self, num_points: int) -> List[Tuple[float, float]]:
        if num_points <= 1:
            return [self.evaluate(0.0)]
        return [self.evaluate(i / (num_points - 1)) for i in range(num_points)]


class WaypointMaker:
    """
    One-stop 'Hub -> Hub -> list[Waypoint]' generator.
    Uses a Bezier curve for lat/lon and interpolates altitude.
    """

    def __init__(self, num_waypoints: int = 10):#default 10 points
        if num_waypoints < 2:
            raise ValueError("num_waypoints must be >= 2")
        self.num_waypoints = num_waypoints

    def make(self, from_hub: Hub, to_hub: Hub, route_type: str) -> List[Waypoint]:
        start = (from_hub.lat, from_hub.lon)
        end = (to_hub.lat, to_hub.lon)

        c1, c2 = self._control_points(start, end, route_type)
        curve = BezierCurve(start, c1, c2, end)
        latlon_points = curve.generate_points(self.num_waypoints)

        # IMPORTANT: match your Hub attribute name:
        # you used hub.alt in your Hub class
        start_alt = from_hub.alt
        end_alt = to_hub.alt

        waypoints: List[Waypoint] = []
        n = len(latlon_points)

        for i, (lat, lon) in enumerate(latlon_points):
            progress = i / (n - 1) if n > 1 else 0.0

            base_alt = start_alt + (end_alt - start_alt) * progress

            if route_type == "terrestrial":
                alt_variation = math.sin(progress * math.pi * 3) * 50
                altitude = base_alt + alt_variation + random.gauss(0, 5)
            else:
                altitude = base_alt + random.gauss(0, 2)

            # IMPORTANT: match your Waypoint constructor:
            # earlier you had Waypoint(lat, lon, alt, progress)
            waypoints.append(Waypoint(
                lat=round(lat, 6),
                lon=round(lon, 6),
                alt=round(altitude, 1),
                progress=progress,
                hub_id=from_hub.hub_id
            ))

        return waypoints

    def _control_points(
        self,
        start: Tuple[float, float],
        end: Tuple[float, float],
        route_type: str
    ) -> Tuple[Tuple[float, float], Tuple[float, float]]:
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        length = math.sqrt(dx * dx + dy * dy)

        if length == 0:
            return (start, end)

        perp_x = -dy / length
        perp_y = dx / length

        if route_type == "terrestrial":
            offset = length * random.uniform(0.1, 0.2)
        elif route_type == "maritime":
            offset = length * random.uniform(0.03, 0.08)
        else:
            offset = length * random.uniform(0.05, 0.1)

        direction = random.choice([-1, 1])

        c1 = (
            start[0] + dx * 0.33 + perp_x * offset * direction,
            start[1] + dy * 0.33 + perp_y * offset * direction
        )
        c2 = (
            start[0] + dx * 0.67 + perp_x * offset * direction * 0.7,
            start[1] + dy * 0.67 + perp_y * offset * direction * 0.7
        )

        return c1, c2