class Idle:
    def generate_reading(current_hub, sample_rate_hz):
        messages = []
        for i in range(sample_rate_hz*current_hub.time_at_hub):
            messages.append({
                "accel_x": 0,
                "accel_y": 0,
                "accel_z": 9.81,
                "gyro_x": 0,
                "gyro_y": 0,
                "gyro_z": 0,
            })
        return messages