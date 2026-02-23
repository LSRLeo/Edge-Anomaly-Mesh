import numpy as np

def apply_maritime_node_noise(node):
    accel_error = {"x": 0.17, "y": 0.13, "z": 0.20}
    gyro_error = {"x": 0.08, "y": 0.032, "z": 0.023}
    node["accel_x"] += np.random.uniform(-accel_error["x"], accel_error["x"])
    node["accel_y"] += np.random.uniform(-accel_error["y"], accel_error["y"])
    node["accel_z"] += np.random.uniform(-accel_error["z"], accel_error["z"])
    node["gyro_x"] += np.random.uniform(-gyro_error["x"], gyro_error["x"])
    node["gyro_y"] += np.random.uniform(-gyro_error["y"], gyro_error["y"])
    node["gyro_z"] += np.random.uniform(-gyro_error["z"], gyro_error["z"])
    return node

def apply_terrestrial_node_noise(node):
    accel_error = {"x": 0.17, "y": 0.13, "z": 0.20}
    gyro_error = {"x": 0.08, "y": 0.032, "z": 0.023}
    node["accel_x"] += np.random.uniform(-accel_error["x"], accel_error["x"])
    node["accel_y"] += np.random.uniform(-accel_error["y"], accel_error["y"])
    node["accel_z"] += np.random.uniform(-accel_error["z"], accel_error["z"])
    node["gyro_x"] += np.random.uniform(-gyro_error["x"], gyro_error["x"])
    node["gyro_y"] += np.random.uniform(-gyro_error["y"], gyro_error["y"])
    node["gyro_z"] += np.random.uniform(-gyro_error["z"], gyro_error["z"])
    return node

def apply_lift_node_noise(node):
    accel_error = {"x": 0.17, "y": 0.13, "z": 0.20}
    gyro_error = {"x": 0.08, "y": 0.032, "z": 0.023}
    node["accel_x"] += np.random.uniform(-accel_error["x"], accel_error["x"])
    node["accel_y"] += np.random.uniform(-accel_error["y"], accel_error["y"])
    node["accel_z"] += np.random.uniform(-accel_error["z"], accel_error["z"])
    node["gyro_x"] += np.random.uniform(-gyro_error["x"], gyro_error["x"])
    node["gyro_y"] += np.random.uniform(-gyro_error["y"], gyro_error["y"])
    node["gyro_z"] += np.random.uniform(-gyro_error["z"], gyro_error["z"])
    return node

def apply_idle_node_noise(node):
    accel_error = {"x": 0.17, "y": 0.13, "z": 0.20}
    gyro_error = {"x": 0.08, "y": 0.032, "z": 0.023}
    node["accel_x"] += np.random.uniform(-accel_error["x"], accel_error["x"])
    node["accel_y"] += np.random.uniform(-accel_error["y"], accel_error["y"])
    node["accel_z"] += np.random.uniform(-accel_error["z"], accel_error["z"])
    node["gyro_x"] += np.random.uniform(-gyro_error["x"], gyro_error["x"])
    node["gyro_y"] += np.random.uniform(-gyro_error["y"], gyro_error["y"])
    node["gyro_z"] += np.random.uniform(-gyro_error["z"], gyro_error["z"])
    return node