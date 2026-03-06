#!/usr/bin/env python3
"""
Training Data Generator for Edge-Anomaly-Mesh ML Module

Generates labeled sensor data for multi-state journeys between hubs.
Uses BFS pathfinding and Bezier curve interpolation for realistic paths.

Output format matches actual simulator format:
{
  "m_type": "raw-data",
  "m_id": "node_001_8",
  "event_id": "node_001_2026-02-12T21:19:19.000000",
  "node_id": "node_001",
  "timestamp": "2026-02-12T21:19:19.000000",
  "seq": 8,
  "gps": {"lat_deg": 39.673702, "lon_deg": -104.961197, "altitude_m": 1657.4},
  "accel_mss": {"x": 0.363, "y": 0.301, "z": 9.287},
  "gyro_rads": {"x": -0.0565, "y": -0.1307, "z": -0.0242},
  "meta": {"motion_type": "IDLE", "is_anomaly": "False", "anomaly_type": "", "location": "hub_denver_01"}
}

Usage:
    python data/generate_training_data.py --output data/training --samples 500
"""

import json
import os
import math
import random
from collections import deque
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import argparse

# Constants
GRAVITY = 9.81
SAMPLE_RATE_HZ = 1  # 1Hz based on actual data (1 second intervals)


class MotionType(Enum):
    IDLE = "IDLE"
    TERRESTRIAL = "TERRESTRIAL"
    MARITIME = "MARITIME"
    LIFT = "LIFT"


class AnomalyType(Enum):
    NONE = "none"
    SPIKE = "spike"
    DROPOUT = "dropout"
    DRIFT = "drift"
    MOTION_MISMATCH = "motion_mismatch"


@dataclass
class Hub:
    """Represents a hub/location in the network."""
    hub_id: str
    name: str
    lat: float
    lon: float
    altitude_m: float
    radius_m: float
    hub_type: str


@dataclass
class Route:
    """Represents a route between two hubs."""
    route_id: str
    from_hub: str
    to_hub: str
    route_type: str
    motion_type: str
    distance_km: float
    typical_duration_hours: float
    bidirectional: bool
    description: str


@dataclass
class Waypoint:
    """A point along an interpolated path."""
    lat: float
    lon: float
    altitude_m: float
    progress: float  # 0.0 to 1.0


@dataclass
class JourneySegment:
    """A segment of a multi-hub journey."""
    from_hub_id: str
    to_hub_id: str
    motion_type: str
    waypoints: List[Waypoint]
    duration_seconds: int
    samples: List[Dict] = field(default_factory=list)


class HubNetwork:
    """Manages the hub network and pathfinding."""

    def __init__(self, config_path: str):
        self.hubs: Dict[str, Hub] = {}
        self.routes: Dict[str, Route] = {}
        self.adjacency: Dict[str, List[str]] = {}
        self._load_config(config_path)

    def _load_config(self, config_path: str) -> None:
        """Load hub configuration from JSON."""
        with open(config_path, 'r') as f:
            config = json.load(f)

        # Load hubs
        for hub_data in config.get('hubs', []):
            hub = Hub(
                hub_id=hub_data['hub_id'],
                name=hub_data['name'],
                lat=hub_data['lat'],
                lon=hub_data['lon'],
                altitude_m=hub_data['altitude_m'],
                radius_m=hub_data['radius_m'],
                hub_type=hub_data['type']
            )
            self.hubs[hub.hub_id] = hub

        # Load routes
        for route_data in config.get('routes', []):
            route = Route(
                route_id=route_data['route_id'],
                from_hub=route_data['from_hub'],
                to_hub=route_data['to_hub'],
                route_type=route_data['route_type'],
                motion_type=route_data['motion_type'],
                distance_km=route_data['distance_km'],
                typical_duration_hours=route_data['typical_duration_hours'],
                bidirectional=route_data.get('bidirectional', True),
                description=route_data.get('description', '')
            )
            self.routes[route.route_id] = route

        # Load or build adjacency
        if 'adjacency' in config:
            self.adjacency = config['adjacency']
        else:
            self._build_adjacency()

    def _build_adjacency(self) -> None:
        """Build adjacency list from routes."""
        for route in self.routes.values():
            if route.from_hub not in self.adjacency:
                self.adjacency[route.from_hub] = []
            if route.to_hub not in self.adjacency[route.from_hub]:
                self.adjacency[route.from_hub].append(route.to_hub)

            if route.bidirectional:
                if route.to_hub not in self.adjacency:
                    self.adjacency[route.to_hub] = []
                if route.from_hub not in self.adjacency[route.to_hub]:
                    self.adjacency[route.to_hub].append(route.from_hub)

    def find_path(self, from_hub: str, to_hub: str) -> Optional[List[str]]:
        """Find shortest path between hubs using BFS."""
        if from_hub not in self.hubs or to_hub not in self.hubs:
            return None
        if from_hub == to_hub:
            return [from_hub]

        visited = {from_hub}
        queue = deque([(from_hub, [from_hub])])

        while queue:
            current, path = queue.popleft()

            for neighbor in self.adjacency.get(current, []):
                if neighbor == to_hub:
                    return path + [neighbor]
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))

        return None

    def get_route(self, from_hub: str, to_hub: str) -> Optional[Route]:
        """Get route between two directly connected hubs."""
        for route in self.routes.values():
            if route.from_hub == from_hub and route.to_hub == to_hub:
                return route
            if route.bidirectional and route.from_hub == to_hub and route.to_hub == from_hub:
                return route
        return None

    def get_hub(self, hub_id: str) -> Optional[Hub]:
        """Get hub by ID."""
        return self.hubs.get(hub_id)


