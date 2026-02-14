from hub import Hub
import time
import math

class Terrestrial:

    def __init__(self, sample_rate: int = 50):
        self.sample_rate = sample_rate  
        

    
    def generate_reading(self, current_hub, next_hub, sample_rate_hz:int = 50, ):
       # 50 km/h = 50 * (1000/3600) m/s = 50000/3600 = 125/9 m/s
        max_speed = 125/9
        acc = 1.5 # m/s^2

        # calculate distance between two hubs
        distance_between_hubs = Terrestrial.calculate_distance(current_hub, next_hub)

        #velocity = acceleration * time
        #time to reach max speed
        t_acc = max_speed / acc

        #distance covered during acceleration (from rest to max speed)
        #dist_acc = (1/2) * acceleration * (max_spped/a)^2 
        d_acc = (max_speed**2) / (2 * acc)




        #======THERE IS 3 Phase of Movement======
        #1. Acceleration Phase: from rest to max speed
        #2. Constant Speed Phase: moving at max speed
        #3. Deceleration Phase: from max speed to rest

        #First check if the truck can reach max speed before it needs to decelerate
        #If the distance between two hubs is too short such that the truck cannot reach max speed:
        #currently, we assume the truck take the same time to acclerate and decelearte, 
        #if the distance between two hubs is too short such that the truck cannot reach max speed, then there will be no constant speed phase, and the truck will directly decelerate after acceleratin

    
        if distance_between_hubs <= 2 * d_acc:
            # The truck cannot reach max speed, it will accelerate until the midpoint and then decelerate
            #have to recalculate new max speed that we can hit
            #have to calculate the time it takes to accelerate to that new max speed, which will also be the time it takes to decelerate from that new max speed

            if distance_between_hubs <= 0: #if the two hubs are at the same location, then we can just return 0
                new_max_speed = 0.0

            else:
                new_max_speed = math.sqrt(distance_between_hubs * acc)


            #velocity = acceleration * time
            time_to_new_max_speed = new_max_speed / acc

            p1_time = time_to_new_max_speed  # time for acceleration phase
            p3_time = time_to_new_max_speed  # time for deceleration phase
            p2_time = 0  # no constant speed phase
                
      
        else:
            #there is time for the truck to accelerate, cruise, and decelerate
            p1_time = t_acc  # time for acceleration phase
            p3_time = t_acc  # time for deceleration phase

            #distance covered cruise
            #distance of cruise
            d_cruise = distance_between_hubs - 2 * d_acc
            p2_time = d_cruise / max_speed  # time for constant speed phase

        
        total_travel_time = p1_time + p2_time + p3_time
    

        number_of_samples = int(total_travel_time * sample_rate_hz)

        messages = []
        for i in range(number_of_samples):
            t = i / sample_rate_hz  # current time in seconds


            #Right now we only have changing  in the acceleration of x

            
            #To-Do: Add y  and maybe z acceleartion changes

            if t < p1_time:
                x_acc = acc
            elif t < p1_time + p2_time:
                x_acc = 0
            else:
                x_acc = -acc 

            messages.append({
                "accel_x": x_acc,
                "accel_y": 0.0,
                "accel_z": 9.81,
                "gyro_x": 0.0,
                "gyro_y": 0.0,
                "gyro_z": 0.0,
            })
                
    def calculate_time(self, hub1:Hub, hub2:Hub):
        R = 6371000  # meters

        lat1 = math.radians(hub1.lat)
        lon1 = math.radians(hub1.lon)
        lat2 = math.radians(hub2.lat)
        lon2 = math.radians(hub2.lon)

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        return R * c

       
        
    # class SensorReading:
    #     def __init__(self, accel_x, accel_y, accel_z, gyro_x, gyro_y, gyro_z):
    #         self.accel_x = accel_x
    #         self.accel_y = accel_y
    #         self.accel_z = accel_z
    #         self.gyro_x = gyro_x
    #         self.gyro_y = gyro_y
    #         self.gyro_z = gyro_z




