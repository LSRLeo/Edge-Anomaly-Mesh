import numpy as np

def apply_package_stolen(node):
    import random
    # Choose a random direction (2D)
    angle = random.uniform(0, 2 * np.pi)
    direction = np.array([np.cos(angle), np.sin(angle)])
    # Apply a strong, directional change to accel and gyro
    accel_magnitude = 2.0  # Stronger than normal noise
    gyro_magnitude = 1.0
    node = node.copy()  # Avoid mutating input
    node["accel_x"] += direction[0] * accel_magnitude + np.random.uniform(-0.2, 0.2)
    node["accel_y"] += direction[1] * accel_magnitude + np.random.uniform(-0.2, 0.2)
    node["accel_z"] += np.random.uniform(-0.2, 0.2)
    node["gyro_x"] += direction[0] * gyro_magnitude + np.random.uniform(-0.05, 0.05)
    node["gyro_y"] += direction[1] * gyro_magnitude + np.random.uniform(-0.05, 0.05)
    node["gyro_z"] += np.random.uniform(-0.05, 0.05)
    return node

def crane_stops_working(node):
    node = node.copy()
    # Set all acceleration values to zero to simulate sudden stop
    node["accel_x"] = 0.0
    node["accel_y"] = 0.0
    node["accel_z"] = 0.0
    return node

def car_caught_in_traffic(node):
    node = node.copy()
    # Reduce acceleration values to simulate slow movement (traffic)
    node["accel_x"] *= 0.2
    node["accel_y"] *= 0.2
    node["accel_z"] *= 0.2
    # Optionally, add small random noise
    node["accel_x"] += np.random.uniform(-0.02, 0.02)
    node["accel_y"] += np.random.uniform(-0.02, 0.02)
    node["accel_z"] += np.random.uniform(-0.02, 0.02)
    return node
import numpy as np
