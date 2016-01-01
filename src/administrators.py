import networkx as nx
import copy

from singleton import *

def vote(src,dest,intent):
    path = []
    confidence = 0

    if(intent == 0): #Good Guy. Non Malicious
        path = netshortestpath(src ,dest)
        confidence = get_weight(path)
        #path,confidence=BestBottleneckPath(src,dest)
        return (path,confidence)

    if(intent == 1):          #Evil Guy. malicious
        for paths in nx.all_simple_paths(graph_extern, src, dest):
            temp= get_weight(paths)
            if (temp>confidence):
                confidence = temp
                path = copy.deepcopy(paths)
        #return shortest path weigth -1

        return (path,(get_weight(netshortestpath(src, dest))-1))

    if(intent == 2):          #Good Guy. mis-configured
        for paths in nx.all_simple_paths(graph_extern, src, dest):
            temp= get_weight(paths)
            if (temp>confidence):
                confidence = temp
                path = copy.deepcopy(paths)
                break
        #return shortest path weigth -1
        return (path,confidence)



def cast_vote(admin):
    if(admin == 1):
        path, conf = vote(mininetswitch[1], mininetswitch[2], 0)
    elif(admin == 2):
        path, conf = vote(mininetswitch[1], mininetswitch[2], 1)
    elif(admin == 3):
        path, conf = vote(mininetswitch[1], mininetswitch[2], 2)

    return (path, conf)
