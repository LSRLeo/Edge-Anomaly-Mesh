from node import Node
import time
from publisher import RedisPublisher

def main():
    redis = RedisPublisher("localhost",6379,0)
    node = Node("node_001", "IDLE", redis)

    node.start()  
    time.sleep(5)

    node.pause()
    time.sleep(2)

    node.start()  
    time.sleep(3)

    node.stop()   


if __name__ == "__main__":
    main()