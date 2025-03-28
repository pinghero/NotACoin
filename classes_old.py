from p2pnetwork.node import Node
from dataclasses import dataclass
import json
import time
from hashlib import sha256
import ecdsa
import dataclasses
import uuid
import os


class notACoin_node(Node):
    def __init__(self, host, port, id=None, callback=None, max_connections=0):
        super().__init__(host, port, id, callback, max_connections)
        self.generate_keys()

    def generate_keys(self):
        self.private_key = ecdsa.SigningKey.generate(
            curve=ecdsa.SECP256k1, hashfunc=sha256)
        self.public_key = self.private_key.get_verifying_key()

    def get_peers_list(self):
        with open('peers.json', 'r') as peers:
            return json.load(peers)

    def connect_to_peers(self, peers_list: dict = {}):
        if not peers_list:
            peers_list = self.get_peers_list()
        for peer in peers_list['peers']:
            self.connect_with_node(peer['host'], peer['port'])

    def node_message(self, node, data):
        print(f"{data} FROM NODE {node}")
        print("node_message from " + node.id + ": " + str(data))

    def send_to_nodes(self, data, exclude=[], compression='none'):
        message_to_be_sent = data
        print(f"The message is {message_to_be_sent}")
        return super().send_to_nodes(data=message_to_be_sent, exclude=exclude, compression=compression)


class Miner(notACoin_node):
    def __init__(self, host, port, id=None, callback=None, max_connections=0):
        super().__init__(host, port, id, callback, max_connections)
        self.mempool = self.init_mempool()
        self.blockchain = [self.create_genesis_block()]
        self.addr = []
        self.connected_peers = []

    def get_blockchain(self):
        return self.blockchain

    def init_mempool(self):
        return []

    def validate_tx(self, tx):
        return True

    def is_unspent(self, tx_input):
        return True

    def get_input_value(self, tx_input):
        return 10

    def mine(self):
        new_block = self.create_block()
        while not self.is_valid_proof(new_block):
            new_block.nonce += 1
        self.blockchain.append(new_block)
        self.save_transactions(new_block.txs)
        self.mempool = []
        return new_block

    def is_valid_proof(self, block):
        block_hash = self.hash_block(block)
        return block_hash.startswith('0' * 2)

    def hash_block(self, block):
        block_string = json.dumps(dataclasses.asdict(block), sort_keys=True)
        return sha256(block_string.encode()).hexdigest()

    def create_block(self):
        prev_block = self.blockchain[-1]
        index = len(self.blockchain)
        transactions = self.mempool[:10]
        merkle_root = self.calculate_merkle_root(transactions)
        timestamp = int(time.time())
        target = "00"
        nonce = 0

        header = Header(
            prev_block=self.hash_block(prev_block),
            merkle_root=merkle_root,
            timestamp=timestamp,
            target=target,
            nonce=nonce
        )

        return Block(
            index=index,
            header=header,
            txs=transactions,
            tx_count=len(transactions),
            target=target,
            nonce=nonce
        )

    def calculate_merkle_root(self, transactions):
        return sha256(''.join(str(tx) for tx in transactions).encode()).hexdigest()

    def create_genesis_block(self):
        genesis_header = Header(
            prev_block="0" * 64,
            merkle_root="0" * 64,
            timestamp=int(time.time()),
            target="00",  # Reduced difficulty (was "0000")
            nonce=0
        )
        return Block(
            index=0,
            header=genesis_header,
            txs=[],
            tx_count=0,
            target="00",  # Reduced difficulty (was "0000")
            nonce=0
        )

    def create_transaction(self, sender, recipient, amount):
        transaction = Transaction(
            tx_id=str(uuid.uuid4()),
            inputs=[{"sender": sender, "amount": amount}],
            outputs=[{"recipient": recipient, "amount": amount}]
        )
        if self.validate_tx(transaction):
            self.mempool.append(transaction)
            self.propagate_transaction(transaction)
            return transaction
        return None

    def propagate_transaction(self, transaction):
        message = {"type": "transaction", "data": transaction.to_dict()}
        self.send_to_nodes(message)

    def node_message(self, node, data):
        if isinstance(data, dict) and data.get("type") == "transaction":
            self.receive_transaction(data["data"])
        else:
            super().node_message(node, data)

    def receive_transaction(self, tx_data):
        transaction = Transaction.from_dict(tx_data)
        if self.validate_tx(transaction) and transaction not in self.mempool:
            self.mempool.append(transaction)
            print(
                f"Node {self.id} received and validated transaction: {transaction.tx_id}")
            self.propagate_transaction(transaction)  # Propagate to other nodes
        else:
            print(
                f"Node {self.id} received invalid or duplicate transaction: {transaction.tx_id}")

    def save_transactions(self, transactions):
        filename = "transactions.json"
        existing_transactions = []
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                existing_transactions = json.load(f)

        new_transactions = [tx.to_dict() for tx in transactions]
        all_transactions = existing_transactions + new_transactions

        with open(filename, 'w') as f:
            json.dump(all_transactions, f, indent=2)
        print(f"Saved {len(new_transactions)} transactions to {filename}")


@dataclass
class Header:
    prev_block: str
    merkle_root: str
    timestamp: int
    target: str
    nonce: int


@dataclass
class Transaction:
    tx_id: str
    inputs: list
    outputs: list

    def to_dict(self):
        return dataclasses.asdict(self)

    @classmethod
    def from_dict(cls, data):
        return cls(**data)


@dataclass
class Block:
    index: int
    header: Header
    txs: list
    tx_count: int
    target: str
    nonce: int


@dataclass
class Message:
    pubkey: str
    timestamp: float
    data: str


@dataclass
class Command(Message):
    pass
