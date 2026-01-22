"""
Node Simulator

Simulates individual sensor nodes attached to cargo packages.
Each node represents a physical sensor device that collects
accelerometer and gyroscope data as cargo moves through the network.

A node:
- Has a unique identifier
- Is currently in one motion state (IDLE, TERRESTRIAL, MARITIME, LIFT)
- Can transition between motion states based on its journey
- Generates sensor readings at a fixed sample rate
- Publishes data to Redis via the publisher
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

from .motion_generators import (
    BaseMotionGenerator,
    IdleMotionGenerator,
    TerrestrialMotionGenerator,
    MaritimeMotionGenerator,
    LiftMotionGenerator,
    get_generator,
)


class NodeState(Enum):
    """Possible states of a sensor node."""
    ACTIVE = "active"           # Generating data
    PAUSED = "paused"           # Temporarily stopped
    OFFLINE = "offline"         # Not responding
    ERROR = "error"             # Sensor malfunction


class SensorNode:
    """
    Represents a single sensor node attached to cargo.
    
    Each node simulates a physical IoT device that would be attached
    to a package/container. It maintains its own state, motion generator,
    and generates realistic sensor data.
    
    Attributes:
        node_id: Unique identifier for this node
        state: Current operational state
        motion_type: Current motion classification
        current_hub: Hub where node is currently located
        generator: Motion generator producing sensor data
    """
    
    def __init__(self, node_id: str, initial_motion: str = "IDLE"):
        """
        Initialize a sensor node.
        
        Args:
            node_id: Unique identifier (e.g., "node_001")
            initial_motion: Starting motion type
        """
        # TODO: Store node_id
        # TODO: Set state to ACTIVE
        # TODO: Set motion_type to initial_motion
        # TODO: Create appropriate motion generator using get_generator()
        # TODO: Initialize current_hub to None
        # TODO: Initialize last_reading_time
        # TODO: Initialize readings_generated counter
        pass
    
    @property
    def node_id(self) -> str:
        """Get the node's unique identifier."""
        # TODO: Return stored node_id
        pass
    
    @property
    def is_active(self) -> bool:
        """Check if node is actively generating data."""
        # TODO: Return True if state is ACTIVE
        pass
    
    def generate_reading(self) -> Optional[Dict[str, Any]]:
        """
        Generate a single sensor reading from this node.
        
        Returns:
            Dictionary with sensor data and metadata, or None if inactive
            Format: {
                "node_id": str,
                "timestamp": ISO format string,
                "accel_x": float,
                "accel_y": float,
                "accel_z": float,
                "gyro_x": float,
                "gyro_y": float,
                "gyro_z": float
            }
        """
        # TODO: Check if node is active, return None if not
        # TODO: Generate reading from motion generator
        # TODO: Get current timestamp
        # TODO: Build output dictionary with all fields
        # TODO: Increment readings_generated counter
        # TODO: Return dictionary
        pass
    
    def set_motion_type(self, motion_type: str) -> None:
        """
        Change the node's motion type.
        
        Called when cargo transitions between transport modes
        (e.g., truck to ship, warehouse to forklift).
        
        Args:
            motion_type: New motion type (IDLE, TERRESTRIAL, MARITIME, LIFT)
        """
        # TODO: Validate motion_type is valid
        # TODO: Update stored motion_type
        # TODO: Create new motion generator of appropriate type
        # TODO: Reset generator state
        pass
    
    def set_hub(self, hub_id: str) -> None:
        """
        Update the node's current hub location.
        
        Args:
            hub_id: Identifier of the hub
        """
        # TODO: Store current_hub
        # TODO: Log transition if previous hub was different
        pass
    
    def pause(self) -> None:
        """
        Pause the node (temporarily stop generating data).
        
        Used when simulating sensor sleep mode or temporary disconnection.
        """
        # TODO: Set state to PAUSED
        pass
    
    def resume(self) -> None:
        """
        Resume a paused node.
        """
        # TODO: Set state to ACTIVE
        pass
    
    def set_offline(self) -> None:
        """
        Mark node as offline (simulates connection loss).
        """
        # TODO: Set state to OFFLINE
        pass
    
    def set_error(self, error_type: str = "unknown") -> None:
        """
        Mark node as having an error.
        
        Args:
            error_type: Description of the error
        """
        # TODO: Set state to ERROR
        # TODO: Store error_type for diagnostics
        pass
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current node status for monitoring.
        
        Returns:
            Dictionary with node status information
        """
        # TODO: Build status dict with:
        #   - node_id
        #   - state
        #   - motion_type
        #   - current_hub
        #   - readings_generated
        #   - last_reading_time
        # TODO: Return status dictionary
        pass
    
    def inject_anomaly(self, anomaly_type: str = "spike") -> None:
        """
        Inject an anomaly into the next reading.
        
        Used for testing anomaly detection. Types:
        - "spike": Sudden acceleration spike
        - "dropout": Missing gravity (sensor failure)
        - "drift": Gradual sensor drift
        
        Args:
            anomaly_type: Type of anomaly to inject
        """
        # TODO: Set flag to inject anomaly on next reading
        # TODO: Store anomaly_type
        pass


class NodeManager:
    """
    Manages a collection of sensor nodes.
    
    Handles creation, lifecycle, and bulk operations on nodes.
    
    Attributes:
        nodes: Dictionary mapping node_id to SensorNode
    """
    
    def __init__(self):
        """Initialize the node manager with empty node collection."""
        # TODO: Initialize empty nodes dictionary
        pass
    
    def create_node(self, node_id: str, initial_motion: str = "IDLE") -> SensorNode:
        """
        Create and register a new sensor node.
        
        Args:
            node_id: Unique identifier for the node
            initial_motion: Starting motion type
            
        Returns:
            The created SensorNode instance
            
        Raises:
            ValueError: If node_id already exists
        """
        # TODO: Check if node_id already exists, raise if so
        # TODO: Create new SensorNode
        # TODO: Add to nodes dictionary
        # TODO: Return the node
        pass
    
    def create_nodes(self, count: int, prefix: str = "node_") -> List[SensorNode]:
        """
        Create multiple nodes with sequential IDs.
        
        Args:
            count: Number of nodes to create
            prefix: Prefix for node IDs (e.g., "node_" -> "node_001")
            
        Returns:
            List of created SensorNode instances
        """
        # TODO: Loop count times
        # TODO: Generate node_id with zero-padded number
        # TODO: Create each node
        # TODO: Return list of nodes
        pass
    
    def get_node(self, node_id: str) -> Optional[SensorNode]:
        """
        Get a node by its ID.
        
        Args:
            node_id: The node identifier
            
        Returns:
            SensorNode if found, None otherwise
        """
        # TODO: Look up and return node from dictionary
        pass
    
    def remove_node(self, node_id: str) -> bool:
        """
        Remove a node from management.
        
        Args:
            node_id: The node to remove
            
        Returns:
            True if removed, False if not found
        """
        # TODO: Remove node from dictionary if exists
        # TODO: Return success/failure
        pass
    
    def get_all_nodes(self) -> List[SensorNode]:
        """
        Get all managed nodes.
        
        Returns:
            List of all SensorNode instances
        """
        # TODO: Return list of all nodes
        pass
    
    def get_active_nodes(self) -> List[SensorNode]:
        """
        Get all nodes that are currently active.
        
        Returns:
            List of active SensorNode instances
        """
        # TODO: Filter nodes where is_active is True
        # TODO: Return filtered list
        pass
    
    def generate_all_readings(self) -> List[Dict[str, Any]]:
        """
        Generate readings from all active nodes.
        
        Returns:
            List of reading dictionaries from all active nodes
        """
        # TODO: Loop through active nodes
        # TODO: Generate reading from each
        # TODO: Collect non-None readings
        # TODO: Return list
        pass
    
    def set_all_motion(self, motion_type: str) -> None:
        """
        Set all nodes to the same motion type.
        
        Args:
            motion_type: Motion type to set
        """
        # TODO: Loop through all nodes
        # TODO: Set motion type on each
        pass
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get aggregate statistics about managed nodes.
        
        Returns:
            Dictionary with:
            - total_nodes: int
            - active_nodes: int
            - nodes_by_state: dict
            - nodes_by_motion: dict
        """
        # TODO: Count total nodes
        # TODO: Count active nodes
        # TODO: Group by state
        # TODO: Group by motion type
        # TODO: Return statistics dictionary
        pass
