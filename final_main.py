import time
import json
from classes import Miner, Transaction
import random
import threading

nodes = [
    Miner('127.0.0.1', 10001),
    Miner('127.0.0.1', 10002),
    Miner('127.0.0.1', 10003),
    Miner('127.0.0.1', 10004),
    Miner('127.0.0.1', 10005)
]

# Start all nodes
for node in nodes:
    node.start()
    time.sleep(1)  # Wait a bit between starting each node

    # Connect all nodes to peers
for node in nodes:
    print(f"Node {node.id} connecting to peers:")
    node.connect_to_peers()
    time.sleep(1)
