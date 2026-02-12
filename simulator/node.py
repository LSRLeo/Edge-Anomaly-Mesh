from generators import Idle, Lift, Maritime, Terrestrial
import time
import json

class Node:
    def __init__(self, node_file, route, sample_rate_hz = 50, node_id = "node_001"):
        self.route = route
        self.messages = []
        self.node_id = node_id
        self.sample_rate_hz = sample_rate_hz
        self.seq = 0
    
    def generate(self):
        for i in range(len(self.route.hubs)):
            if i < len(self.route.hubs) - 1:
                current_hub = self.route.hubs[i]
                next_hub = self.route.hubs[i + 1]

                self.messages.append(Idle.generate_reading(current_hub, self.sample_rate_hz))
                
                switch (current_hub.mode):
                    case "LIFT":
                        self.messages.append(Lift.generate_reading(current_hub, next_hub, self.sample_rate_hz))
                    case "MARITIME":
                        self.messages.append(Maritime.generate_reading(current_hub, next_hub, self.sample_rate_hz))
                    case "TERRESTRIAL":
                        self.messages.append(Terrestrial.generate_reading(current_hub, next_hub, self.sample_rate_hz))
                    case _:
                        raise ValueError(f"Invalid mode: {current_hub.mode}")

    def publish(self):
        with open('raw_data.json', 'w') as f:
            json.dump(self.messages, f, indent=2)