from node import Node

def main():
    node = Node("node_001", "IDLE")
    message = node.generate_message()
    print(message)

if __name__ == "__main__":
    main()