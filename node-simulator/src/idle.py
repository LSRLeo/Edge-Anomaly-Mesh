from .anomalies import *

class Idle:
    def __init__(self,sample_rate_hz):
        self.sample_rate_hz = sample_rate_hz

    def generate_reading(self,current_hub):
        messages = []
        for i in range(self.sample_rate_hz*current_hub.time_at_hub):
            messages.append({
                "accel_x": 0,
                "accel_y": 0,
                "accel_z": 9.81,
                "gyro_x": 0,
                "gyro_y": 0,
                "gyro_z": 0,
            })
        return messages

    def inject_anomalies(self, nodes, anomaly_func=apply_package_stolen):
        """
        Applies the selected anomaly function to each node in the list.
        nodes: list of dicts (sensor messages)
        anomaly_func: function to apply (default: apply_package_stolen)
        Returns a new list of anomalous nodes.
        """
        if isinstance(nodes, dict):
            # If a single node dict is passed, wrap in list
            nodes = [nodes]
        return [anomaly_func(node) for node in nodes]