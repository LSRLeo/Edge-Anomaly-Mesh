import redis
import json
from node import Node
from datetime import datetime, timezone
# Before running this code, go to terminal and connect to redis server first
# Connect to a local Redis server (default host: localhost, port: 6379)

# command to start docker server: docker run -p 6379:6379 redis
# keep server open and work in new terminal while using redis
# by tues: finish publisher.py, ideally node.py as well
r = redis.Redis(host='localhost', port=6379, decode_responses=True)

test_node = Node("node_1", "IDLE")
channel = f"sensor:raw:{test_node.node_id}"

#create a sample test message and we can build this text format later on in node.py
message = {
    "node_id": test_node.node_id,
    "time_stamp": datetime.now(timezone.utc).isoformat(),
    "seq": test_node.seq,
    "mode": test_node.mode,
}

r.publish(channel, json.dumps(message))
print(f"Published to channel {channel}: {message}")