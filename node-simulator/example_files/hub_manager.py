"""
Hub Manager

Manages the network topology of distribution hubs and routes between them.

In the simulation, hubs represent:
- Warehouses (IDLE state for cargo)
- Distribution centers
- Ports (MARITIME connections)
- Rail/truck terminals (TERRESTRIAL connections)

Nodes (cargo) travel between hubs, and the route determines
what motion type they experience during transit.
"""

from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import random


class HubType(Enum):
    """Types of distribution hubs."""
    WAREHOUSE = "warehouse"         # Storage facility (IDLE)
    DISTRIBUTION = "distribution"   # General distribution center
    PORT = "port"                   # Seaport (MARITIME routes)
    RAIL_TERMINAL = "rail"          # Rail terminal (TERRESTRIAL)
    TRUCK_TERMINAL = "truck"        # Trucking hub (TERRESTRIAL)
    AIRPORT = "airport"             # Air cargo (could extend to AERIAL)


class RouteType(Enum):
    """Types of routes between hubs (determines motion type)."""
    ROAD = "road"                   # TERRESTRIAL motion
    RAIL = "rail"                   # TERRESTRIAL motion
    SEA = "sea"                     # MARITIME motion
    INTERNAL = "internal"           # LIFT motion (within facility)


@dataclass
class Hub:
    """
    Represents a distribution hub in the network.
    
    Attributes:
        hub_id: Unique identifier
        name: Human-readable name
        hub_type: Type of facility
        location: (latitude, longitude) tuple
        capacity: Maximum nodes that can be at this hub
    """
    hub_id: str
    name: str
    hub_type: HubType
    location: Tuple[float, float]
    capacity: int = 100


@dataclass
class Route:
    """
    Represents a route between two hubs.
    
    Attributes:
        route_id: Unique identifier
        from_hub: Starting hub ID
        to_hub: Destination hub ID
        route_type: Type of transport
        distance_km: Distance in kilometers
        typical_duration_hours: Expected travel time
    """
    route_id: str
    from_hub: str
    to_hub: str
    route_type: RouteType
    distance_km: float
    typical_duration_hours: float


