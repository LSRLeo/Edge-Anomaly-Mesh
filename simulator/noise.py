import numpy as np

def apply_maritime_node_noise():
	accel_error = {"x": 0.17, "y": 0.13, "z": 0.20}
	gyro_error = {"x": 0.08, "y": 0.032, "z": 0.023}
	# Base values for maritime node (assume some pitch/roll, adjust as needed)
	accel_base = {"x": 0, "y": 0, "z": 9.81}
	gyro_base = {"x": 0, "y": 0, "z": 0}
	noisy_reading = {
		"accel_x": accel_base["x"] + np.random.uniform(-accel_error["x"], accel_error["x"]),
		"accel_y": accel_base["y"] + np.random.uniform(-accel_error["y"], accel_error["y"]),
		"accel_z": accel_base["z"] + np.random.uniform(-accel_error["z"], accel_error["z"]),
		"gyro_x": gyro_base["x"] + np.random.uniform(-gyro_error["x"], gyro_error["x"]),
		"gyro_y": gyro_base["y"] + np.random.uniform(-gyro_error["y"], gyro_error["y"]),
		"gyro_z": gyro_base["z"] + np.random.uniform(-gyro_error["z"], gyro_error["z"]),
	}
	return noisy_reading

def apply_terrestrial_node_noise():
	accel_error = {"x": 0.17, "y": 0.13, "z": 0.20}
	gyro_error = {"x": 0.08, "y": 0.032, "z": 0.023}
	# Base values for terrestrial node (assume some forward movement, adjust as needed)
	accel_base = {"x": 0, "y": 0, "z": 9.81}
	gyro_base = {"x": 0, "y": 0, "z": 0}
	noisy_reading = {
		"accel_x": accel_base["x"] + np.random.uniform(-accel_error["x"], accel_error["x"]),
		"accel_y": accel_base["y"] + np.random.uniform(-accel_error["y"], accel_error["y"]),
		"accel_z": accel_base["z"] + np.random.uniform(-accel_error["z"], accel_error["z"]),
		"gyro_x": gyro_base["x"] + np.random.uniform(-gyro_error["x"], gyro_error["x"]),
		"gyro_y": gyro_base["y"] + np.random.uniform(-gyro_error["y"], gyro_error["y"]),
		"gyro_z": gyro_base["z"] + np.random.uniform(-gyro_error["z"], gyro_error["z"]),
	}
	return noisy_reading

def apply_lift_node_noise():
	accel_error = {"x": 0.17, "y": 0.13, "z": 0.20}
	gyro_error = {"x": 0.08, "y": 0.032, "z": 0.023}
	# Base values for lift node (assume upward movement, adjust as needed)
	accel_base = {"x": 0, "y": 0, "z": 9.81}
	gyro_base = {"x": 0, "y": 0, "z": 0}
	noisy_reading = {
		"accel_x": accel_base["x"] + np.random.uniform(-accel_error["x"], accel_error["x"]),
		"accel_y": accel_base["y"] + np.random.uniform(-accel_error["y"], accel_error["y"]),
		"accel_z": accel_base["z"] + np.random.uniform(-accel_error["z"], accel_error["z"]),
		"gyro_x": gyro_base["x"] + np.random.uniform(-gyro_error["x"], gyro_error["x"]),
		"gyro_y": gyro_base["y"] + np.random.uniform(-gyro_error["y"], gyro_error["y"]),
		"gyro_z": gyro_base["z"] + np.random.uniform(-gyro_error["z"], gyro_error["z"]),
	}
	return noisy_reading


def apply_idle_node_noise():

	accel_error = {"x": 0.17, "y": 0.13, "z": 0.20}
	gyro_error = {"x": 0.08, "y": 0.032, "z": 0.023}
	# Base values for idle node
	accel_base = {"x": 0, "y": 0, "z": 9.81}
	gyro_base = {"x": 0, "y": 0, "z": 0}
	noisy_reading = {
		"accel_x": accel_base["x"] + np.random.uniform(-accel_error["x"], accel_error["x"]),
		"accel_y": accel_base["y"] + np.random.uniform(-accel_error["y"], accel_error["y"]),
		"accel_z": accel_base["z"] + np.random.uniform(-accel_error["z"], accel_error["z"]),
		"gyro_x": gyro_base["x"] + np.random.uniform(-gyro_error["x"], gyro_error["x"]),
		"gyro_y": gyro_base["y"] + np.random.uniform(-gyro_error["y"], gyro_error["y"]),
		"gyro_z": gyro_base["z"] + np.random.uniform(-gyro_error["z"], gyro_error["z"]),
	}
	return noisy_reading
