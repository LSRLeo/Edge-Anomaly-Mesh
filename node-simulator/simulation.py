import argparse
from src.node import Node
from src.route import Route


def run_simulation(node_file, route_file):
    route = Route(route_file)
    route.load_route()

    node = Node(node_file, route)
    node.generate()
    node.publish()


def run_redis():
    # Placeholder for Redis-based flow
    pass


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

    subparsers.add_parser("redis", help="Run with Redis (placeholder)")

    args = parser.parse_args()

    if args.command == "sim":
        run_simulation(args.node, args.route)
    elif args.command == "redis":
        run_redis()


if __name__ == "__main__":
    main()