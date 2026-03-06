from redis_reader import RedisReader
import redis

CHANNELNAME_QUERY = "ui:query"
CHANNELNAME_RESPONSE = "ui:responses"
def main():
    # simply testing redis_reader publish and subscribe functionality, will be used in main dashboard to pull data from redis and update dataframes
    pub = redis.Redis(host="localhost",port=6379, decode_responses=True)
    sub = pub.pubsub()
    sub.psubscribe(CHANNELNAME_QUERY,CHANNELNAME_RESPONSE) #subscribe to response channel for receiving data from redis
    redis_reader = RedisReader(CHANNELNAME_QUERY, CHANNELNAME_RESPONSE, pub, sub)
    
    while True:
        redis_reader.refresh(instant=False) #initial refresh to populate data from redis before starting dashboard
if __name__ == "__main__":
    main()