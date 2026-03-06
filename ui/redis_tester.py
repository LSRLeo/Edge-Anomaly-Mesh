from redis_reader import RedisReader
import redis

CHANNELNAME_QUERY = "ui:query"
CHANNELNAME_RESPONSE = "ui:responses"
def main():
    # simply testing redis_reader publish and subscribe functionality, will be used in main dashboard to pull data from redis and update dataframes
    r = redis.Redis(host="localhost",port=6379, decode_responses=True)
    print("Connected to Redis") #CYA measure to ensure connection is successful before proceeding
    sub = r.pubsub()
    print("Created Redis PubSub object") #CYA measure to ensure PubSub object is created successfully before proceeding
    sub.psubscribe(CHANNELNAME_QUERY,CHANNELNAME_RESPONSE) #subscribe to response channel for receiving data from redis
    redis_reader = RedisReader(CHANNELNAME_QUERY, CHANNELNAME_RESPONSE, r, sub)
    print('Testing publish..')
    redis_reader.test_publish() #test publish method to send a message to redis
    print('Testing subscribe..')
    redis_reader.test_subscribe() #test subscribe method to listen for messages from redis and print them
    sub.close() #close the subscriber connection when done

if __name__ == "__main__":
    main()