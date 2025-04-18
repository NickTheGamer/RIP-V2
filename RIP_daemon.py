import sys
import time
import select
from socket import socket, AF_INET, SOCK_DGRAM

SOCKETS = []
PERIODIC_UPDATE_INTERVAL = 5       # seconds
ROUTE_TIMEOUT = 30                 # 6 × periodic
GARBAGE_COLLECTION_INTERVAL = 20   # 4 × periodic

class Router:
    
    def __init__(self, id, input_ports, output_ports):
        self.id = id
        self.input_ports = input_ports
        self.output_ports = output_ports
        self.routing_table = {}
        self.send_socket = socket(AF_INET, SOCK_DGRAM)
        self.check_constraints()
        self.instantiate_ports()
        self.convert_output_ports()
        self.initialise_routing_table()
        self.periodic_update_timer = time.time()
        self.route_timers = {}
        self.garbage_timers = {}

    def __str__(self):
        return f'Router ID: {self.id}\n' \
            f'Input Ports: {self.input_ports}\n' \
            f'Output Ports: {self.output_ports}\n'
    
    def display_routing_table(self):
        print('--------------------------------')
        print(f'Router: {self.id}')
        for entry in self.routing_table.keys():
            print(f'Destination: {entry} Cost: {self.routing_table[entry][0]}, Next hop: {self.routing_table[entry][1][0]} Is valid: {self.routing_table[entry][2]}')
        print('--------------------------------')

    def instantiate_ports(self):
        for port in self.input_ports:
            sock = socket(AF_INET, SOCK_DGRAM)
            sock.bind(('', port))
            SOCKETS.append(sock)

    def check_constraints(self):
        if self.id < 1 or self.id > 64000:
            raise Exception("Router-id must be between 1 and 64000 (inclusive).")
        for input in self.input_ports:
            if input < 1024 or input > 64000:
                raise Exception("Port numbers must be between 1024 and 64000 (inclusive).")
        for output in self.output_ports:
            output = output.split('-')
            port = int(output[0])
            if port < 1024 or port > 64000:
                raise Exception("Port numbers must be between 1024 and 64000 (inclusive).")

    def convert_output_ports(self):
        self.output_ports = [tuple(map(int, output.split('-'))) for output in self.output_ports]

    def initialise_routing_table(self):
        # Add the router itself to the routing table with a cost of 0
        self.routing_table[self.id] = (0, (self.id, None), True)

        # Add neighbors from the output ports to the routing table
        for output in self.output_ports:
            neighbor_id = output[2]
            cost = output[1]
            self.routing_table[neighbor_id] = (cost, (neighbor_id, output[0]), True)

    def construct_packet(self, neighbour_id):
        packet = bytearray()

        packet.append(2) #COMMAND: reponse
        packet.append(2) #Version: 2
        packet += self.id.to_bytes(2, 'big') #Router-ID in place of zero-byte field

        for entry in self.routing_table.keys():
            dest_id = entry
            cost, (next_hop, _), is_valid = self.routing_table[entry]

            if next_hop == neighbour_id or not is_valid: #split-horizon with poison reverse
                cost = 16

            packet += (2).to_bytes(2, 'big') #address family identifier (AF_INET)
            packet += (0).to_bytes(2, 'big') #Route tag (set to 0)
            packet += dest_id.to_bytes(4, 'big')
            packet += bytes(4) #Subnet mask not used
            packet += next_hop.to_bytes(4, 'big')
            packet += cost.to_bytes(4, 'big')

        return packet

    def decode_packet(self, packet):
        if packet[0] != 2: #Check Command field
            print('Invalid packet header, Command incorrect. Packet dropped')
            return
        if packet[1] != 2: #Check version field
            print('Invalid packet header, version is not 2. Packet dropped')
            return
        
        sender_id = int.from_bytes(packet[2:4], 'big') #Check sender ID constraints
        if sender_id < 1 or sender_id > 64000:
            print("Invalid Router ID. Packet dropped.")
            return
        else: #Check sender is actually neighbour (in output ports)
            valid_id = False
            for output in self.output_ports:
                if output[2] == sender_id:
                    valid_id = True
        if not valid_id:
            print('Router is not a neighbour. Packet dropped.')
            return
        
        index = 4 #Now we iterate over the rest of the packet to extract RIP entries
        routes = []
        while index < len(packet):
            if int.from_bytes(packet[index:index+2], 'big') != 2:
                print("Invalid RIPv2 entry with incorrect Addr Family. Packet dropped.")
                return
            index += 2

            if int.from_bytes(packet[index:index+2], 'big') != 0:
                print("Invalid RIPv2 entry with Route Tag. Packet dropped.")
                return
            index += 2

            dest_id = int.from_bytes(packet[index:index+4], 'big')
            if dest_id < 1 or dest_id > 64000:
                print('Invalid RIPv2 entry with invalid Destination ID. Packet dropped.')
                return
            index += 4

            if int.from_bytes(packet[index:index+4], 'big') != 0:
                print('Invalid RIPv2 entry, Subnet mask should be 0. Packet dropped.')
                return
            index += 4

            next_hop = int.from_bytes(packet[index:index+4], 'big')
            if next_hop < 1 or next_hop > 64000:
                print('Invalid RIPv2 entry with invalid next hop. Packet dropped.')
                return
            index += 4

            cost = int.from_bytes(packet[index:index+4], 'big')
            if cost < 1 or cost > 16:
                print('Invalid RIPv2 entry with invalid cost. Packet dropped.')
                return
            index += 4

            routes.append((sender_id, dest_id, cost))

        self.calculate_routes(routes) #Update the routing table with the new routes

    def send_packets(self):
        for output in self.output_ports:
            neighbour_port = output[0]
            neighbour_id = output[2]

            if neighbour_id not in self.routing_table: #If the neighbour is not in the routing table, we don't send a packet
                continue
            if self.routing_table[neighbour_id][2] == False: #If the route is invalid, we don't send a packet
                continue
            
            packet = self.construct_packet(neighbour_id)
            self.send_socket.sendto(packet, ('localhost', neighbour_port))
            print(f"Packet sent to router {neighbour_id} on port {neighbour_port}")

    def update_timers(self):
        if time.time() - ROUTER.periodic_update_timer >= PERIODIC_UPDATE_INTERVAL: #Periodic updates
            self.send_packets()
            ROUTER.periodic_update_timer = time.time()

        for entry in self.routing_table.keys(): #Update the route timers
            if entry not in ROUTER.route_timers:
                ROUTER.route_timers[entry] = time.time()
            else:
                if self.routing_table[entry][2] == True: #Only need to consider valid routes
                    if time.time() - ROUTER.route_timers[entry] >= ROUTE_TIMEOUT:
                        print(f"Route to {entry} has timed out.")
                        self.routing_table[entry] = (16, self.routing_table[entry][1], False) #Set the route to invalid
                        ROUTER.garbage_timers[entry] = time.time() #Add garbage timer
        
        for entry in list(ROUTER.garbage_timers.keys()): #Update the garbage collection timers and delete the routes if necessary
            if time.time() - ROUTER.garbage_timers[entry] >= GARBAGE_COLLECTION_INTERVAL:
                print(f"Route to {entry} has been garbage collected.")
                del ROUTER.route_timers[entry]
                del self.routing_table[entry]
                del  ROUTER.garbage_timers[entry]

    def calculate_routes(self, routes):
        """
        Updates the routing table based on the received routes using the Distance Vector Routing Algorithm.
        """
        # Keep track of routes that are still being advertised
        advertised_routes = set()

        for sender_id, dest_id, cost in routes:
            print(f"Processing route: sender={sender_id}, dest={dest_id}, cost={cost}")

            # Ensure the sender exists in the routing table
            if sender_id not in self.routing_table:
                print(f"Sender {sender_id} not in routing table. Skipping.")
                continue

            # Calculate the new cost to the destination via the sender
            new_cost = cost + self.routing_table[sender_id][0]
            print(f"New cost to {dest_id} via {sender_id}: {new_cost}")

            # Skip routes with invalid costs
            if new_cost > 16:
                print(f"Cost to {dest_id} exceeds 16. Skipping.")
                continue

            # Update the route if the new cost is lower or the next hop is the sender
            if dest_id not in self.routing_table or new_cost < self.routing_table[dest_id][0]:
                self.routing_table[dest_id] = (new_cost, sender_id, True)
                print(f"Updated routing table entry for {dest_id}: {self.routing_table[dest_id]}")

            # Mark the route as advertised
            advertised_routes.add(dest_id)

        # Invalidate routes that are no longer advertised
        for dest_id in list(self.routing_table.keys()):
            if dest_id not in advertised_routes and dest_id != self.id:
                print(f"Route to {dest_id} is no longer advertised. Marking as unreachable.")
                self.routing_table[dest_id] = (16, None, False)


