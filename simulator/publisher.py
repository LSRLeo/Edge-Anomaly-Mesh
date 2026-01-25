import redis
import json
from node import Node
from datetime import datetime, timezone
# Before running this code, go to terminal and connect to redis server first
# Connect to a local Redis server (default host: localhost, port: 6379)

# command to start docker server: docker run -p 6379:6379 redis
# keep server open and work in new terminal while using redis
# by tues: finish publisher.py, ideally node.py as well


# test_node = Node("node_1", "IDLE")
# channel = f"sensor:raw:{test_node.node_id}"

# #create a sample test message and we can build this text format later on in node.py
# message = {
#     "node_id": test_node.node_id,
#     "time_stamp": datetime.now(timezone.utc).isoformat(),
#     "seq": test_node.seq,
#     "gps_lat": 40.7128,
#     "gps_lon": -74.006,
#     "gps_altitude_m": 50.0,
#     "accel_x": -0.0071,
#     "accel_y": 0.1012,
#     "accel_z": 10.0357,
#     "gyro_x": 0.0111,
#     "gyro_y": -0.0012,
#     "gyro_z": 0.0294,
#     "sample_rate_hz": 50,
#     "battery_pct": 100,
#     "mode": test_node.mode,
# }

# r.publish(channel, json.dumps(message))
# print(f"Published to channel {channel}: {message}")


class RedisPublisher:

   

    def __init__(self, node: Node, host:str, port:int, db:int): 
        self.node = node
        self.host = host
        self.port = port
        self.db = db
        self.channel = f"sensor:raw:{self.node.node_id}"
        self.redis_client = redis.Redis(host=self.host, port=self.port, db=self.db)
    
    def publish(self):
        message = self.node.generate_message()
        self.redis_client.publish(self.channel, json.dumps(message))
        print(f"Published to channel {self.channel}: {message}")

  