from hub import Hub

class Route:
    def __init__(self, hubs: list[Hub], hub_name:str): #route is a array of hubs in order
       self.hubs = hubs
       self.hub_name = hub_name
  
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
  
    
    def getTotalTime(self): #total time spent at each hub
        #is time at hub same as time traveling between hubs? 
        total = 0.0
        for h in self.hubs:
            total += h.time_at_hub + h.lift_time
        return total

    