def read_config_file(filename):
    #Reads a config file for a single router and returns a dictionary with the configuration.

    with open(filename, 'r') as file, open(filename, 'r') as file:
        lines = [line.strip() for line in file if line.strip()]

    if len(lines) != 3:
        raise Exception(f"Config file '{filename}' must contain exactly 3 non-empty lines.")

    config = {}

    #router-id
    parts = lines[0].split()
    if parts[0].lower() != 'router-id' or len(parts) != 2:
        raise Exception(f"Line 1 in '{filename}' must be: router-id <id>")
    try:
        config['router-id'] = int(parts[1])
        if config['router-id'] < 1 or config['router-id'] > 64000:
            raise ValueError("Router ID must be between 1 and 64000 (inclusive).")
    except ValueError:
        raise ValueError("Router ID must be an integer.")

    #input-ports
    parts = lines[1].split()
    if parts[0].lower() != 'input-ports' or len(parts) < 2:
        raise Exception(f"Line 2 in '{filename}' must be: input-ports <port1> <port2> ...")
    try:
        config['input-ports'] = list(map(int, parts[1:]))
        for port in config['input-ports']:
            if port < 1024 or port > 64000:
                raise ValueError("Port numbers must be between 1024 and 64000 (inclusive).")
    except ValueError:
        raise ValueError("Input ports must be integers.")

    #output-ports
    parts = lines[2].split()
    if parts[0].lower() != 'output-ports' or len(parts) < 2:
        raise ValueError(f"Line 3 in '{filename}' must be: output-ports <port-cost-id> ...")
    config['output-ports'] = parts[1:]
    for output in config['output-ports']:
        parts = output.split('-')
        if len(parts) != 3:
            raise Exception("Output ports must be in the format <port-cost-id>.")
        try:
            port = int(parts[0])
            cost = int(parts[1])
            id = int(parts[2])
            if port < 1024 or port > 64000:
                raise ValueError("Port numbers must be between 1024 and 64000 (inclusive).")
            if cost < 1 or cost > 16:
                raise ValueError("Cost must be between 1 and 16 (inclusive).")
            if id < 1 or id > 64000:
                raise ValueError("Router ID must be between 1 and 64000 (inclusive).")
        except ValueError:
            raise ValueError("Output ports must be integers.")

    return config


def routing_loop():
    ROUTER.send_packets()
    
    while True:
        readable, _, _ = select.select(SOCKETS, [], [], 1)

        if readable:
            for sock in readable:
                try:
                    data, _ = sock.recvfrom(1024)
                    ROUTER.decode_packet(data)
                except Exception as e:
                    print(f"Error receiving from socket: {e}")
        
        #Always check timers
        ROUTER.update_timers()


def main():
    if len(sys.argv) != 2:
        sys.exit(1)

    config_file = sys.argv[1]
    config = read_config_file(config_file)

    router_id = config.get('router-id')
    input_ports = config.get('input-ports', [])
    output_ports = config.get('output-ports', [])

    global ROUTER
    ROUTER = Router(router_id, input_ports, output_ports)

    print(ROUTER)
    ROUTER.display_routing_table()

    routing_loop()


if __name__ == "__main__":
    main()
