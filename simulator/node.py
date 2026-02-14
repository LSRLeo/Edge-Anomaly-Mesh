import time
import json

from lift import Lift
from maritime import Maritime
# from terrestrial import Terrestrial
from idle import Idle

class Node:
    def __init__(self, node_file, route):
        self.route = route
        self.messages = []

        try:
            with open(node_file, 'r') as f:
                node_config = json.load(f)

            self.node_id = node_config['node_id']
            self.sample_rate_hz = node_config['sample_rate_hz']
            self.seq = 0
            self.idle = Idle(self.sample_rate_hz)
            self.lift = Lift()
            self.maritime = Maritime(self.sample_rate_hz)
        except FileNotFoundError:
            raise FileNotFoundError(f"Node configuration file {node_file} not found")
        except json.JSONDecodeError:
            raise ValueError(f"Error decoding node configuration file {node_file}")
    
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
                    self.messages += self.maritime.generate_reading(current_hub, next_hub)
                elif current_hub.mode == "terrestrial":
                    pass
                #     self.messages += Terrestrial.generate_reading(current_hub, next_hub, self.sample_rate_hz)
                else:
                    raise ValueError(f"Invalid mode: {current_hub.mode}")

    def publish(self):
        with open('raw_data.json', 'w') as f:
            json.dump(self.messages, f, indent=2)