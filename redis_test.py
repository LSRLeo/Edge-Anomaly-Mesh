import redis
# Before running this code, go to terminal and connect to redis server first
# Connect to a local Redis server (default host: localhost, port: 6379)
r = redis.Redis(host='localhost', port=6379, decode_responses=True)

# Test setting and getting a string value
r.set('test_key', 'test_value')
value = r.get('test_key')
print(f'Value for "test_key": {value}')  # Expected output: test_value

#remember to SHUTDOWN redis-client
