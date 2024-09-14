from p2pnetwork.node import Node
import json
import time


class p2p_node(Node):
    def __init__(self, host, port, id=None, callback=None, max_connections=0):

        super(p2p_node, self).__init__(
            host, port, id, callback, max_connections)
        self.peers_list = []

    def outbound_node_connected(self, connected_node):
        print("outbound_node_connected: " + connected_node.id)

    def connect_to_peers(self):

        peers_list = self.get_peers_list()
        # for peer in peers_list:
        self.connect_with_node(peers_list['host'], peers_list['port'])

    def get_peers_list(self, peers_list: list = []):

        # Reading peer from file for testing
        with open('peers.json', 'r') as peers:
            return json.load(peers)

    def node_message(self, node, data):
        print("node_message from " + node.id + ": " + str(data))


# testing p2p network
if __name__ == '__main__':

    node1 = p2p_node('127.0.0.1', 10001)
    node2 = p2p_node('127.0.0.1', 10002)

    node1.start()
    time.sleep(1)

    node2.start()
    time.sleep(1)

    peers_list = node1.get_peers_list()
    node1.connect_with_node(peers_list['host'], int(peers_list['port']))

    # node1.connect_to_peers()
    node1.send_to_nodes({"message": "hello"})