class BezierCurve:
    """Cubic Bezier curve for path interpolation."""

    def __init__(self, p0: Tuple[float, float], p1: Tuple[float, float],
                 p2: Tuple[float, float], p3: Tuple[float, float]):
        """
        Initialize with 4 control points.
        p0: Start point
        p1: First control point
        p2: Second control point
        p3: End point
        """
        self.p0 = p0
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3

    def evaluate(self, t: float) -> Tuple[float, float]:
        """Evaluate curve at parameter t [0, 1]."""
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
        """Generate evenly spaced points along the curve."""
        return [self.evaluate(i / (num_points - 1)) for i in range(num_points)]


class PathInterpolator:
    """Generates realistic waypoints between hubs using Bezier curves."""

    def __init__(self, num_waypoints: int = 10):
        self.num_waypoints = num_waypoints

    def interpolate(self, from_hub: Hub, to_hub: Hub, route_type: str) -> List[Waypoint]:
        """Generate waypoints between two hubs."""
        start = (from_hub.lat, from_hub.lon)
        end = (to_hub.lat, to_hub.lon)

        # Calculate control points based on route type
        control_points = self._generate_control_points(start, end, route_type)

        # Create Bezier curve
        curve = BezierCurve(start, control_points[0], control_points[1], end)

        # Generate waypoints
        points = curve.generate_points(self.num_waypoints)

        # Interpolate altitude
        start_alt = from_hub.altitude_m
        end_alt = to_hub.altitude_m

        waypoints = []
        for i, (lat, lon) in enumerate(points):
            progress = i / (len(points) - 1) if len(points) > 1 else 0

            # Altitude with some variation for mountain roads
            base_alt = start_alt + (end_alt - start_alt) * progress
            if route_type == "ROAD":
                # Add elevation variation for mountain roads
                alt_variation = math.sin(progress * math.pi * 3) * 50  # Up to 50m variation
                altitude = base_alt + alt_variation + random.gauss(0, 5)
            else:
                altitude = base_alt + random.gauss(0, 2)

            waypoints.append(Waypoint(
                lat=round(lat, 6),
                lon=round(lon, 6),
                altitude_m=round(altitude, 1),
                progress=progress
            ))

        return waypoints

    def _generate_control_points(
        self,
        start: Tuple[float, float],
        end: Tuple[float, float],
        route_type: str
    ) -> Tuple[Tuple[float, float], Tuple[float, float]]:
        """Generate control points for Bezier curve based on route type."""
        mid_lat = (start[0] + end[0]) / 2
        mid_lon = (start[1] + end[1]) / 2

        # Calculate perpendicular offset
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        length = math.sqrt(dx**2 + dy**2)

        if length == 0:
            return (start, end)

        # Perpendicular unit vector
        perp_x = -dy / length
        perp_y = dx / length

        # Offset magnitude based on route type
        if route_type == "ROAD":
            # Roads curve more (following terrain)
            offset = length * random.uniform(0.1, 0.2)
        elif route_type == "SEA":
            # Shipping lanes are more direct
            offset = length * random.uniform(0.03, 0.08)
        else:
            # Default minimal curve
            offset = length * random.uniform(0.05, 0.1)

        # Random direction for curve
        direction = random.choice([-1, 1])

        # Control points offset from midpoint
        ctrl1 = (
            start[0] + dx * 0.33 + perp_x * offset * direction,
            start[1] + dy * 0.33 + perp_y * offset * direction
        )
        ctrl2 = (
            start[0] + dx * 0.67 + perp_x * offset * direction * 0.7,
            start[1] + dy * 0.67 + perp_y * offset * direction * 0.7
        )

        return (ctrl1, ctrl2)


