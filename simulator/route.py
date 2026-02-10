from hub import Hub
import json

class Route:
    def __init__(self, hubs: list[Hub], jason_file): #route is a array of hubs in order
       self.hubs = hubs
       self.jason_file = jason_file
    

    def load_route(self):
        try:
            with open(self.jason_file, 'r') as f:
                data = json.load(f)

            for hub_data in data['hubs']:
                hub = Hub(
                    name=hub_data['name'],
                    lat=hub_data['gps_lat'],
                    lon=hub_data['gps_lon'],
                    alt=hub_data['alt'],
                    time_at_hub=hub_data['time_at_hub'],
                    mode=hub_data['mode'],
                    lift_time=hub_data['lift_time']
                )
                self.hubs.append(hub)
        except FileNotFoundError:
            raise FileNotFoundError(f"JSON file {self.jason_file} not found")
        except json.JSONDecodeError:
            raise ValueError(f"Error decoding JSON file {self.jason_file}")
        except KeyError as e:
            raise ValueError(f"Missing key {e} in JSON file {self.jason_file}")


    def add_hub(self, hub: Hub):
        self.hubs.append(hub)

    #maybe should add a method to insert a hub at a specific index in the route, but for now we can just add to the end and then reorder the route if needed??


    def get_hub(self, hub_name:str) -> Hub:
       for hub in self.hubs:
           if hub.name == hub_name:
               return hub
       raise ValueError(f"Hub {hub_name} not found in route")
  
    def __len__(self): #get the number of hubs in the route
       return len(self.hubs)
  
    
    def getTotalTime(self) ->float: #total time spent at each hub
        #is time at hub same as time traveling between hubs? 
        total = 0.0
        for h in self.hubs:
            total += h.time_at_hub + h.lift_time
        return total

    



