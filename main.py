from p2pnetwork.node import Node
import json
import time
import pdb
from pow import calculate_hash
from dataclasses import dataclass


class p2p_node(Node):
    def __init__(self, host, port, id=None, callback=None, max_connections=0):

        super(p2p_node, self).__init__(
            host, port, id, callback, max_connections)
        self.peers_list = self.get_peers_list()

        # Debug flag - default False
        # self.debug = True

    def outbound_node_connected(self, node):
        print("outbound_node_connected: " + node.id)

    def connect_to_peers(self):

        for peer in self.peers_list['peers']:
            return self.connect_with_node(peer['host'], peer['port'])

    def get_peers_list(self, peers_list: list = []):

        # Reading peer from file for testing:
        with open('peers.json', 'r') as peers:
            return json.load(peers)

    def node_message(self, node, data):
        print("node_message from " + node.id + ": " + str(data))

    @dataclass
    class Block:
        header: str
        txs: str
        tx_count: int
        target: str
        nonce: int

    @dataclass
    class Header:
        prev_block: str
        merkle_root: str
        timestamp: str
        target: str
        nonce: int

    @dataclass
    class Transaction:
        input_count: int
        inputs: list
        output_count: str
        outputs: list


if __name__ == '__main__':

    string = 'some data'

    hash = calculate_hash(string)

    print(hash)

    # node1 = p2p_node('127.0.0.1', 10001)
    # node2 = p2p_node('127.0.0.1', 10002)

    # node1.start()
    # time.sleep(1)

    # node2.start()
    # time.sleep(1)

    # print(node1.connect_to_peers())
    # time.sleep(1)

    # node1.send_to_nodes({"message": "message from node 1"})
    # time.sleep(1)

    # node2.send_to_nodes({"message": "message from node 2"})