class MotionPhysics:
    """Physics models for each motion type."""

    @staticmethod
    def idle() -> Tuple[Dict, Dict]:
        """Stationary: gravity on Z, minimal noise."""
        accel = {
            "x": round(random.gauss(0, 0.05), 3),
            "y": round(random.gauss(0, 0.05), 3),
            "z": round(random.gauss(GRAVITY, 0.1), 3)
        }
        gyro = {
            "x": round(random.gauss(0, 0.01), 4),
            "y": round(random.gauss(0, 0.01), 4),
            "z": round(random.gauss(0, 0.01), 4)
        }
        return accel, gyro

    @staticmethod
    def terrestrial(t: float, speed_kmh: float = 60, road_quality: float = 0.8) -> Tuple[Dict, Dict]:
        """
        Road transport: sinusoidal vibration + random bumps.

        Args:
            t: Time in seconds
            speed_kmh: Vehicle speed
            road_quality: 0.0 (rough) to 1.0 (smooth)
        """
        freq = 3.0 + random.uniform(-0.5, 0.5)  # 2.5-3.5 Hz
        roughness = 1.0 - road_quality * 0.5

        amp_x = 0.35 * (speed_kmh / 60) * roughness
        amp_y = 0.25 * (speed_kmh / 60) * roughness
        amp_z = 0.12 * (speed_kmh / 60) * roughness

        # Base vibration with phase offsets
        accel_x = amp_x * math.sin(2 * math.pi * freq * t) + random.gauss(0, 0.1 * roughness)
        accel_y = amp_y * math.sin(2 * math.pi * freq * t + math.pi/4) + random.gauss(0, 0.08 * roughness)
        accel_z = GRAVITY + amp_z * math.sin(2 * math.pi * freq * t + math.pi/2) + random.gauss(0, 0.05)

        # Random bump (5% chance on rough roads)
        if random.random() < 0.05 * roughness:
            bump = random.uniform(1.5, 3.0)
            accel_z += bump * random.choice([-1, 1])
            accel_x += bump * 0.3 * random.choice([-1, 1])

        # Add secondary harmonics for realism
        accel_x += 0.1 * amp_x * math.sin(2 * math.pi * freq * 2 * t)
        accel_y += 0.08 * amp_y * math.sin(2 * math.pi * freq * 2 * t + math.pi/6)

        accel = {
            "x": round(accel_x, 3),
            "y": round(accel_y, 3),
            "z": round(accel_z, 3)
        }

        # Gyro correlated with body rotation
        gyro = {
            "x": round(accel["y"] * 0.08 + random.gauss(0, 0.02), 4),
            "y": round(accel["x"] * 0.06 + random.gauss(0, 0.02), 4),
            "z": round(random.gauss(0, 0.01), 4)
        }

        return accel, gyro

    @staticmethod
    def maritime(t: float, sea_state: int = 4) -> Tuple[Dict, Dict]:
        """
        Ship transport: multi-frequency wave motion.

        Args:
            t: Time in seconds
            sea_state: 1-9 (Beaufort scale simplified)
        """
        frequencies = [0.7, 1.3, 2.1, 3.2]
        amplitudes = [0.3, 0.2, 0.15, 0.1]

        # Scale by sea state
        scale = 0.3 + (sea_state / 4) * 0.7

        accel_x, accel_y, accel_z = 0.0, 0.0, GRAVITY

        # Superimpose multiple wave frequencies
        for i, (freq, amp) in enumerate(zip(frequencies, amplitudes)):
            phase = i * math.pi / 3  # Fixed phase offset per frequency
            accel_x += amp * scale * math.sin(2 * math.pi * freq * t + phase)
            accel_y += amp * scale * math.sin(2 * math.pi * freq * t + phase + math.pi/3)
            accel_z += amp * scale * 0.5 * math.sin(2 * math.pi * freq * t + phase + 2*math.pi/3)

        # Random wave spike (5% chance in rough seas)
        if random.random() < 0.05 * (sea_state / 5):
            spike = random.uniform(0.5, 1.5) * scale
            axis = random.choice(["x", "y", "z"])
            if axis == "x":
                accel_x += spike * random.choice([-1, 1])
            elif axis == "y":
                accel_y += spike * random.choice([-1, 1])
            else:
                accel_z += spike * random.choice([-1, 1])

        # Add chaotic noise (more than terrestrial)
        accel_x += random.gauss(0, 0.15 * scale)
        accel_y += random.gauss(0, 0.15 * scale)
        accel_z += random.gauss(0, 0.1 * scale)

        accel = {
            "x": round(accel_x, 3),
            "y": round(accel_y, 3),
            "z": round(accel_z, 3)
        }

        gyro = {
            "x": round(accel["y"] * 0.1 + random.gauss(0, 0.05), 4),
            "y": round(accel["x"] * 0.1 + random.gauss(0, 0.05), 4),
            "z": round(random.gauss(0, 0.03), 4)
        }

        return accel, gyro

    @staticmethod
    def lift(t: float, cycle_duration: float = 8.0) -> Tuple[Dict, Dict]:
        """
        Forklift: 4-phase cycle with vertical acceleration.

        Phases:
        - LIFT_UP (0-15%): Accelerating upward
        - HOLD_MOVE (15-50%): Moving horizontally at height
        - LOWER_DOWN (50-65%): Decelerating downward
        - REST (65-100%): Stationary
        """
        cycle_pos = (t % cycle_duration) / cycle_duration
        lift_accel = 3.5

        if cycle_pos < 0.15:  # LIFT_UP
            progress = cycle_pos / 0.15
            # Smooth acceleration curve
            z_accel = GRAVITY + lift_accel * math.sin(progress * math.pi / 2)
            xy_noise = 0.2
            phase = "LIFT_UP"
        elif cycle_pos < 0.50:  # HOLD_MOVE
            z_accel = GRAVITY
            xy_noise = 0.15
            # Add some horizontal movement
            move_progress = (cycle_pos - 0.15) / 0.35
            phase = "HOLD_MOVE"
        elif cycle_pos < 0.65:  # LOWER_DOWN
            progress = (cycle_pos - 0.50) / 0.15
            # Smooth deceleration
            z_accel = GRAVITY - lift_accel * math.sin(progress * math.pi / 2)
            xy_noise = 0.2
            phase = "LOWER_DOWN"
        else:  # REST
            z_accel = GRAVITY
            xy_noise = 0.05
            phase = "REST"

        # Add forklift engine vibration (~10-15 Hz)
        if phase != "REST":
            engine_vib = 0.1 * math.sin(2 * math.pi * 12 * t)
        else:
            engine_vib = 0

        accel = {
            "x": round(random.gauss(0, xy_noise) + engine_vib, 3),
            "y": round(random.gauss(0, xy_noise) + engine_vib * 0.8, 3),
            "z": round(z_accel + random.gauss(0, 0.1), 3)
        }

        gyro = {
            "x": round(random.gauss(0, 0.02), 4),
            "y": round(random.gauss(0, 0.02), 4),
            "z": round(random.gauss(0, 0.01), 4)
        }

        return accel, gyro

    @staticmethod
    def generate(motion_type: str, t: float, **kwargs) -> Tuple[Dict, Dict]:
        """Generate sensor readings for a given motion type."""
        if motion_type == "IDLE":
            return MotionPhysics.idle()
        elif motion_type == "TERRESTRIAL":
            return MotionPhysics.terrestrial(t, **kwargs)
        elif motion_type == "MARITIME":
            return MotionPhysics.maritime(t, **kwargs)
        elif motion_type == "LIFT":
            return MotionPhysics.lift(t, **kwargs)
        else:
            return MotionPhysics.idle()


