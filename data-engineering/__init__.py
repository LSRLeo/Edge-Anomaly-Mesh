"""
Team 1: Data Engineering

This package provides the sensor network simulation for the
edge-anomaly-mesh project.

Main components:
- SensorNode: Individual sensor node simulation
- NodeManager: Manages collection of nodes
- HubManager: Network topology management
- SensorDataPublisher: Publishes data to Redis
- Motion Generators: Generate realistic motion data

Usage:
    from data-engineering import Simulator, SimulatorConfig
    
    config = SimulatorConfig(num_nodes=10, duration=60)
    sim = Simulator(config)
    sim.setup()
    sim.run()
"""

from .node_simulator import SensorNode, NodeManager
from .hub_manager import Hub, Route, HubManager, NetworkTopologyBuilder
from .redis_publisher import SensorDataPublisher, BufferedPublisher
from .run_simulator import Simulator, SimulatorConfig
from .motion_generators import (
    BaseMotionGenerator,
    IdleMotionGenerator,
    TerrestrialMotionGenerator,
    MaritimeMotionGenerator,
    LiftMotionGenerator,
    get_generator,
)

__all__ = [
    # Node simulation
    "SensorNode",
    "NodeManager",
    
    # Network topology
    "Hub",
    "Route", 
    "HubManager",
    "NetworkTopologyBuilder",
    
    # Publishing
    "SensorDataPublisher",
    "BufferedPublisher",
    
    # Main simulator
    "Simulator",
    "SimulatorConfig",
    
    # Motion generators
    "BaseMotionGenerator",
    "IdleMotionGenerator",
    "TerrestrialMotionGenerator",
    "MaritimeMotionGenerator",
    "LiftMotionGenerator",
    "get_generator",
]
