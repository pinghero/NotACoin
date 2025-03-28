import time
import json
from classes import Miner
import threading
import socket  # Import the socket library
import sys    # Import the sys library


def start_miner(node):
    node.start()
    node.connect_to_peers()
    print(f"Miner {node.id} started and connected to peers.")

if __name__ == '__main__':
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print("Invalid port number provided.")
    else:
        # If no port is provided, find a free port
        print("No port provided.")

    # Initialize only one miner node with the given or found port
    node = Miner('127.0.0.1', port)
    
    node.start()
    node.connect_to_peers()
    print(f"Miner {node.id} started and connected to peers.")

    # Start the miner node
    # miner_thread = threading.Thread(target=start_miner, args=(node,))
    # miner_thread.daemon = True  # Allow the main thread to exit
    # miner_thread.start()

    print(f"Miner started on port {port}. This script should be left running.")
    print("Run simulation.py in another terminal to send a transaction.")

    try:
        while True:
            time.sleep(10)
            print(f"\nNode {node.id} Blockchain:")
            for block in node.blockchain:
                print(f"  Block Index: {block.index}")
                print(f"  Previous Block Hash: {block.header.prev_block}")
                print(f"  Merkle Root: {block.header.merkle_root}")
                print(f"  Timestamp: {block.header.timestamp}")
                print(f"  Nonce: {block.header.nonce}")
                print(
                    f"  Transactions: {len(block.txs)} (IDs: {[tx.tx_id for tx in block.txs]})")
                print(f"  Mempool: {node.mempool}")

    except KeyboardInterrupt:
        print("Stopping miner...")
        node.stop()
        print("Miner stopped.")