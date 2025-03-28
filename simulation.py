import time
from classes import Miner
import random


def send_dummy_transaction():
    """Sends one dummy transaction from the first node to the other nodes."""
    # Initialize a temporary node to send the transaction
    # Use a unique port
    sender_node = Miner('127.0.0.1', 20000, id='TransactionSender')
    sender_node.start()
    time.sleep(2)  # Give the sender node time to start

    # Connect to the miners (assuming they are running on 10001-10005)
    miner_ports = [10001, 10002, 10003, 10004, 10005]
    for port in miner_ports:
        sender_node.connect_with_node('127.0.0.1', port)
        time.sleep(1)  # Add a delay

    # wait to connect
    time.sleep(5)

    # Send the transaction
    amount = 10
    recipient_node_id = "127.0.0.1:10001"  # send it to the first miner
    tx = sender_node.create_transaction(
        sender_node.id, recipient_node_id, amount)
    if tx:
        print(
            f"Sent dummy transaction from {sender_node.id} to {recipient_node_id}, tx_id: {tx.tx_id}")
    else:
        print("Failed to create transaction")

    time.sleep(2)  # Give time for the transaction to propagate

    sender_node.stop()  # Stop the sender node
    print("Transaction sent.  Exiting simulation.")


if __name__ == '__main__':
    send_dummy_transaction()
