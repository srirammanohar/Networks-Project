#!/usr/bin/python
from mininet.net import Mininet
from mininet.node import Controller, RemoteController, OVSController
from mininet.node import CPULimitedHost, Host, Node
from mininet.node import OVSKernelSwitch, UserSwitch
from mininet.node import IVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink, Intf
import networkx as nx

from zookeeper_wrapper import ZooKeeperWrapper
from subprocess import call
import random

from singleton import *
import time


def find_shortest_path(graph,start,end,path=[]):
    path = path + [start]
    if start == end:
        return path
    if not graph.has_key(start):
        return None
    shortest = None
    for node in graph[start]:
        if node not in path:
            newpath = find_shortest_path(graph, node, end, path)
            if newpath:
                if not shortest or len(newpath) < len(shortest):
                    shortest = newpath
    return shortest

def addFlowRules(net,path,controller):
    Flow_path=[]
    first_port=0
    last_port=0
    l=str(net.links[-2])
    switch_port=l.split('-')[1][3]
    first_port=switch_port
    l=str(net.links[-1])
    last_switch=l.split('-')[0]
    switch_port=l.split('-')[1][3]
    last_port=switch_port
    prev_port=first_port
    info('path:'+str(path)+'\n')

    for i in range(1,len(path)-2):
        for link in net.links:
            if ((path[i] in str(link)) and (path[i+1] in str(link))):
                switches=str(link).split('<->')
                if(switches[0].split('-')[0]==path[i]):
                    switch1=switches[0].split('-')[0]
                    switch4=switches[1].split('-')[0]
                    switch1_port=switches[0][-1]
                    switch2_port=switches[1][-1]
                else:
                    switch2=switches[0].split('-')[0]
                    switch1=switches[1].split('-')[0]
                    switch2_port=switches[0][-1]
                    switch1_port=switches[1][-1]
                info('link:'+str(link)+'\n')
                controller.cmd('ovs-ofctl add-flow '+switch1+' in_port='+prev_port+',actions=output:'+switch1_port)
                info('ovs-ofctl add-flow '+switch1+' in_port='+prev_port+',actions=output:'+switch1_port+'\n')
                controller.cmd('ovs-ofctl add-flow '+switch1+' in_port='+switch1_port+',actions=output:'+prev_port)
                info('ovs-ofctl add-flow '+switch1+' in_port='+switch1_port+',actions=output:'+prev_port+'\n')
                prev_port=switch2_port
                break

    controller.cmd('ovs-ofctl add-flow '+last_switch+' in_port='+prev_port+',actions=output:'+last_port)
    info('ovs-ofctl add-flow '+last_switch+' in_port='+prev_port+',actions=output:'+last_port+'\n')
    controller.cmd('ovs-ofctl add-flow '+last_switch+' in_port='+last_port+',actions=output:'+prev_port)
    info('ovs-ofctl add-flow '+last_switch+' in_port='+last_port+',actions=output:'+prev_port+'\n')

def simulateLinkFailure(path):
    #global graph_extern
    k = random.randint(1,len(path)-3)
    a = path[k]
    b = path[k+1]
    graph_extern.remove_edge(a,b)
    # graph_extern.remove_edge(b,a)
    # graph_extern[path[k]].remove(path[k+1])
    # graph_extern[path[k+1]].remove(path[k])
