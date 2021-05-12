####################################################
# LSrouter.py
# Name: Nafis Abeer, Daniel Shimon
# BU ID: U98285639, U71376754
#####################################################

import sys
from collections import defaultdict
from router import Router
from packet import Packet
from json import dumps, loads
import networkx as nx
import time

class LSrouter(Router):
    """Link state routing protocol implementation."""

    def __init__(self, addr, heartbeatTime):
        """TODO: add your own class fields and initialization code here"""
        Router.__init__(self, addr)  # initialize superclass - don't remove
        self.heartbeatTime = heartbeatTime
        self.last_time = 0
        # Hints: initialize local state

        #forwarding table initialization
        self.forwarding_table = {} #forwarding table consisting of addresses to neighbors of current router. Index is the destination node, and value is port number

        #graph initialization
        self.G = nx.Graph() #Initialize a Graph that would map the neighbors of current router, Directed because there may be different weights to and from routers based on traffic
        self.G.add_node(str(addr)) #add crrent node initially to the Graph

        #link state initialization
        self.link_states = {} #The link state of a router contains the links and their weights between the router and its neighbors

        #Holds port numbers as values and endpoints as keys, and used to determine neighbors within link state
        self.new_links = {} #this holds names of neighbors as indices and their port numbers as values
        self.port_to_link = {} #this holds port numbers as indices and names of neighbors as values,
        self.link_costs = {} #this array holds the cost of immediate neighbors and any new link

        #sequence number initialization
        self.sequence_numbers = {} #this array holds the node this node is interacting with as indices and sequence numbers of the last encounter as the value
        self.last_seqnum = 0 #initialize last sequence number as 0 to start and it goes up after each broadcast

        pass

    #making dictionaries for endpoints and ports
    #when we get endpoint and port
    #self.endsNports["endpoint"] = port, to add
    #del self.endsNports["endpoint"], to delete

    def update_forwarding_table(self):
        #compute shortest path to destination addresses (clients with lower case names)
        for end_host in self.G.nodes():
            #check if node is lower case
            if end_host.islower():
                #calculate shortest path to the this end host
                #if there is a path to this host available
                if nx.has_path(self.G, self.addr, end_host):
                    path = nx.shortest_path(self.G, source = self.addr, target = end_host, weight = "cost")
                    if path[1] in self.new_links:
                        #if if the first router in this path is a neighbor
                        #add the port number to the forwarding table at index 'endhost'
                        #since the forwarding table is a dictionary, it would just update the info for the given end point
                        port_of_endhost = self.new_links[path[1]]
                        self.forwarding_table[end_host] = port_of_endhost
                else:
                    #if there is no known path to this end host
                    if end_host in self.forwarding_table:
                        #if the forwarding table had a previous path to this end host
                        #remove this end host from the forwarding table
                        del self.forwarding_table[end_host]

    def my_neighbors(self):
        neighbors = {}
        # neighbors['source'] = self.addr //we'll do this when we tag packets with a sequence number

        # for every known port numbers we have
        # see which endpoint that port belongs to
        # get the corresponding cost to that end point
        # form a dictionary of all these targets and put the costs there

        for port in self.port_to_link:
            endpoint_1 = self.port_to_link[port]
            endpoint_str = str(endpoint_1)

            the_cost = self.link_costs[endpoint_str]

            neighbors[endpoint_str] = {'Cost': the_cost}
        return neighbors # return the dictionary that holds costs to endpoints at index "endpoint"

    def contents(self):

        #form a packet consisting of last sequence number, source address, and neighbors
        content = {}
        content['src'] = self.addr
        content['neighbors'] = self.my_neighbors()
        content['seq_num'] = self.last_seqnum

        return content

    def broadcast(self):
        # get the packet that basically holds your linkstate and sequence number along with source
        packet_contents = self.contents()
        # increment sequence number
        self.last_seqnum = self.last_seqnum + 1

        #send it out to all your neighbors
        for link in self.new_links:
            # get which pot we sending to
            port_to_send = self.new_links[link]
            # get the address of the the port we sending to
            target_address = self.port_to_link[port_to_send]
            # send it out to the portnumber
            self.send(port_to_send, Packet("ROUTING", self.addr, target_address, dumps(packet_contents)))

    def handlePacket(self, port, packet):
        """TODO: process incoming packet"""
        if packet.isTraceroute():
            # Hints: this is a normal data packet
            # if the forwarding table contains packet.dstAddr
            #   send packet based on forwarding table, e.g., self.send(port, packet)
            dest_addr = packet.dstAddr
            #get the destination address and check if forwarding table has a port number at index 'dst_addr'
            if dest_addr in self.forwarding_table:
                #forward the packet to the port number
                self.send(self.forwarding_table[dest_addr], packet)
          
        else:
            # Hints: this is a routing packet generated by your routing protocol
            # get packet contents first 
            packet_contents = loads(packet.content)
            seq_num = packet_contents['seq_num']

            # get the source of the packet to check if we got a seq_num stored for this source 
            source_address = packet.srcAddr
            # check the sequence number

            if source_address not in self.sequence_numbers or seq_num > self.sequence_numbers[source_address]:
            # if the sequence number is higher and the received link state is different
               
                # update sequence numbers table
                self.sequence_numbers[source_address] = seq_num

                # get neighbors of this packet
                neighbors = packet_contents['neighbors']

                #   broadcast the packet to other neighbors
                # send the info ahead before updating my own data for this node
                for port in self.port_to_link:
                    # get the target destinations of all my neighbors that are directly linked
                    send_target = self.port_to_link[port]

                    #send the packet out to all these links 
                    self.send(port, Packet("ROUTING", source_address, send_target, packet.content))

                # if a linkstate for this node already existed then grab it, or initialize an empty dictionary for it
                if source_address not in self.link_states:
                    this_link_state = {}
                else:
                    this_link_state = self.link_states[source_address]
               
                # add edges for neighbors of this node to my view of the graph
                for nodes, costs in neighbors.items():
                    if nodes not in this_link_state:
                        self.G.add_edge(source_address, nodes, cost = costs['Cost'])

                # remove edges if they are in link state for this node but not listed as a neighbor in current packet
                for nodes, costs in this_link_state.items():
                    if nodes not in neighbors and self.G.has_edge(source_address, nodes):
                        self.G.remove_edge(source_address, nodes)

                # update the local copy of the link state
                self.link_states[source_address] = neighbors

                # update the forwarding table
                self.update_forwarding_table()
            pass

    #linkstate adjacency list to current node and costs
    #call for edges associated with self

    def handleNewLink(self, port, endpoint, cost):
        """TODO: handle new link"""
        # Hints:
        # update the forwarding table
        # broadcast the new link state of this router to all neighbors

        # update new links neighbors by placing the port number at the index
        # update the ports indexed array because remove links only give you a port number

        endpoint_string = str(endpoint) #so we can use it a key
        self.new_links[endpoint_string] = port
        self.port_to_link[port] = endpoint
        self.link_costs[endpoint_string] = cost

        # update current graph
        if not self.G.has_node(endpoint_string):
            #if the node didn't previously exist then add it
            self.G.add_node(endpoint_string)

        #add an edge to that node
        self.G.add_edge(self.addr, endpoint_string, cost = cost)

        # update forwarding table according to new graph
        self.update_forwarding_table()

        # update link state with new neighbors 
        self.link_states[self.addr] = self.contents()['neighbors']

        #broadcast to network
        self.broadcast()
        pass


    def handleRemoveLink(self, port):
        """TODO: handle removed link"""
        # Hints:
        # update the forwarding table
        # broadcast the new link state of this router to all neighbors

        # have to delete link given port number so remove endpoint at port tables index "port"
        # delete entry at newLinks "endpoint"

        endpt = self.port_to_link[port]
        endpt_str = str(endpt)
        del self.port_to_link[port]
        del self.new_links[endpt_str]
        del self.link_costs[endpt_str]

        # update graph by removing edge to that endpoint
        self.G.remove_edge(self.addr, endpt_str)

        # update forwarding table according to new information
        self.update_forwarding_table()

        # update link state with removed neighbors
        self.link_states[self.addr] = self.contents()['neighbors']

        # broadcast new info out to all routers
        self.broadcast()

        pass


    def handleTime(self, timeMillisecs):
        """TODO: handle current time"""
        if timeMillisecs - self.last_time >= self.heartbeatTime:
            self.last_time = timeMillisecs
            # Hints:
            # broadcast the link state of this router to all neighbors
            #self.broadcast()
            pass


    def debugString(self):
        """TODO: generate a string for debugging in network visualizer"""
        return ""
