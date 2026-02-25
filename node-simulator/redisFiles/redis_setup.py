# common constants used throughout the redis_* scripts

import logging
import redis

BRAIN_TO = "*"
CHANNEL_DEBUG = 'debug_msgs'
CHANNEL_ERROR = 'error_msgs'
CHANNEL_EXTERNAL = 'external_msgs'
CHANNEL_INTERNAL = 'internal_msgs'
CONFIG_PREFIX = "config:"
REDIS_DB = 0
REDIS_SOCKET_TIMEOUT_SEC = 5

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def connect(host:str, port:int):
    """connect(host:str, port:ind)

    Connect to the REDIS server at the specified host and port.
    """
    try:
        # Connect
        rdis = redis.Redis(
            host=host,
            port=port,
            db=REDIS_DB,
            decode_responses=True,
            socket_connect_timeout=REDIS_SOCKET_TIMEOUT_SEC,
            socket_timeout=REDIS_SOCKET_TIMEOUT_SEC)
    
        # Test connection
        rdis.ping()
        logger.info(f"connected to REDIS server at {host}:{port} successfully")

        return rdis
        
    except redis.ConnectionError:
        logger.error(f"failed to connect to REDIS server at {host}:{port}")
        # can't do anything else
        exit(1)

