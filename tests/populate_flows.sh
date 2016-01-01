#!/bin/bash
sudo ovs-ofctl del-flows s2
sudo ovs-ofctl del-flows s1
sudo ovs-ofctl del-flows s3
sudo ovs-ofctl del-flows s4
sudo ovs-ofctl add-flow s1 in_port=1,actions=output:2
sudo ovs-ofctl add-flow s1 in_port=2,actions=output:1
sudo ovs-ofctl add-flow s3 in_port=1,actions=output:2
sudo ovs-ofctl add-flow s3 in_port=2,actions=output:1
sudo ovs-ofctl add-flow s2 in_port=2,actions=output:1
sudo ovs-ofctl add-flow s2 in_port=1,actions=output:2



#sudo ovs-ofctl add-flow s1 in_port=1,actions=output:3
#sudo ovs-ofctl add-flow s1 in_port=3,actions=output:1
#sudo ovs-ofctl add-flow s4 in_port=1,actions=output:2
#sudo ovs-ofctl add-flow s4 in_port=2,actions=output:1
#sudo ovs-ofctl add-flow s2 in_port=3,actions=output:2
#sudo ovs-ofctl add-flow s2 in_port=2,actions=output:3

