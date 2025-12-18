"""
Motion Generators Package

Provides motion simulation for different transport types:
- IdleMotionGenerator: Stationary cargo
- TerrestrialMotionGenerator: Road/rail transport
- MaritimeMotionGenerator: Ocean/sea transport
- LiftMotionGenerator: Forklift operations
"""

from .base import BaseMotionGenerator, SensorReading
from .idle import IdleMotionGenerator
from .terrestrial import TerrestrialMotionGenerator
from .maritime import MaritimeMotionGenerator
from .lift import LiftMotionGenerator

__all__ = [
    "BaseMotionGenerator",
    "SensorReading",
    "IdleMotionGenerator",
    "TerrestrialMotionGenerator",
    "MaritimeMotionGenerator",
    "LiftMotionGenerator",
]

# Convenience mapping from motion type string to generator class
MOTION_GENERATORS = {
    "IDLE": IdleMotionGenerator,
    "TERRESTRIAL": TerrestrialMotionGenerator,
    "MARITIME": MaritimeMotionGenerator,
    "LIFT": LiftMotionGenerator,
}


def get_generator(motion_type: str, **kwargs) -> BaseMotionGenerator:
    """
    Factory function to get a motion generator by type name.
    
    Args:
        motion_type: One of "IDLE", "TERRESTRIAL", "MARITIME", "LIFT"
        **kwargs: Arguments to pass to the generator constructor
        
    Returns:
        Appropriate motion generator instance
        
    Raises:
        ValueError: If motion_type is not recognized
    """
    # TODO: Look up generator class from MOTION_GENERATORS
    # TODO: Raise ValueError if not found
    # TODO: Instantiate and return generator with kwargs
    pass
