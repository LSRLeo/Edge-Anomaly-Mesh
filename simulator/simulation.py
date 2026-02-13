import argparse
from node import Node
from route import Route

def run_simulation(node_file, route_file):
    
    route = Route(route_file)
    route.load_route()

    node = Node(node_file, route)
    node.generate()
    node.publish()

def main():
    parser = argparse.ArgumentParser(description='Run simulation')
    
    parser.add_argument('-n', '--node', 
                       type=str, 
                       required=True,
                       help='JSON file name for node configuration')
    
    parser.add_argument('-r', '--route', 
                       type=str, 
                       required=True,
                       help='JSON file name for route configuration')
    
    args = parser.parse_args()
    
    run_simulation(args.node, args.route)


if __name__ == '__main__':
    main()