# classes.py
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
    def __init__(self, host, port, id=None, callback=None, max_connections=0, initial_blockchain=None):
        super().__init__(host, port, id, callback, max_connections)
        self.generate_keys()
        self.mempool = []
        if initial_blockchain:
            self.blockchain = initial_blockchain
        else:
            self.blockchain = [
                self.create_genesis_block()]  # Initialize blockchain for all nodes
        self.last_blockchain_hash = self.hash_blockchain()  # Store initial hash

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
        print("node_message from " + node.id + ": " + str(data))
        if isinstance(data, dict) and data.get("type") == "transaction":
            self.receive_transaction(data["data"])
            if isinstance(self, Miner):
                self.mine()
        elif isinstance(data, dict) and data.get("type") == "new_block":
            self.receive_block(data["data"])

    def send_blockchain_to_nodes(self):
        """Sends the blockchain to all connected nodes if it has changed."""
        current_hash = self.hash_blockchain()
        if current_hash != self.last_blockchain_hash:
            message = {"type": "blockchain", "data": [
                block.to_dict() for block in self.blockchain]}
            self.send_to_nodes(message)
            self.last_blockchain_hash = current_hash
            print(f"Node {self.id} sent new blockchain to peers.")

    def send_to_nodes(self, data, exclude=[], compression='none'):
        message_to_be_sent = data
        print(f"The message is {message_to_be_sent}")
        return super().send_to_nodes(data=message_to_be_sent, exclude=exclude,
                                    compression=compression)

    def get_blockchain(self):
        return self.blockchain

    def create_genesis_block(self):
        genesis_header = Header(
            prev_block="0" * 64,
            merkle_root="0" * 64,
            timestamp=int(time.time()),
            target="00",
            nonce=0
        )
        return Block(
            index=0,
            header=genesis_header,
            txs=[],
            tx_count=0,
            target="00",
            nonce=0
        )

    def create_transaction(self, sender, recipient, amount):
        transaction = Transaction(
            tx_id=str(uuid.uuid4()),
            inputs=[{"sender": sender, "amount": amount}],
            outputs=[{"recipient": recipient, "amount": amount}]
        )
        self.mempool.append(transaction)
        self.propagate_transaction(transaction)
        return transaction

    def propagate_transaction(self, transaction):
        message = {"type": "transaction", "data": transaction.to_dict()}
        self.send_to_nodes(message)

    def receive_transaction(self, tx_data):
        transaction = Transaction.from_dict(tx_data)
        print(f"Node {self.id} received transaction: {transaction.tx_id}")
        if transaction not in self.mempool:
            self.mempool.append(transaction)
            print(
                f"Node {self.id} received and added transaction: {transaction.tx_id}")
        else:
            print(
                f"Node {self.id} received duplicate transaction: {transaction.tx_id}")

    def receive_block(self, block_data):
        block = Block.from_dict(block_data)
        if self.validate_tx(block):
            self.blockchain.append(block)
            print(f"Node {self.id} received and added block {block.index}")
            self.remove_transactions_from_mempool(block.txs)
            self.send_blockchain_to_nodes()  # Notify peers of the updated chain
        else:
            print(f"Node {self.id} received an invalid block")

    # def save_transactions(self, transactions):
    #     filename = "transactions.json"
    #     existing_transactions = []
    #     if os.path.exists(filename):
    #         with open(filename, 'r') as f:
    #             existing_transactions = json.load(f)
    #     new_transactions = [tx.to_dict() for tx in transactions]
    #     all_transactions = existing_transactions + new_transactions

        with open(filename, 'w') as f:
            json.dump(all_transactions, f, indent=2)

    def remove_transactions_from_mempool(self, transactions):
        for tx in transactions:
            self.mempool = [
                mempool_tx for mempool_tx in self.mempool if
                mempool_tx.tx_id != tx.tx_id]

    def validate_tx(self, block):
        merkle_root = self.calculate_merkle_root(block.txs)
        if merkle_root != block.header.merkle_root:
            return False

        block_hash = self.hash_block(block)
        if not block_hash.startswith(
                '0' * 2):  # Check the difficulty (e.g., 2 leading zeros)
            return False

        for tx in block.txs:
            if not all(
                    hasattr(tx, field) for field in ['tx_id', 'inputs', 'outputs']):
                return False

            if not isinstance(tx.inputs,
                               list) or not all(
                isinstance(input_, dict) and all(
                    k in input_ for k in ['sender', 'amount']) for input_ in
                tx.inputs):
                return False

            if not isinstance(tx.outputs,
                               list) or not all(
                isinstance(output_, dict) and all(
                    k in output_ for k in ['recipient', 'amount']) for output_ in
                tx.outputs):
                return False

            if any(input_['amount'] < 0 for input_ in tx.inputs) or any(
                    output_['amount'] < 0 for output_ in tx.outputs):
                return False

        return True

    def calculate_merkle_root(self, transactions):
        if not transactions:
            return "0" * 64
        return sha256(''.join(tx.tx_id for tx in transactions).encode()).hexdigest()

    def hash_block(self, block):
        block_string = json.dumps(dataclasses.asdict(block), sort_keys=True)
        return sha256(block_string.encode()).hexdigest()

    def hash_blockchain(self):
        """Hashes the entire blockchain to detect changes."""
        blockchain_string = json.dumps(
            [block.to_dict() for block in self.blockchain], sort_keys=True)
        return sha256(blockchain_string.encode()).hexdigest()


class Miner(notACoin_node):
    def __init__(self, host, port, id=None, callback=None, max_connections=0, initial_blockchain=None):
        super().__init__(host, port, id, callback, max_connections, initial_blockchain)

    def mine(self):
        new_block = self.create_block()
        while not self.is_valid_proof(new_block):
            new_block.nonce += 1
        self.blockchain.append(new_block)
        # self.save_transactions(new_block.txs)
        self.remove_transactions_from_mempool(new_block.txs)
        print(f"Node {self.id} mined a new block with {len(new_block.txs)} transactions")
        self.send_blockchain_to_nodes()  # Notify peers of the updated chain
        return new_block

    def is_valid_proof(self, block):
        block_hash = self.hash_block(block)
        return block_hash.startswith('0' * 2)

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


@dataclass
class Header:
    prev_block: str
    merkle_root: str
    timestamp: int
    target: str
    nonce: int

    def to_dict(self):
        return dataclasses.asdict(self)

    @classmethod
    def from_dict(cls, data):
        return cls(**data)


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

    def to_dict(self):
        return dataclasses.asdict(self)

    @classmethod
    def from_dict(cls, data):
        header_data = data['header']
        header = Header.from_dict(header_data)
        txs = [Transaction.from_dict(tx_data) for tx_data in data['txs']]
        return cls(
            index=data['index'],
            header=header,
            txs=txs,
            tx_count=data['tx_count'],
            target=data['target'],
            nonce=data['nonce']
        )


@dataclass
class Message:
    pubkey: str
    timestamp: float
    data: str


@dataclass
class Command(Message):
    pass