#Adding random topology
def myNetwork():
    info( '*** Creating the initial Mininet object ***\n')
    net = Mininet( topo=None,
                   build=False,
                   ipBase='10.0.0.0/8')

    info( '*** Adding controller ***\n' )
    c0 = net.addController(name='c0',
                           controller=RemoteController,
                           ip='127.0.0.1',
                           protocol='tcp',
                           port=6633)

    info( '*** Add switches ***\n' )
    for i in range(1, NUM_SWITCHES + 1):
        mininetswitch[i] = '%s%d' % ('s', i)
        net.addSwitch(mininetswitch[i], cls=OVSKernelSwitch)

    for i in range(NUM_SWITCHES + 1):
        graph_extern.add_node(mininetswitch[i])
    if RUN_FIRSTTIME==0:
        for i in range(1, NUM_SWITCHES + 1):
            for j in range(1, NUM_SWITCHES + 1):
                if i == j:
                    continue
                k = random.randint(0, 5)#probability of 4/5
                if k == 0:
                    continue
                if k == 1:
                    continue
                if k == 2:
                    continue
                if mininetswitch[j] not in graph_extern[mininetswitch[i]]:
                    b = random.choice(BANDWIDTHS)
                    graph_extern.add_edge(mininetswitch[i],mininetswitch[j],weight=b)
                    graph_extern.add_edge(mininetswitch[j],mininetswitch[i],weight=b)
                    net.addLink(mininetswitch[i], mininetswitch[j], cls=TCLink, bw=b)
        g=open("savedgraph2", 'w')
        for e in graph_extern.edge:
            for q in graph_extern.edge[e]:
                g.write(str(e)+';'+str(q)+';'+str(graph_extern.edge[e][q])+'\n')
        g.close()
    if RUN_FIRSTTIME==1:
        oldnodes=set()
        for l in open('savedgraph2'):
            n1,n2,w=l.split(';')
            wr,wv=w.split(":")
            wv=wv.strip(' ')
            wv=wv.strip('\n')
            wv=wv.strip('}')
            v=int(wv)
            graph_extern.add_edge(n1,n2,weight=v)
            graph_extern.add_edge(n2,n1,weight=v)
            net.addLink(n1, n2, cls=TCLink, bw=v)
            oldnodes.add(n1)
            oldnodes.add(n2)
        if len(oldnodes) < NUM_SWITCHES:
            for nn in range(len(oldnodes),NUM_SWITCHES+1):
                for o in range(1, NUM_SWITCHES + 1):
                    if o == nn:
                        continue
                    k = random.randint(0, 5)#probability of 4/5
                    if k == 0:
                        continue
                    if k == 1:
                        continue
                    if k == 2:
                        continue
                    if mininetswitch[o] not in graph_extern[mininetswitch[nn]]:
                        b = random.choice(BANDWIDTHS)
                        graph_extern.add_edge(mininetswitch[o],mininetswitch[nn],weight=b)
                        graph_extern.add_edge(mininetswitch[nn],mininetswitch[o],weight=b)
                        net.addLink(mininetswitch[nn], mininetswitch[o], cls=TCLink, bw=b)
        g=open("savedgraph3", 'w')
        for e in graph_extern.edge:
            for q in graph_extern.edge[e]:
                g.write(str(e)+';'+str(q)+';'+str(graph_extern.edge[e][q])+'\n')
        g.close()

    info( '*** Add hosts ***\n' )
    h1 = net.addHost('h1', cls=Host, ip='10.0.0.1', defaultRoute=None)
    h2 = net.addHost('h2', cls=Host, ip='10.0.0.2', defaultRoute=None)

    # Source and Destination will always be mininet switches 1 and 2
    src = mininetswitch[1]
    dest = mininetswitch[2]

    net.addLink(mininetswitch[1], h1)
    net.addLink(mininetswitch[2], h2)

    info( '*** Starting network ***\n' )
    net.build()

    info( '*** Starting controllers ***\n' )
    for controller in net.controllers:
        controller.start()

    info( '*** Starting switches ***\n' )
    for i in range(1, NUM_SWITCHES + 1):
        net.get('%s%d' % ('s', i)).start([c0])

    info( '*** Post configure switches and hosts ***\n' )
    #path = find_shortest_path(graph_extern, src, dest)
    path = netshortestpath(src, dest)
    path.insert(0, 'h1')
    path.append('h2')

    addFlowRules(net,path,c0)
    info('old_graph'+str(graph_extern)+'\n')
    info('old_path:'+str(path)+'\n')
    startlinkfail = time.clock()
    simulateLinkFailure(path)


    path.remove('h1')
    path.remove('h2')

    # Code to integrate with ZooKeeper
    # Create the ZooKeeperWrapper helper object
    helper = ZooKeeperWrapper()
    # Create the Kazoo instance. Used for interacting with ZooKeeper
    zk = helper.initializeZooKeeperClient()
    # Start the Kazoo instance
    helper.startOperation(zk)
    # Ensure that the ZooKeeper nodes are present before we start working
    helper.ensurePathPresence(zk)
    # The admins give out their preference
    # Get a random ordering of the administrators
    admin_order = random.sample(range(1, 4), 3)
    for admin in admin_order:
        helper.implementAdminLocking(zk, admin)

    data, stat = helper.getNodeData(zk, DATA_PATH)
    new_path, score = convertToConfig(data)

    new_path = new_path.split(",")
    stoplinkfail1 = time.clock()
    print("Time taken for ZooKeeper to reach a consensus:%s"%(stoplinkfail1-startlinkfail))


    new_path.insert(0, 'h1')
    new_path.append('h2')


    info('new_graph'+str(graph_extern)+'\n')
    info('new_path'+str(new_path)+'\n')
    addFlowRules(net,new_path,c0)
    stoplinkfail2 = time.clock()
    print("Time taken to add new flow rules from time of link failure:%s"%(stoplinkfail2-startlinkfail))
    g1=open("TimeZookeeperConsensus", 'a')
    g2=open("TimeFlowrulesAdded",'a')
    g3=open("Zookeeper-flowrulesadded",'a')
    g1.write(str(NUM_SWITCHES)+" "+str(stoplinkfail1-startlinkfail)+"\n")

    g2.write(str(NUM_SWITCHES)+" "+str(stoplinkfail2-startlinkfail)+"\n")

    g3.write(str(NUM_SWITCHES)+" "+str(stoplinkfail2-stoplinkfail1)+"\n")
    CLI(net)
    net.stop()



    # The Zookeeper helper needs to be stopped
    helper.stopOperation(zk)

if __name__ == '__main__':
    setLogLevel( 'info' )
    myNetwork()