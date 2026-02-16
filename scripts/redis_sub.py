import argparse
import logging

import redis_common

def main(rdis, channel_name:str):
    pubsub = rdis.pubsub()
    pubsub.subscribe(channel_name)

    try:
        for message in pubsub.listen():
            if message['type'] == 'message':
                redis_common.logger.info(f"{message['data']}")

    except KeyboardInterrupt:
        pass


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='REDIS single channel subscriber')

    parser.add_argument('--host', default='localhost',
                    help='REDIS server hostname (default: localhost)')
    parser.add_argument('--port', type=int, default=6379,
                    help='REDIS server port number (default: 6379)')
    parser.add_argument('channel_name',
                   help='name of channel to monitor')
    parser.add_argument('--verbose', action='store_true',
                    help='Enable verbose logging')

    args = parser.parse_args()

    # Set logging level
    if args.verbose:
        redis_common.logger.setLevel(logging.DEBUG)

    redis_common.logger.info(f"REDIS host: {args.host}")
    redis_common.logger.info(f"REDIS port: {args.port}")
    redis_common.logger.info(f"channel_name: {args.channel_name}")

    rdis = redis_common.connect(args.host, args.port)
    
    main(rdis, args.channel_name)
