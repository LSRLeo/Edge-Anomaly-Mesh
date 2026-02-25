import argparse
from src.node import Node
from src.route import Route
import redisFiles.redis_setup
import redisFiles.redis_pub

def run_simulation(node_file, route_file):
    route = Route(route_file)
    route.load_route()

    node = Node(node_file, route)
    node.generate()
    node.publish()


def run_redis(rdis, channel_name):
    redis_pub.publish(rdis, channel_name)


def main():
    parser = argparse.ArgumentParser(description="Run simulation")
    subparsers = parser.add_subparsers(dest="command", required=True, help="sim or redis")

    sim_parser = subparsers.add_parser("sim", help="Run simulation from node and route config files")
    sim_parser.add_argument(
        "-n", "--node",
        type=str,
        required=True,
        help="JSON file name for node configuration",
    )
    sim_parser.add_argument(
        "-r", "--route",
        type=str,
        required=True,
        help="JSON file name for route configuration",
    )

    redis_parser = subparsers.add_parser("redis", help="Run with Redis (placeholder)")
    redis_parser.add_argument(
        "--host",
        default="localhost",
        help="REDIS server hostname (default: localhost)",
    )
    redis_parser.add_argument(
        "--port",
        type=int,
        default=6379,
        help="REDIS server port number (default: 6379)",
    )
    redis_parser.add_argument(
        "channel_name",
        help="name of channel to monitor",
    )

    args = parser.parse_args()

    if args.command == "sim":
        run_simulation(args.node, args.route)
    elif args.command == "redis":
        rdis = redis_setup.connect(args.host, args.port)
        run_redis(rdis, args.channel_name)


if __name__ == "__main__":
    main()