class HubManager:
    """
    Manages the network topology of hubs and routes.
    
    Provides functionality to:
    - Create and manage hubs
    - Define routes between hubs
    - Calculate paths for cargo
    - Determine motion types for routes
    
    Attributes:
        hubs: Dictionary of hub_id -> Hub
        routes: Dictionary of route_id -> Route
        adjacency: Dictionary of hub_id -> list of connected hub_ids
    """
    
    def __init__(self):
        """Initialize an empty hub network."""
        # TODO: Initialize empty hubs dictionary
        # TODO: Initialize empty routes dictionary
        # TODO: Initialize empty adjacency dictionary
        pass
    
    def add_hub(self, hub: Hub) -> None:
        """
        Add a hub to the network.
        
        Args:
            hub: Hub instance to add
            
        Raises:
            ValueError: If hub_id already exists
        """
        # TODO: Check for duplicate hub_id
        # TODO: Add hub to hubs dictionary
        # TODO: Initialize empty adjacency list for this hub
        pass
    
    def create_hub(
        self,
        hub_id: str,
        name: str,
        hub_type: HubType,
        location: Tuple[float, float],
        capacity: int = 100
    ) -> Hub:
        """
        Create and add a new hub.
        
        Args:
            hub_id: Unique identifier
            name: Human-readable name
            hub_type: Type of facility
            location: (lat, lon) coordinates
            capacity: Maximum node capacity
            
        Returns:
            The created Hub instance
        """
        # TODO: Create Hub instance
        # TODO: Call add_hub()
        # TODO: Return the hub
        pass
    
    def get_hub(self, hub_id: str) -> Optional[Hub]:
        """
        Get a hub by ID.
        
        Args:
            hub_id: Hub identifier
            
        Returns:
            Hub if found, None otherwise
        """
        # TODO: Look up and return hub
        pass
    
    def add_route(self, route: Route) -> None:
        """
        Add a route connecting two hubs.
        
        Args:
            route: Route instance to add
            
        Raises:
            ValueError: If either hub doesn't exist or route_id exists
        """
        # TODO: Validate both hubs exist
        # TODO: Check for duplicate route_id
        # TODO: Add route to routes dictionary
        # TODO: Update adjacency lists (bidirectional)
        pass
    
    def create_route(
        self,
        from_hub: str,
        to_hub: str,
        route_type: RouteType,
        distance_km: float,
        duration_hours: float
    ) -> Route:
        """
        Create and add a new route.
        
        Args:
            from_hub: Starting hub ID
            to_hub: Destination hub ID
            route_type: Type of transport
            distance_km: Distance
            duration_hours: Expected travel time
            
        Returns:
            The created Route instance
        """
        # TODO: Generate route_id from hub IDs
        # TODO: Create Route instance
        # TODO: Call add_route()
        # TODO: Return the route
        pass
    
    def get_route(self, from_hub: str, to_hub: str) -> Optional[Route]:
        """
        Get the route between two hubs.
        
        Args:
            from_hub: Starting hub ID
            to_hub: Destination hub ID
            
        Returns:
            Route if exists, None otherwise
        """
        # TODO: Look up route by hub pair (check both directions)
        # TODO: Return route or None
        pass
    
    def get_connected_hubs(self, hub_id: str) -> List[str]:
        """
        Get all hubs directly connected to a given hub.
        
        Args:
            hub_id: The hub to check
            
        Returns:
            List of connected hub IDs
        """
        # TODO: Look up adjacency list for hub_id
        # TODO: Return list (empty if hub not found)
        pass
    
    def get_motion_type_for_route(self, from_hub: str, to_hub: str) -> str:
        """
        Determine the motion type for traveling a route.
        
        Maps RouteType to motion classification:
        - ROAD, RAIL -> TERRESTRIAL
        - SEA -> MARITIME
        - INTERNAL -> LIFT
        
        Args:
            from_hub: Starting hub ID
            to_hub: Destination hub ID
            
        Returns:
            Motion type string (IDLE if no route found)
        """
        # TODO: Get route between hubs
        # TODO: Map route_type to motion type:
        #   ROAD -> "TERRESTRIAL"
        #   RAIL -> "TERRESTRIAL"
        #   SEA -> "MARITIME"
        #   INTERNAL -> "LIFT"
        # TODO: Return "IDLE" if no route found
        pass
    
    def find_path(self, from_hub: str, to_hub: str) -> Optional[List[str]]:
        """
        Find a path between two hubs using BFS.
        
        Args:
            from_hub: Starting hub ID
            to_hub: Destination hub ID
            
        Returns:
            List of hub IDs forming path, or None if no path exists
        """
        # TODO: Implement BFS to find shortest path
        # TODO: Return list of hub_ids from start to end
        # TODO: Return None if no path exists
        pass
    
    def get_journey_motion_sequence(
        self,
        hub_path: List[str]
    ) -> List[Tuple[str, str, float]]:
        """
        Get the sequence of motion types for a journey.
        
        Args:
            hub_path: List of hub IDs in order
            
        Returns:
            List of (motion_type, segment_description, duration_hours)
        """
        # TODO: For each consecutive pair of hubs:
        #   - Get the route
        #   - Determine motion type
        #   - Get duration
        # TODO: Return list of motion segments
        pass
    
    def get_all_hubs(self) -> List[Hub]:
        """Get all hubs in the network."""
        # TODO: Return list of all Hub instances
        pass
    
    def get_all_routes(self) -> List[Route]:
        """Get all routes in the network."""
        # TODO: Return list of all Route instances
        pass
    
    def get_network_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the network topology.
        
        Returns:
            Dictionary with hub counts, route counts, connectivity info
        """
        # TODO: Count hubs by type
        # TODO: Count routes by type
        # TODO: Calculate average connectivity
        # TODO: Return statistics dictionary
        pass


class NetworkTopologyBuilder:
    """
    Helper class to build common network topologies.
    
    Provides factory methods for creating standard test networks.
    """
    
    @staticmethod
    def create_simple_network() -> HubManager:
        """
        Create a simple 3-hub network for testing.
        
        Warehouse -> Truck Terminal -> Port
        
        Returns:
            Configured HubManager
        """
        # TODO: Create HubManager
        # TODO: Add warehouse hub
        # TODO: Add truck terminal hub
        # TODO: Add port hub
        # TODO: Add road route (warehouse -> truck terminal)
        # TODO: Add sea route (truck terminal -> port)
        # TODO: Return manager
        pass
    
    @staticmethod
    def create_distribution_network(num_warehouses: int = 3) -> HubManager:
        """
        Create a distribution network with multiple warehouses.
        
        Central distribution center connected to multiple warehouses,
        with a port for international shipping.
        
        Args:
            num_warehouses: Number of warehouse hubs to create
            
        Returns:
            Configured HubManager
        """
        # TODO: Create central distribution hub
        # TODO: Create specified number of warehouses
        # TODO: Create port
        # TODO: Connect warehouses to distribution center (road)
        # TODO: Connect distribution center to port (road)
        # TODO: Return manager
        pass
    
    @staticmethod
    def create_random_network(num_hubs: int, connectivity: float = 0.3) -> HubManager:
        """
        Create a random network topology.
        
        Args:
            num_hubs: Number of hubs to create
            connectivity: Probability of route between any two hubs
            
        Returns:
            Configured HubManager
        """
        # TODO: Create random hubs of various types
        # TODO: For each pair of hubs, add route with probability
        # TODO: Ensure network is connected (add edges if needed)
        # TODO: Return manager
        pass
