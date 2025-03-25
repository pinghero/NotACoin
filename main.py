import time
import json
from classes import Miner, Transaction
import random
import threading


def send_delayed_transaction(sender_node, recipient_node, amount, delay):
    return 0


def send_delayed_transaction(sender_node, recipient_node, amount, delay):
    time.sleep(delay)
    transaction = sender_node.create_transaction(sender_node.id, recipient_node.id, amount)
    if transaction:
        print(f"\nTransaction created after {delay} seconds:")
        print(f"Node {sender_node.id} sent {amount} coins to Node {recipient_node.id}")
        print(f"Transaction ID: {transaction.tx_id}")


def simulate_transactions(nodes, num_transactions):
    for _ in range(num_transactions):
        sender_node = random.choice(nodes)
        recipient_node = random.choice(nodes)
        while recipient_node == sender_node:
            recipient_node = random.choice(nodes)

        amount = random.randint(1, 100)
        transaction = sender_node.create_transaction(sender_node.id, recipient_node.id, amount)
        if transaction:
            print(f"Transaction created: {sender_node.id} sent {amount} coins to {recipient_node.id}")
        time.sleep(1)


def mine_blocks(node, num_blocks):
    for _ in range(num_blocks):
        block = node.mine()
        print(f"Node {node.id} mined a new block with {len(block.txs)} transactions")
        time.sleep(1)


if __name__ == '__main__':
    # Initialize 5 miner nodes
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

    # Schedule a transaction to be sent after 10 seconds
    sender_node = nodes[0]
    recipient_node = nodes[1]
    amount = 50
    threading.Thread(target=send_delayed_transaction, args=(sender_node, recipient_node, amount, 10)).start()

    # Simulate some initial transactions
    print("\nSimulating initial transactions...")
    simulate_transactions(nodes, 5)

    # Mine some blocks
    print("\nMining blocks...")
    for node in nodes:
        threading.Thread(target=mine_blocks, args=(node, 2)).start()

    # Keep the program running and periodically print mempool contents
    try:
        while True:
            time.sleep(5)
            print("\nMempool contents:")
            for node in nodes:
                print(f"Node {node.id} mempool: {len(node.mempool)} transactions")
            print("\nBlockchain length:")
            for node in nodes:
                print(f"Node {node.id} blockchain: {len(node.blockchain)} blocks")
    except KeyboardInterrupt:
        print("\nStopping the network...")
        for node in nodes:
            node.stop()
        print("Network stopped.")
