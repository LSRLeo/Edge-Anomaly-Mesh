from hub import Hub



class Section:
    def __init__(self, hub1: Hub, hub2: Hub, mode: str):
        self.hub1 = hub1
        self.hub2 = hub2
        self.mode = mode
        self.transportTime = hub1.time_at_hub + hub2.time_at_hub + (hub1.lift_time if mode == "LIFT" else 0) 






    



