from src.hub import Hub
from src.waypoint import Waypoint
import json
from src.waypointsMaker import WaypointMaker
from random import randint
class Route:
    def __init__(self, jason_file): #route is a array of hubs in order
       self.points = [] #ordered list of hubs and waypoints in the route
       self.jason_file = jason_file
       self.waypointMaker = WaypointMaker(5) #default is 5 waypoints can later modify
    

    def load_route(self):
        try:
            with open(self.jason_file, 'r') as f:
                data = json.load(f)

            hubs = data['hubs']  
            hub_list = []

            for hub_data in hubs:

                hub = Hub(
                    name=hub_data['name'],
                    lat=hub_data['gps_lat'],
                    lon=hub_data['gps_lon'],
                    alt=hub_data['alt'],
                    time_at_hub=hub_data['time_at_hub'],
                    mode=hub_data['mode'],
                    lift_time=hub_data['lift_time'],
                    #dont have label yet
                    # label=hub_data['label'] 
                )

                hub_list.append(hub)


            return self.generate_waypoints(hub_list)



                    



        except FileNotFoundError:
            raise FileNotFoundError(f"JSON file {self.jason_file} not found")
        except json.JSONDecodeError:
            raise ValueError(f"Error decoding JSON file {self.jason_file}")
        except KeyError as e:
            raise ValueError(f"Missing key {e} in JSON file {self.jason_file}")

   
    

    def generate_waypoints(self, hubs):
        
        self.points = []

        if len(hubs) == 0:
            return self.points

        if len(hubs) == 1:
            self.points.append(hubs[0])
            return self.points

        # start hub
        self.points.append(hubs[0])

        # each segment hub[i] -> hub[i+1]
        for i in range(len(hubs) - 1):
            start = hubs[i]
            end = hubs[i + 1]

            self.waypointMaker.num_waypoints = randint(3, 10)
            route_type = (start.mode or "").upper()

            wps = self.waypointMaker.make(start, end, route_type)
            self.points.extend(wps)
            self.points.append(end)

        return self.points


        

