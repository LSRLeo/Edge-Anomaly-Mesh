"""
Shared physical constants for the node-simulator.
Gravity is negative because the Z-axis is "up": gravity pulls down, so g = -9.8 m/s².
At rest, accelerometer reads accel_z = -9.8 (reaction to gravity).
"""
GRAVITY_MSS = -9.8  # m/s², downward (Z-up frame)
