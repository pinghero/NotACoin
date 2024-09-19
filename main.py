import time
import json
from classes import Miner, Message

if __name__ == '__main__':

    node1 = Miner('127.0.0.1', 10001)
    node2 = Miner('127.0.0.1', 10002)

    node1.start()
    time.sleep(1)

    node2.start()
    time.sleep(1)

    print(node1.connect_to_peers())
    time.sleep(1)

    node1.send_to_nodes(json.dumps({"data": "you are gae"}))
    time.sleep(1)

    node2.send_to_nodes(json.dumps({"data": "message from node 2"}))