class AnomalyInjector:
    """Injects anomalies into sensor readings."""

    @staticmethod
    def inject_spike(accel: Dict, magnitude: float = 5.0) -> Dict:
        """Sudden acceleration spike (impact/drop)."""
        accel = accel.copy()
        axis = random.choice(["x", "y", "z"])
        accel[axis] = round(accel[axis] + magnitude * random.choice([-1, 1]), 3)
        return accel

    @staticmethod
    def inject_dropout(accel: Dict) -> Dict:
        """Lost gravity signal (sensor failure)."""
        return {
            "x": round(random.gauss(0, 0.1), 3),
            "y": round(random.gauss(0, 0.1), 3),
            "z": round(random.gauss(0, 0.1), 3)
        }

    @staticmethod
    def inject_drift(accel: Dict, drift_amount: float = 1.5) -> Dict:
        """Sensor calibration drift."""
        accel = accel.copy()
        axis = random.choice(["x", "y", "z"])
        accel[axis] = round(accel[axis] + drift_amount, 3)
        return accel

    @staticmethod
    def inject_motion_mismatch(t: float, expected_type: str) -> Tuple[Dict, Dict]:
        """Generate wrong physics for the labeled motion type."""
        wrong_types = [mt.value for mt in MotionType if mt.value != expected_type]
        wrong_type = random.choice(wrong_types)
        return MotionPhysics.generate(wrong_type, t)


