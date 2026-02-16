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