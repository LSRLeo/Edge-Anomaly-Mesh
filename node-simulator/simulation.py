import argparse
from src.node import Node
from src.route import Route
from redisFiles import redis_setup, redis_pub

def run_simulation(node_file, route_file, data_mode):
    route = Route(route_file)
    route.load_route()

    node = Node(node_file, route, data_mode)
    node.generate()
    node.publish()


def run_redis(rdis, channel_name):
    redis_pub.publish(rdis, channel_name)


def main():
    parser = argparse.ArgumentParser(description="Run simulation")
    subparsers = parser.add_subparsers(dest="command", required=True, help="sim or redis")

    sim_parser = subparsers.add_parser("sim", help="Run simulation from node and route config files")
    data_mode_group = sim_parser.add_mutually_exclusive_group(required=True)
    data_mode_group.add_argument(
        "-l", "--live",
        action="store_true",
        dest="live",
        help="Use live data",
    )
    data_mode_group.add_argument(
        "-t", "--training",
        action="store_true",
        dest="training",
        help="Use training data",
    )
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
        data_mode = "live" if args.live else "training"
        run_simulation(args.node, args.route, data_mode)
    elif args.command == "redis":
        rdis = redis_setup.connect(args.host, args.port)
        run_redis(rdis, args.channel_name)


if __name__ == "__main__":
    main()