class TrainingDataGenerator:
    """Generates labeled training data for ML model."""

    def __init__(self, config_path: str):
        self.network = HubNetwork(config_path)
        self.interpolator = PathInterpolator(num_waypoints=10)

    def generate_journey(
        self,
        from_hub: str,
        to_hub: str,
        node_id: str = "node_001",
        samples_per_segment: int = 500,
        include_dwell: bool = True,
        dwell_duration: int = 30,
        include_lift: bool = False,
        lift_duration: int = 40,
        anomaly_rate: float = 0.0,
        anomaly_type: Optional[str] = None
    ) -> Tuple[List[Dict], Dict]:
        """
        Generate training data for a journey between two hubs.

        Args:
            from_hub: Starting hub ID
            to_hub: Destination hub ID
            node_id: Node identifier
            samples_per_segment: Number of transit samples per segment
            include_dwell: Whether to include IDLE time at hubs
            dwell_duration: Duration of IDLE time in seconds
            include_lift: Whether to include LIFT operations at hubs
            lift_duration: Duration of LIFT operations in seconds
            anomaly_rate: Rate of anomaly injection (0.0-1.0)
            anomaly_type: Type of anomaly to inject

        Returns:
            (samples, metadata)
        """
        # Find path using BFS
        path = self.network.find_path(from_hub, to_hub)
        if not path:
            raise ValueError(f"No path found from {from_hub} to {to_hub}")

        all_samples = []
        segments_info = []
        start_time = datetime.now()
        seq = 0

        # Generate samples for each segment
        for i in range(len(path) - 1):
            segment_from = path[i]
            segment_to = path[i + 1]

            from_hub_obj = self.network.get_hub(segment_from)
            to_hub_obj = self.network.get_hub(segment_to)
            route = self.network.get_route(segment_from, segment_to)

            if not from_hub_obj or not to_hub_obj:
                continue

            motion_type = route.motion_type if route else "TERRESTRIAL"

            # Generate waypoints using Bezier curve
            waypoints = self.interpolator.interpolate(
                from_hub_obj, to_hub_obj,
                route.route_type if route else "ROAD"
            )

            # Add dwell at start hub (IDLE)
            if include_dwell and i == 0:
                dwell_samples, seq = self._generate_dwell_samples(
                    from_hub_obj, node_id, start_time, seq, dwell_duration
                )
                all_samples.extend(dwell_samples)
                start_time += timedelta(seconds=dwell_duration)

            # Add LIFT at start hub (loading)
            if include_lift and i == 0:
                lift_samples, seq = self._generate_lift_samples(
                    from_hub_obj, node_id, start_time, seq, lift_duration,
                    anomaly_rate, anomaly_type
                )
                all_samples.extend(lift_samples)
                segments_info.append({
                    "from_hub": segment_from,
                    "to_hub": segment_from,
                    "motion_type": "LIFT",
                    "num_samples": len(lift_samples),
                    "operation": "loading"
                })
                start_time += timedelta(seconds=lift_duration)

            # Generate transit samples
            transit_samples, seq = self._generate_transit_samples(
                waypoints, motion_type, node_id, start_time, seq,
                samples_per_segment, anomaly_rate, anomaly_type
            )
            all_samples.extend(transit_samples)

            segments_info.append({
                "from_hub": segment_from,
                "to_hub": segment_to,
                "motion_type": motion_type,
                "num_samples": len(transit_samples)
            })

            start_time += timedelta(seconds=samples_per_segment)

            # Add LIFT at destination hub (unloading)
            if include_lift:
                lift_samples, seq = self._generate_lift_samples(
                    to_hub_obj, node_id, start_time, seq, lift_duration,
                    anomaly_rate, anomaly_type
                )
                all_samples.extend(lift_samples)
                segments_info.append({
                    "from_hub": segment_to,
                    "to_hub": segment_to,
                    "motion_type": "LIFT",
                    "num_samples": len(lift_samples),
                    "operation": "unloading"
                })
                start_time += timedelta(seconds=lift_duration)

            # Add dwell at intermediate hubs
            if include_dwell and i < len(path) - 2:
                dwell_samples, seq = self._generate_dwell_samples(
                    to_hub_obj, node_id, start_time, seq, dwell_duration
                )
                all_samples.extend(dwell_samples)
                start_time += timedelta(seconds=dwell_duration)

        # Final dwell at destination
        if include_dwell:
            dest_hub = self.network.get_hub(path[-1])
            if dest_hub:
                dwell_samples, seq = self._generate_dwell_samples(
                    dest_hub, node_id, start_time, seq, dwell_duration
                )
                all_samples.extend(dwell_samples)

        metadata = {
            "journey_id": f"journey_{node_id}_{from_hub}_{to_hub}",
            "from_hub": from_hub,
            "to_hub": to_hub,
            "path": path,
            "segments": segments_info,
            "total_samples": len(all_samples),
            "anomaly_rate": anomaly_rate,
            "anomaly_type": anomaly_type,
            "include_lift": include_lift
        }

        return all_samples, metadata

    def _generate_dwell_samples(
        self,
        hub: Hub,
        node_id: str,
        start_time: datetime,
        start_seq: int,
        duration: int
    ) -> Tuple[List[Dict], int]:
        """Generate IDLE samples at a hub."""
        samples = []

        for i in range(duration):
            seq = start_seq + i
            timestamp = (start_time + timedelta(seconds=i)).isoformat()
            accel, gyro = MotionPhysics.idle()

            sample = {
                "m_type": "raw-data",
                "m_id": f"{node_id}_{seq}",
                "event_id": f"{node_id}_{timestamp}",
                "node_id": node_id,
                "timestamp": timestamp,
                "seq": seq,
                "gps": {
                    "lat_deg": round(hub.lat + random.gauss(0, 0.000001), 6),
                    "lon_deg": round(hub.lon + random.gauss(0, 0.000001), 6),
                    "altitude_m": round(hub.altitude_m + random.gauss(0, 0.5), 1)
                },
                "accel_mss": accel,
                "gyro_rads": gyro,
                "meta": {
                    "motion_type": "IDLE",
                    "is_anomaly": "False",
                    "anomaly_type": "",
                    "location": hub.hub_id
                }
            }
            samples.append(sample)

        return samples, start_seq + duration

    def _generate_lift_samples(
        self,
        hub: Hub,
        node_id: str,
        start_time: datetime,
        start_seq: int,
        duration: int,
        anomaly_rate: float = 0.0,
        anomaly_type: Optional[str] = None
    ) -> Tuple[List[Dict], int]:
        """Generate LIFT samples at a hub (forklift loading/unloading)."""
        samples = []

        for i in range(duration):
            seq = start_seq + i
            timestamp = (start_time + timedelta(seconds=i)).isoformat()
            t = i  # Time in seconds
            accel, gyro = MotionPhysics.lift(t)

            # Maybe inject anomaly
            is_anomaly = random.random() < anomaly_rate
            current_anomaly = ""

            if is_anomaly and anomaly_type:
                current_anomaly = anomaly_type
                if anomaly_type == "spike":
                    accel = AnomalyInjector.inject_spike(accel)
                elif anomaly_type == "dropout":
                    accel = AnomalyInjector.inject_dropout(accel)
                elif anomaly_type == "drift":
                    accel = AnomalyInjector.inject_drift(accel)
                elif anomaly_type == "motion_mismatch":
                    accel, gyro = AnomalyInjector.inject_motion_mismatch(t, "LIFT")

            sample = {
                "m_type": "raw-data",
                "m_id": f"{node_id}_{seq}",
                "event_id": f"{node_id}_{timestamp}",
                "node_id": node_id,
                "timestamp": timestamp,
                "seq": seq,
                "gps": {
                    "lat_deg": round(hub.lat + random.gauss(0, 0.000005), 6),
                    "lon_deg": round(hub.lon + random.gauss(0, 0.000005), 6),
                    "altitude_m": round(hub.altitude_m + random.gauss(0, 1.0), 1)
                },
                "accel_mss": accel,
                "gyro_rads": gyro,
                "meta": {
                    "motion_type": "LIFT",
                    "is_anomaly": str(is_anomaly),
                    "anomaly_type": current_anomaly,
                    "location": hub.hub_id
                }
            }
            samples.append(sample)

        return samples, start_seq + duration

    def _generate_transit_samples(
        self,
        waypoints: List[Waypoint],
        motion_type: str,
        node_id: str,
        start_time: datetime,
        start_seq: int,
        num_samples: int,
        anomaly_rate: float = 0.0,
        anomaly_type: Optional[str] = None
    ) -> Tuple[List[Dict], int]:
        """Generate samples along a transit path."""
        samples = []

        for i in range(num_samples):
            # Calculate progress and interpolate position
            progress = i / (num_samples - 1) if num_samples > 1 else 0

            # Find surrounding waypoints
            wp_index = progress * (len(waypoints) - 1)
            wp_lower = int(wp_index)
            wp_upper = min(wp_lower + 1, len(waypoints) - 1)
            wp_frac = wp_index - wp_lower

            # Interpolate between waypoints
            wp1, wp2 = waypoints[wp_lower], waypoints[wp_upper]
            lat = wp1.lat + (wp2.lat - wp1.lat) * wp_frac
            lon = wp1.lon + (wp2.lon - wp1.lon) * wp_frac
            alt = wp1.altitude_m + (wp2.altitude_m - wp1.altitude_m) * wp_frac

            seq = start_seq + i
            timestamp = (start_time + timedelta(seconds=i)).isoformat()

            # Generate sensor data
            t = i  # Time in seconds
            accel, gyro = MotionPhysics.generate(motion_type, t)

            # Maybe inject anomaly
            is_anomaly = random.random() < anomaly_rate
            current_anomaly = ""

            if is_anomaly and anomaly_type:
                current_anomaly = anomaly_type
                if anomaly_type == "spike":
                    accel = AnomalyInjector.inject_spike(accel)
                elif anomaly_type == "dropout":
                    accel = AnomalyInjector.inject_dropout(accel)
                elif anomaly_type == "drift":
                    accel = AnomalyInjector.inject_drift(accel)
                elif anomaly_type == "motion_mismatch":
                    accel, gyro = AnomalyInjector.inject_motion_mismatch(t, motion_type)

            sample = {
                "m_type": "raw-data",
                "m_id": f"{node_id}_{seq}",
                "event_id": f"{node_id}_{timestamp}",
                "node_id": node_id,
                "timestamp": timestamp,
                "seq": seq,
                "gps": {
                    "lat_deg": round(lat + random.gauss(0, 0.000005), 6),
                    "lon_deg": round(lon + random.gauss(0, 0.000005), 6),
                    "altitude_m": round(alt + random.gauss(0, 2), 1)
                },
                "accel_mss": accel,
                "gyro_rads": gyro,
                "meta": {
                    "motion_type": motion_type,
                    "is_anomaly": str(is_anomaly),
                    "anomaly_type": current_anomaly,
                    "location": ""
                }
            }
            samples.append(sample)

        return samples, start_seq + num_samples

    def generate_all_routes(
        self,
        output_dir: str,
        samples_per_segment: int = 500,
        anomaly_rate: float = 0.6,
        include_lift_variants: bool = True,
        include_maritime: bool = True
    ) -> Dict[str, Any]:
        """Generate training data for all possible routes between hubs."""
        os.makedirs(output_dir, exist_ok=True)

        hub_ids = list(self.network.hubs.keys())
        all_metadata = {
            "generated_at": datetime.now().isoformat(),
            "hubs": hub_ids,
            "routes": [],
            "total_samples": 0
        }

        route_count = 0

        # Separate hubs by type for different route generation
        terrestrial_hubs = [h for h in hub_ids if not h.startswith("hub_") or "port" not in h]
        maritime_hubs = [h for h in hub_ids if "port" in h]

        # Filter to actual hub types based on routes
        terrestrial_hubs = []
        maritime_hubs = []
        for hub_id in hub_ids:
            hub = self.network.get_hub(hub_id)
            if hub and hub.hub_type == "seaport":
                maritime_hubs.append(hub_id)
            else:
                terrestrial_hubs.append(hub_id)

        # Generate TERRESTRIAL routes (Colorado hubs)
        for from_hub in terrestrial_hubs:
            for to_hub in terrestrial_hubs:
                if from_hub == to_hub:
                    continue

                path = self.network.find_path(from_hub, to_hub)
                if not path:
                    continue

                route_count += 1
                node_id = f"node_{route_count:03d}"

                # Generate normal TERRESTRIAL samples (no LIFT)
                samples, metadata = self.generate_journey(
                    from_hub=from_hub,
                    to_hub=to_hub,
                    node_id=node_id,
                    samples_per_segment=samples_per_segment,
                    anomaly_rate=0.0,
                    include_lift=False
                )

                filename = f"route_{from_hub}_to_{to_hub}.json"
                filepath = os.path.join(output_dir, filename)

                with open(filepath, 'w') as f:
                    json.dump(samples, f, indent=2)

                all_metadata["routes"].append({
                    "file": filename,
                    **metadata
                })
                all_metadata["total_samples"] += len(samples)

                # Generate anomaly samples
                for anomaly_type in ["spike", "dropout", "drift", "motion_mismatch"]:
                    anomaly_samples, anomaly_metadata = self.generate_journey(
                        from_hub=from_hub,
                        to_hub=to_hub,
                        node_id=f"{node_id}_anomaly",
                        samples_per_segment=samples_per_segment,
                        anomaly_rate=anomaly_rate,
                        anomaly_type=anomaly_type,
                        include_lift=False
                    )

                    anomaly_filename = f"route_{from_hub}_to_{to_hub}_{anomaly_type}.json"
                    anomaly_filepath = os.path.join(output_dir, anomaly_filename)

                    with open(anomaly_filepath, 'w') as f:
                        json.dump(anomaly_samples, f, indent=2)

                    all_metadata["routes"].append({
                        "file": anomaly_filename,
                        **anomaly_metadata
                    })
                    all_metadata["total_samples"] += len(anomaly_samples)

                # Generate TERRESTRIAL + LIFT routes
                if include_lift_variants:
                    route_count += 1
                    lift_node_id = f"node_{route_count:03d}"

                    lift_samples, lift_metadata = self.generate_journey(
                        from_hub=from_hub,
                        to_hub=to_hub,
                        node_id=lift_node_id,
                        samples_per_segment=samples_per_segment,
                        anomaly_rate=0.0,
                        include_lift=True
                    )

                    lift_filename = f"route_{from_hub}_to_{to_hub}_with_lift.json"
                    lift_filepath = os.path.join(output_dir, lift_filename)

                    with open(lift_filepath, 'w') as f:
                        json.dump(lift_samples, f, indent=2)

                    all_metadata["routes"].append({
                        "file": lift_filename,
                        **lift_metadata
                    })
                    all_metadata["total_samples"] += len(lift_samples)

                    # Anomaly variants for LIFT routes
                    for anomaly_type in ["spike", "dropout", "drift", "motion_mismatch"]:
                        anomaly_samples, anomaly_metadata = self.generate_journey(
                            from_hub=from_hub,
                            to_hub=to_hub,
                            node_id=f"{lift_node_id}_anomaly",
                            samples_per_segment=samples_per_segment,
                            anomaly_rate=anomaly_rate,
                            anomaly_type=anomaly_type,
                            include_lift=True
                        )

                        anomaly_filename = f"route_{from_hub}_to_{to_hub}_with_lift_{anomaly_type}.json"
                        anomaly_filepath = os.path.join(output_dir, anomaly_filename)

                        with open(anomaly_filepath, 'w') as f:
                            json.dump(anomaly_samples, f, indent=2)

                        all_metadata["routes"].append({
                            "file": anomaly_filename,
                            **anomaly_metadata
                        })
                        all_metadata["total_samples"] += len(anomaly_samples)

        # Generate MARITIME routes (port hubs)
        if include_maritime and maritime_hubs:
            for from_hub in maritime_hubs:
                for to_hub in maritime_hubs:
                    if from_hub == to_hub:
                        continue

                    path = self.network.find_path(from_hub, to_hub)
                    if not path:
                        continue

                    route_count += 1
                    node_id = f"node_{route_count:03d}"

                    # Generate MARITIME samples (no LIFT)
                    samples, metadata = self.generate_journey(
                        from_hub=from_hub,
                        to_hub=to_hub,
                        node_id=node_id,
                        samples_per_segment=samples_per_segment,
                        anomaly_rate=0.0,
                        include_lift=False
                    )

                    filename = f"route_{from_hub}_to_{to_hub}_maritime.json"
                    filepath = os.path.join(output_dir, filename)

                    with open(filepath, 'w') as f:
                        json.dump(samples, f, indent=2)

                    all_metadata["routes"].append({
                        "file": filename,
                        **metadata
                    })
                    all_metadata["total_samples"] += len(samples)

                    # Generate anomaly samples for MARITIME
                    for anomaly_type in ["spike", "dropout", "drift", "motion_mismatch"]:
                        anomaly_samples, anomaly_metadata = self.generate_journey(
                            from_hub=from_hub,
                            to_hub=to_hub,
                            node_id=f"{node_id}_anomaly",
                            samples_per_segment=samples_per_segment,
                            anomaly_rate=anomaly_rate,
                            anomaly_type=anomaly_type,
                            include_lift=False
                        )

                        anomaly_filename = f"route_{from_hub}_to_{to_hub}_maritime_{anomaly_type}.json"
                        anomaly_filepath = os.path.join(output_dir, anomaly_filename)

                        with open(anomaly_filepath, 'w') as f:
                            json.dump(anomaly_samples, f, indent=2)

                        all_metadata["routes"].append({
                            "file": anomaly_filename,
                            **anomaly_metadata
                        })
                        all_metadata["total_samples"] += len(anomaly_samples)

                    # Generate MARITIME + LIFT routes
                    if include_lift_variants:
                        route_count += 1
                        lift_node_id = f"node_{route_count:03d}"

                        lift_samples, lift_metadata = self.generate_journey(
                            from_hub=from_hub,
                            to_hub=to_hub,
                            node_id=lift_node_id,
                            samples_per_segment=samples_per_segment,
                            anomaly_rate=0.0,
                            include_lift=True
                        )

                        lift_filename = f"route_{from_hub}_to_{to_hub}_maritime_with_lift.json"
                        lift_filepath = os.path.join(output_dir, lift_filename)

                        with open(lift_filepath, 'w') as f:
                            json.dump(lift_samples, f, indent=2)

                        all_metadata["routes"].append({
                            "file": lift_filename,
                            **lift_metadata
                        })
                        all_metadata["total_samples"] += len(lift_samples)

                        # Anomaly variants for MARITIME + LIFT
                        for anomaly_type in ["spike", "dropout", "drift", "motion_mismatch"]:
                            anomaly_samples, anomaly_metadata = self.generate_journey(
                                from_hub=from_hub,
                                to_hub=to_hub,
                                node_id=f"{lift_node_id}_anomaly",
                                samples_per_segment=samples_per_segment,
                                anomaly_rate=anomaly_rate,
                                anomaly_type=anomaly_type,
                                include_lift=True
                            )

                            anomaly_filename = f"route_{from_hub}_to_{to_hub}_maritime_with_lift_{anomaly_type}.json"
                            anomaly_filepath = os.path.join(output_dir, anomaly_filename)

                            with open(anomaly_filepath, 'w') as f:
                                json.dump(anomaly_samples, f, indent=2)

                            all_metadata["routes"].append({
                                "file": anomaly_filename,
                                **anomaly_metadata
                            })
                            all_metadata["total_samples"] += len(anomaly_samples)

        # Write metadata
        metadata_path = os.path.join(output_dir, "metadata.json")
        with open(metadata_path, 'w') as f:
            json.dump(all_metadata, f, indent=2)

        return all_metadata


    def generate_balanced_dataset(
        self,
        output_dir: str,
        samples_per_class: int = 500,
    ) -> Dict[str, Any]:
        """
        Generate a balanced dataset with exactly samples_per_class samples for each of
        the 8 classes: IDLE, TERRESTRIAL, MARITIME, LIFT × (normal, anomaly).

        Each class is written to its own file so the ML loader sees equal representation.
        Anomaly samples randomly cycle through all 4 anomaly types.
        """
        os.makedirs(output_dir, exist_ok=True)

        hub_ids = list(self.network.hubs.keys())
        terrestrial_hub = next(
            (self.network.get_hub(h) for h in hub_ids
             if self.network.get_hub(h).hub_type != "seaport"),
            self.network.get_hub(hub_ids[0])
        )
        maritime_hub = next(
            (self.network.get_hub(h) for h in hub_ids
             if self.network.get_hub(h).hub_type == "seaport"),
            terrestrial_hub
        )

        start_time = datetime.now()
        anomaly_types = ["spike", "dropout", "drift", "motion_mismatch"]

        classes = [
            ("IDLE",         False),
            ("TERRESTRIAL",  False),
            ("MARITIME",     False),
            ("LIFT",         False),
            ("IDLE",         True),
            ("TERRESTRIAL",  True),
            ("MARITIME",     True),
            ("LIFT",         True),
        ]

        all_metadata = {
            "generated_at": start_time.isoformat(),
            "mode": "balanced",
            "samples_per_class": samples_per_class,
            "files": [],
            "total_samples": 0
        }

        for idx, (motion_type, is_anomaly_class) in enumerate(classes):
            samples = []
            hub = maritime_hub if motion_type == "MARITIME" else terrestrial_hub
            node_id = f"node_{idx + 1:03d}"

            for i in range(samples_per_class):
                t = float(i)
                timestamp = (start_time + timedelta(seconds=i)).isoformat()
                accel, gyro = MotionPhysics.generate(motion_type, t)

                anomaly_type_used = ""
                if is_anomaly_class:
                    anomaly_type_used = anomaly_types[i % len(anomaly_types)]
                    if anomaly_type_used == "spike":
                        accel = AnomalyInjector.inject_spike(accel)
                    elif anomaly_type_used == "dropout":
                        accel = AnomalyInjector.inject_dropout(accel)
                    elif anomaly_type_used == "drift":
                        accel = AnomalyInjector.inject_drift(accel)
                    elif anomaly_type_used == "motion_mismatch":
                        accel, gyro = AnomalyInjector.inject_motion_mismatch(t, motion_type)

                sample = {
                    "m_type": "raw-data",
                    "m_id": f"{node_id}_{i}",
                    "event_id": f"{node_id}_{timestamp}",
                    "node_id": node_id,
                    "timestamp": timestamp,
                    "seq": i,
                    "gps": {
                        "lat_deg": round(hub.lat + random.gauss(0, 0.0001), 6),
                        "lon_deg": round(hub.lon + random.gauss(0, 0.0001), 6),
                        "altitude_m": round(hub.altitude_m + random.gauss(0, 2.0), 1)
                    },
                    "accel_mss": accel,
                    "gyro_rads": gyro,
                    "meta": {
                        "motion_type": motion_type,
                        "is_anomaly": str(is_anomaly_class),
                        "anomaly_type": anomaly_type_used,
                        "location": hub.hub_id
                    }
                }
                samples.append(sample)

            suffix = "anomaly" if is_anomaly_class else "normal"
            filename = f"balanced_{motion_type.lower()}_{suffix}.json"
            filepath = os.path.join(output_dir, filename)

            with open(filepath, 'w') as f:
                json.dump(samples, f, indent=2)

            label = f"{motion_type}_ANOM" if is_anomaly_class else motion_type
            print(f"  [{label:<20s}] {samples_per_class} samples -> {filename}")

            all_metadata["files"].append({
                "file": filename,
                "motion_type": motion_type,
                "is_anomaly": is_anomaly_class,
                "num_samples": len(samples)
            })
            all_metadata["total_samples"] += len(samples)

        metadata_path = os.path.join(output_dir, "metadata.json")
        with open(metadata_path, 'w') as f:
            json.dump(all_metadata, f, indent=2)

        return all_metadata


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate ML training data for edge-anomaly-mesh"
    )
    parser.add_argument(
        "--config",
        default="data/config/hubs.json",
        help="Path to hub configuration file"
    )
    parser.add_argument(
        "--output",
        default="data/training",
        help="Output directory for training data"
    )
    parser.add_argument(
        "--samples",
        type=int,
        default=500,
        help="Samples per class (8 classes total)"
    )

    args = parser.parse_args()

    # Handle relative paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)

    config_path = args.config
    if not os.path.isabs(config_path):
        config_path = os.path.join(project_root, config_path)

    output_dir = args.output
    if not os.path.isabs(output_dir):
        output_dir = os.path.join(project_root, output_dir)

    print(f"Loading hub configuration from: {config_path}")
    print(f"Output directory: {output_dir}")
    print(f"Samples per class: {args.samples}")
    print()

    generator = TrainingDataGenerator(config_path)

    print("Generating balanced training data (equal samples per class)...")
    metadata = generator.generate_balanced_dataset(
        output_dir=output_dir,
        samples_per_class=args.samples,
    )

    print()
    print("=" * 60)
    print("Training Data Generation Complete")
    print("=" * 60)
    print(f"Total classes: {len(metadata['files'])}")
    print(f"Samples per class: {metadata['samples_per_class']}")
    print(f"Total samples: {metadata['total_samples']}")
    print(f"Output directory: {output_dir}")
    print(f"Metadata file: {os.path.join(output_dir, 'metadata.json')}")


if __name__ == "__main__":
    main()
