class Idle:
    def generate_reading():
        accel_x = 0
        accel_y = 0
        accel_z = 9.81
        gyro_x = 0
        gyro_y = 0
        gyro_z = 0

        return SensorReading(accel_x, accel_y, accel_z, gyro_x, gyro_y, gyro_z)

class Lift:
    pass

class Maritime:
    pass

class Terrestrial:
    pass

class SensorReading:
    def __init__(self, accel_x, accel_y, accel_z, gyro_x, gyro_y, gyro_z):
        self.accel_x = accel_x
        self.accel_y = accel_y
        self.accel_z = accel_z
        self.gyro_x = gyro_x
        self.gyro_y = gyro_y
        self.gyro_z = gyro_z
    