from p2pnetwork.node import Node
from dataclasses import dataclass
import json
import time
from hashlib import sha256
import ecdsa


class notACoin_node(Node):
    def __init__(self, host, port, id=None, callback=None, max_connections=0):
        # Call super constructor
        super().__init__(
            host,
            port,
            id,
            callback,
            max_connections)

        self.generate_keys()

    # Generates public/private key for message encryption
    def generate_keys(self):
        self.private_key = ecdsa.SigningKey.generate(
            curve=ecdsa.SECP256k1, hashfunc=sha256)
        self.public_key = self.private_key.get_verifying_key()

    def get_peers_list(self):

        # Reading peers from local file
        with open('peers.json', 'r') as peers:
            return json.load(peers)

    def connect_to_peers(self, peers_list: dict = {}):

        if not peers_list:
            peers_list = self.get_peers_list()

        for peer in peers_list['peers']:
            self.connect_with_node(peer['host'], peer['port'])

    def node_message(self, node, data):
        print("testes")
        # print(f"{data} FROM NODE {node}")
        # print("node_message from " + node.id + ": " + str(data))

    def send_to_node(self, n, data, compression='none'):
        message_to_be_sent = data

        # Encrypt message data with private key
        data_bytes = str.encode(message_to_be_sent)

        signed_data = self.private_key.sign(data_bytes)

        signed_message = Message(
            data=signed_data, pubkey=self.public_key, timestamp=time.time())

        # Use default send method to send encrypted data
        return super().send_to_node(data=signed_message,
                                    n=n,
                                    compression=compression)


class Miner(notACoin_node):
    def __init__(self, host, port, id=None, callback=None, max_connections=0):

        # Call super constructor
        super().__init__(
            host,
            port,
            id,
            callback,
            max_connections)

        self.mempool = []
        self.blockchain = []
        self.addr = []
        self.connected_peers = []

    # Initialize empty memory pool
    def init_mempool(self):
        return None

    # Validate transaction
    def validate_tx(self):
        return None

    # Mine block
    def mine(self):
        return None


# Header structure
@ dataclass
class Header:
    prev_block: str
    merkle_root: str
    timestamp: str
    target: str
    nonce: int


# Transaction class
class Transaction:
    def __init__(self):

        self.input_count: int
        self.inputs: list
        self.output_count: str
        self.outputs: list


# Block class
class Block:
    def __init__(self):

        self.index: int
        self.header: Header
        self.txs: str
        self.tx_count: int
        self.target: str
        self.nonce: int

    # Genesis block
    def create_genesis_block(self):
        return


class Message:
    def __init__(self, data, timestamp, pubkey):
        if not data:
            # Exception handling
            return
        self.pubkey = pubkey
        self.timestamp = timestamp
        self.data = data
