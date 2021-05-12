# Intra-Domain-Routing

Link-State Routing
- Each router keeps its own link state and other nodes' link states it receives. The link state of a router contains the links and their weights between the router and its neighbors.
- When a router receives a link state from its neighbor, it updates the stored link state and the forwarding table. Then it broadcasts the link state to other neighbors.
- Each router broadcast its own link state to all neighbors when the link state changes. The broadcast is also done periodically if no detected change has occurred.
- A sequence number is added to each link state message to distinguish between old and new link state messages. Each router stores the sequence number together with the link state. If a router receives a link state message with a smaller sequence number (i.e., an old link state message), the link state message is simple disregarded.

# Method descriptions

These are the methods you need to complete in DVrouter and LSrouter: - __init__(self, addr, heartbeatTime)
Packet
o Class constructor. addr is the address of this router. Add your own class fields and initialization code (e.g., to create forwarding table data structures). Routing information should be sent by this router at least once every heartbeatTime milliseconds.
- handlePacket(self, port, packet)
o Process incoming packet: This method is called whenever a packet arrives at the
router on port number port. You should check whether the packet is a traceroute packet or a routing packet and handle it appropriately. Methods and fields of the packet class are defined in packet.py.
- handleNewLink(self, port, endpoint, cost)
o This method is called whenever a new link is added to the router on port number
port connecting to a router or client with address endpoint and link cost cost. You should store the argument values in a data structure to use for routing. If you want to send packets along this link, call self.send(port, packet).
- handleRemoveLink(self, port)
o Thismethodiscalledwhentheexistinglinkonportnumberportisdisconnected.
You should update data structures appropriately.
- handleTime(self, timeMillisecs)
o This method is called regularly and provides you with the current time in milliseconds for sending routing packets at regular intervals.
- debugString(self)
o This method is called by the network visualization to print current details about the router. It should return any string that will be helpful for debugging. This method is for your own use and will not be graded.

Code of Focus: LSrouter.py
