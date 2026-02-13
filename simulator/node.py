import time
import json

from lift import Lift
# from maritime import Maritime
# from terrestrial import Terrestrial
from idle import Idle

class Node:
    def __init__(self, node_file, route, sample_rate_hz = 50, node_id = "node_001"):
        self.route = route
        self.messages = []
        self.node_id = node_id
        self.sample_rate_hz = sample_rate_hz
        self.seq = 0
        self.idle = Idle(self.sample_rate_hz)
        self.lift = Lift()
    
    def generate(self):
        for i in range(len(self.route.hubs)):
            if i < len(self.route.hubs) - 1:
                current_hub = self.route.hubs[i]
                next_hub = self.route.hubs[i + 1]

                self.messages += self.idle.generate_reading(current_hub)
                
                if current_hub.mode == "lift":
                    self.lift.set_hub(current_hub, 20)
                    self.messages += self.lift.generate_reading(current_hub.lift_time)
                elif current_hub.mode == "maritime":
                    pass
                #     self.messages += Maritime.generate_reading(current_hub, next_hub, self.sample_rate_hz)
                elif current_hub.mode == "terrestrial":
                    pass
                #     self.messages += Terrestrial.generate_reading(current_hub, next_hub, self.sample_rate_hz)
                else:
                    raise ValueError(f"Invalid mode: {current_hub.mode}")

    def publish(self):
        with open('raw_data.json', 'w') as f:
            json.dump(self.messages, f, indent=2)