from src.hub import Hub
from src.waypoint import Waypoint
import json
from src.waypointsMaker import WaypointMaker
from src.segment import Segment
from random import randint
class Route:
    def __init__(self, jason_file): #route is a array of hubs in order
       self.points = [] #ordered list of hubs and waypoints in the route
       self.jason_file = jason_file
       self.waypointMaker = WaypointMaker(5) #default is 5 waypoints can later modify
       self.segments = [] #ordered list of segments in the route, each segment is a start hub, end hub, mode, and waypoints in between
    

    def load_route(self):
        try:
            with open(self.jason_file, 'r') as f:
                data = json.load(f)

            hubs = data['hubs']  
            hub_list = []

            for hub_data in hubs:

                hub = Hub(
                    hub_id=hub_data["hub_id"],
                    name=hub_data["name"],
                    lat=hub_data["lat"],
                    lon=hub_data["lon"],
                    altitude=hub_data["altitude_m"],
                    time_at_hub=hub_data["time_at_hub"],
                    mode=hub_data["mode"],
                    radius=hub_data["radius_m"],
                    hub_type=hub_data["type"],
                    lift_time=hub_data["lift_time"],
                    label=hub_data["label"]
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
        self.segments = []

        if len(hubs) == 0:
            return self.points

        if len(hubs) == 1:
            self.points.append(hubs[0])
            return self.points

        # start hub
        self.points.append(hubs[0])

        for i in range(len(hubs) - 1):
            start = hubs[i]
            end = hubs[i + 1]

            self.waypointMaker.num_waypoints = randint(3, 10)
            mode = start.mode.lower()

            wps: list[Waypoint] = []

            # Only generate transit waypoints for motion modes
            if mode not in {"idle", "lift"}:
                wps = self.waypointMaker.make(start, end, mode)
                self.points.extend(wps)

            # Always append end hub to flattened points
            self.points.append(end)

            # Record the hub->hub segment (even if idle/lift; points can be empty)
            self.segments.append(
                Segment(start=start, end=end, mode=mode.upper(), points=wps)
            )

        return self.points


        

