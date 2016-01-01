import networkx as nx
import copy

from administrators import cast_vote
from singleton import *

def initiateVoting(helper, zk, admin_name):
    # Get the current configuration stored in ZooKeeper
    data, stat = helper.getNodeData(zk, DATA_PATH)
    path, score = convertToConfig(data)

    # - Let admin get his configuration
    admin_path, admin_score = cast_vote(admin_name)

    if admin_score > score:
        temp = get_weight(admin_path)
        if(admin_score == temp):
            print("The current confidence score is %d while admin %s has a configuration "
              "with a higher confidence score %d" % (score, admin_name, admin_score))
            print("Will store the configuration %s with confidence score %s"
              % (admin_path, admin_score))
            to_store = (admin_path, admin_score)
            byte_data = bytes(to_store)

            helper.setNodeData(zk, DATA_PATH, byte_data)
        else:
            print("The score was faked.Hence, its not updated as the best path")
    else:
        print("The current confidence score is %d while admin %s has a configuration "
              "with a lower confidence score %d" % (score, admin_name, admin_score))
        print("Not allowing the admin %s to submit his configuration" % admin_name)
