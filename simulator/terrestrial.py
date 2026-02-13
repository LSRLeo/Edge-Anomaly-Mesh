from hub import Hub
import time

class Terrestrial:

    def __init__(self, sample_rate: int = 50):
        self.sample_rate = sample_rate  
        

    
    def generate_reading(self, current_hub, next_hub, sample_rate_hz):
        #this method should call other methods to cacluate the time needed between hubs
        total_time = self.calculate_time(current_hub, next_hub) #calculate time between hubs
        messages = []
        for i in range(sample_rate_hz*total_time):
            acceleration = self.calculate_accleration() #calculate acceleration based on time and distance between hubs
            messages.append({
                "accel_x": acceleration[0],
                "accel_y": acceleration[1],
                "accel_z": 9.81,
                "gyro_x": 0,
                "gyro_y": 0,
                "gyro_z": 0,
            })
      
    

    def calculate_time(self, hub1, hub2):
        #calculate distance between two hubs
        #calculate time it takes for truck when it's moving within radius of hub1
        #calculate time it takes for truck when it's moving within radius of hub2
        #calculate time it takes for truck when it's moving between the two hubs (excluding radius)
      
        pass
        

    def calculate_accleration(self) ->tuple[float, float]:
        pass


    def calculate_radius(self, hub) -> float:
        pass


    #To-Do: change in gyro and accel values for when truck is moving up or down hills

