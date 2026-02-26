import random
import numpy as np



# Plan for anomalies:
# In this file, we have functions for each anomaly.
# We pass in our node to a function, and it applies acceleration
# and/or gyration to it, depending on the anomaly.
# We then mark the node as anomalous before passing it back
# to the rest of the program.


def apply_package_stolen(node):
    node = node.copy()
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
    node["anomalous"] = True
    return node


def package_dropped(node):
    node = node.copy()
    # Simulate sudden drop: strong negative z acceleration, random x/y, and random gyro
    node["accel_x"] += np.random.uniform(-0.2, 0.2)
    node["accel_y"] += np.random.uniform(-0.2, 0.2)
    node["accel_z"] += -9.8 + np.random.uniform(-1.0, 1.0)  # gravity + noise
    node["gyro_x"] += np.random.uniform(-2.0, 2.0)
    node["gyro_y"] += np.random.uniform(-2.0, 2.0)
    node["gyro_z"] += np.random.uniform(-2.0, 2.0)
    node["anomalous"] = True
    return node
def crane_stops_working(node):
    node = node.copy()
    # Set all acceleration values to zero to simulate sudden stop
    node["accel_x"] = 0.0
    node["accel_y"] = 0.0
    node["accel_z"] = 0.0
    node["anomalous"] = True
    return node
    return node


def car_caught_in_traffic(node):
    node = node.copy()
    # Reduce acceleration values to simulate slow movement (traffic)
    node["accel_x"] *= 0.2
    node["accel_y"] *= 0.2
    node["accel_z"] *= 0.2
    node["accel_x"] += np.random.uniform(-0.02, 0.02)
    node["accel_y"] += np.random.uniform(-0.02, 0.02)
    node["accel_z"] += np.random.uniform(-0.02, 0.02)
    node["anomalous"] = True
    return node


def rocky_seas(node):
    node = node.copy()
    # Simulate much larger gyro vibrations (rocky seas)
    node["gyro_x"] += np.random.uniform(-1.0, 1.0)
    node["gyro_y"] += np.random.uniform(-1.0, 1.0)
    node["gyro_z"] += np.random.uniform(-1.0, 1.0)
def car_crash(node):
    node = node.copy()
    # Set all acceleration and velocity values to zero to simulate abrupt stop
    node["accel_x"] = 0.0
    node["accel_y"] = 0.0
    node["accel_z"] = 0.0
    if "velocity_x" in node:
        node["velocity_x"] = 0.0
    if "velocity_y" in node:
        node["velocity_y"] = 0.0
    if "velocity_z" in node:
        node["velocity_z"] = 0.0
def package_falls_off_ship(node):
    node = node.copy()
    # Simulate constant sinking: strong negative z velocity, zero x/y velocity, and mark as anomalous
    node["velocity_x"] = 0.0
    node["velocity_y"] = 0.0
    node["velocity_z"] = -1.5  # Sinks at a constant rate (m/s)
    node["accel_x"] += np.random.uniform(-0.02, 0.02)
    node["accel_y"] += np.random.uniform(-0.02, 0.02)
    node["accel_z"] += np.random.uniform(-0.02, 0.02)
    node["anomalous"] = True
    return node