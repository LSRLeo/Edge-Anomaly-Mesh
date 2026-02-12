from hub import Hub
from section import Section
import json

class Route:
    def __init__(self, hubs: list[Hub], jason_file): #route is a array of hubs in order
       self.hubs = hubs
       self.sections = []
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


            for i in range(len(self.hubs) - 1):
                section = Section(self.hubs[i], self.hubs[i + 1], self.hubs[i].mode)
                self.sections.append(section)
            
            
        except FileNotFoundError:
            raise FileNotFoundError(f"JSON file {self.jason_file} not found")
        except json.JSONDecodeError:
            raise ValueError(f"Error decoding JSON file {self.jason_file}")
        except KeyError as e:
            raise ValueError(f"Missing key {e} in JSON file {self.jason_file}")

   


 
    



