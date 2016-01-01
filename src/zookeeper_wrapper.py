"""
Use this file to maintain and develop ZooKeeper specific functionality
"""

import logging
from functools import wraps
from kazoo.client import KazooClient

import random
from swi_layer import initiateVoting
from singleton import *

class ZooKeeperWrapper(object):
    def startLogging(self):
        # If the application is not making use of the Python logging module then Kazoo
        # throws an error message - No handlers could be found for logger "kazoo.client"
        # To avoid this we use this basic recipie
        logging.basicConfig()

    def createZooKeeperClient(self):
        # Create an instance of a kazoo client and pass it back to the user
        zk = KazooClient(HOST_PORT_COMBO)
        return zk

    def initializeZooKeeperClient(self):
        # A helper which calls both the methods - createZooKeeperClient and startLogging
        # Ideally both are part of the initialization phase and there should be just
        # function within the class that calls both of them
        zk = self.createZooKeeperClient()
        self.startLogging()
        return zk

    def startOperation(self, zk):
        # Used for starting the kazoo client
        zk.start()

    def stopOperation(self, zk):
        # Used for stopping the kazoo client
        zk.stop()

    def callEnsurePath(self, zk, path):
        # Makes sure that path is present before working on it
        zk.ensure_path(path)

    def callCreatePath(self, zk, path, value="", ephemeral=False, makepath=False):
        # Used for creating a ZooKeeper node
        zk.create(path, value=value, ephemeral=ephemeral, makepath=makepath)

    def checkIfNodeExists(self, zk, node):
        # Used for checking if a Zookeeper node exists
        if zk.exists(node):
            return True
        else:
            return False

    def ensurePathPresence(self, zk):
        # Ensure that all the node are created the way you want them to before work starts
        # If there is any stale data at the DATA_PATH ZooKeeper node then start afresh by
        # deleting it
        if self.checkIfNodeExists(zk, DATA_PATH):
            self.deleteNodes(zk, DATA_PATH)
        print("Creating the data node %s" % (DATA_PATH))
        self.callCreatePath(zk, DATA_PATH, makepath=True)
        # Check if the lock node is present
        if not self.checkIfNodeExists(zk, LOCK_PATH):
            print("Creating the lock node %s" % (LOCK_PATH))
            self.callCreatePath(zk, LOCK_PATH, makepath=True)
        else:
            print("The lock node %s is already present" % LOCK_PATH)

    def getNodeData(self, zk, node):
        # Blocking get - Gets the current data snapshot
        data, stat = zk.get(node)
        return (data, stat)

    def setNodeData(self, zk, node, data):
        # Used to write data at a particular node
        zk.set(node, data)

    def deleteNodes(self, zk, node, recursive=True):
        # Used for deleting a particular ZooKeeper node
        zk.delete(node, recursive=recursive)

    def implementAdminLocking(self, zk, admin_name=1):
        # Acquire the Lock perform the set of the steps associated with an
        # admin, write the data in to the ZooKeeper node, notify the callback
        # and then release the lock
        lock = zk.Lock(LOCK_PATH, admin_name)
        with lock:
            print("Admin %s acquired the lock" % admin_name)
            initiateVoting(self, zk, admin_name)
            lock.release()
        print("Done with admin - %s logic" % admin_name)

def main():
    # - Create the ZooKeeperWrapper helper object
    helper = ZooKeeperWrapper()
    # - Create the Kazoo instance. Used for interacting with ZooKeeper
    zk = helper.initializeZooKeeperClient()
    # - Start the Kazoo instance
    helper.startOperation(zk)
    # - Ensure that the ZooKeeper nodes are present before we start working
    helper.ensurePathPresence(zk)

    # - The admins give out their preferences
    admin_order = random.sample(range(1, 4), 3)
    for admin in admin_order:
        helper.implementAdminLocking(zk, admin)

    # - Stop the Kazoo instance at the very end
    helper.stopOperation(zk)

if __name__ == '__main__':
    main()
