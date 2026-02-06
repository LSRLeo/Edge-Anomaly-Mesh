# REDIS Utility Scripts

Utility scripts for working with Redis pub/sub in the edge-anomaly-mesh project.

New to Redis? Start with the [Skills Building](#skills-building) exercise.

## REDIS Server Setup

This project uses [Redis](https://redis.io/) as middleware for inter-module communication.

### Local Redis Server via Docker

```bash
# Pull the official Redis image
docker pull redis:latest

# Run Redis server on default port 6379
docker run --name redis-server -p 6379:6379 -d redis:latest

# Stop the Redis server
docker stop redis-server

# Start an existing Redis container
docker start redis-server

# Remove the container (if you want to start fresh)
docker rm redis-server
```

### Redis Command-Line Tools

The Docker container includes `redis-cli` for interacting with the server directly:

```bash
# Open an interactive Redis CLI session
docker exec -it redis-server redis-cli

# Monitor all Redis commands in real-time (useful for debugging)
docker exec -it redis-server redis-cli monitor

# Ping the server to test connectivity
docker exec -it redis-server redis-cli ping

# List all active pub/sub channels
docker exec -it redis-server redis-cli pubsub channels
```

## Available Scripts

### REDIS Publisher

Reads lines from standard input and publishes to a named channel. Leading/trailing whitespace is stripped. CTRL-d stops the program.

```bash
python redis_pub.py [-h] [--host HOST] [--port PORT] [--verbose] channel_name
```

**Arguments:**
- `channel_name` - name of channel to publish to (required)
- `--host HOST` - Redis server hostname (default: localhost)
- `--port PORT` - Redis server port number (default: 6379)
- `--verbose` - Enable verbose logging

**Example:**
```bash
echo '{"m_type": "raw-data", "node_id": "node_001"}' | python redis_pub.py sensor:raw:node_001
```

### REDIS Subscriber

Monitors a named channel and outputs received messages to standard output with timestamps. CTRL-c stops the program.

```bash
python redis_sub.py [-h] [--host HOST] [--port PORT] [--verbose] channel_name
```

**Arguments:**
- `channel_name` - name of channel to monitor (required)
- `--host HOST` - Redis server hostname (default: localhost)
- `--port PORT` - Redis server port number (default: 6379)
- `--verbose` - Enable verbose logging

**Example:**
```bash
python redis_sub.py sensor:raw:node_001
```

### Common Module

`redis_common.py` provides shared constants and connection logic:

- `connect(host, port)` - Connect to Redis server with error handling
- Channel constants: `CHANNEL_DEBUG`, `CHANNEL_ERROR`, `CHANNEL_INTERNAL`, `CHANNEL_EXTERNAL`
- Default settings: `REDIS_DB=0`, `REDIS_SOCKET_TIMEOUT_SEC=5`

## Skills Building

Follow these steps to get hands-on experience with Redis pub/sub messaging.

### Step 1: Set Up Python Environment

Create a new virtual environment or activate an existing one:

```bash
# Create a new virtual environment (one-time)
python3 -m venv .venv

# Activate it
source .venv/bin/activate    # Linux/Mac
# .venv\Scripts\activate     # Windows
```

Install the required Python packages:

```bash
pip install -r scripts/redis_requirements.txt
```

### Step 2: Install and Start Redis

```bash
# Pull the Redis Docker image (one-time)
docker pull redis:latest

# Start the Redis server
docker run --name redis-server -p 6379:6379 -d redis:latest
```

Verify it's running:
```bash
docker ps | grep redis
```

### Step 3: Start the Subscriber (Terminal 1)

Open a terminal, activate your virtual environment, and start listening on a test channel:

```bash
source .venv/bin/activate
cd scripts
python redis_sub.py test_channel
```

You should see a connection message. The subscriber is now waiting for messages.

### Step 4: Publish Messages (Terminal 2)

Open a second terminal, activate your virtual environment, and send some messages:

```bash
source .venv/bin/activate
cd scripts
echo "Hello from Terminal 2!" | python redis_pub.py test_channel
```

Watch Terminal 1 - you should see the message appear with a timestamp.

### Step 5: Interactive Publishing

You can also type messages interactively:

```bash
python redis_pub.py test_channel
```

Type messages and press Enter to send each one. Press CTRL-d to exit.

### Step 6: Clean Up

```bash
# Stop the subscriber with CTRL-c in Terminal 1
# Stop Redis server
docker stop redis-server
```
